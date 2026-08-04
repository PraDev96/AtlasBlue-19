# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = "project.project"

    subscription_ids = fields.One2many('sale.order', 'project_id', string="Subscriptions", domain="[('is_subscription', '=', True)]")
    subscription_count = fields.Integer(string="#Total Subscription", compute='_compute_subscription', tracking=True)

    total_service_so_amount = fields.Float(compute="_compute_total_service_sale", string="Service Sale Amount")

    @api.depends('subscription_ids', 'subscription_ids.state', 'subscription_ids.amount_total', 'subscription_ids.is_subscription', 'subscription_ids.date_order')
    def _compute_total_service_sale(self):
        for project in self:
            subscriptions = project.subscription_ids.filtered(lambda sale: sale.is_subscription and sale.state in ('sale', 'done')).sorted(key='date_order', reverse=True)
            project.total_service_so_amount = subscriptions[0].amount_total if subscriptions else 0.0

    def _compute_subscription(self):
        for record in self:
            record.subscription_count = len(record.subscription_ids.ids)

    def action_view_sale_subscription(self):
        action = self.env.ref('sale_subscription.sale_subscription_action').sudo().read()[0]
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {
            'default_project_id': self.id,
            'default_is_subscription': True,
            'default_company_id': self.company_id.id,
            "default_partner_id": self.partner_id.id,
        }

        return action

# -*- coding: utf-8 -*-

from markupsafe import Markup
from odoo import models, fields, _, api


class CrmStages(models.Model):
    _inherit = "crm.stage"

    code = fields.Char(string="Code")


class Team(models.Model):
    _inherit = "crm.lead"

    ticket_id = fields.Many2one("helpdesk.ticket", string="Ticket", tracking=True)
    ticket_ids = fields.One2many("helpdesk.ticket", "lead_id", string="Tickets", tracking=True)
    detail = fields.Text(string="Details", tracking=True)
    lead_through = fields.Selection([('internal', 'Internal'), ('external_party', 'External Party')], string="Lead Through", tracking=True)
    third_party_id = fields.Many2one("res.partner", string="Third party name", tracking=True)
    commission = fields.Float(string="Commission (%)", tracking=True)
    number_of_days_per_week = fields.Integer(string="Number Of Visits Per Week", tracking=True)
    day_ids = fields.Many2many('week.days', string="Days Of Visit", tracking=True)
    hr_employee_id = fields.Many2one("hr.employee", string="Employee")
    partner_id = fields.Many2one("res.partner", string="Contacts")

    def update_ticket(self, vals):
        if not vals.get('ticket_id'):
            return

        stage = self.env['helpdesk.stage'].search([('code', '=', 'CLOSE')], limit=1)
        if stage:
            for rec in self.filtered('ticket_id'):
                message_body = Markup("Lead <strong>%(display_name)s</strong> has been generated from this ticket.") % {'display_name': rec.display_name}
                rec.ticket_id.message_post(body=message_body)
                if stage:
                    rec.ticket_id.stage_id = stage.id
                else:
                    rec.ticket_id.message_post(body="Ticket should goto close stage. (Stage with code 'CLOSE' not found)")

    @api.model_create_multi
    def create(self, vals_list):
        record = super().create(vals_list)
        for vals in vals_list:
            record.update_ticket(vals)

        return record

    def write(self, vals):
        res = super().write(vals)
        self.update_ticket(vals)
        return res

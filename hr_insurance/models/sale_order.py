# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    insurance_count = fields.Integer(string="Insurance Count", compute='_compute_insurance')
    insurance_ids = fields.One2many('hr.insurance', 'sale_order_id', string="Insurance")

    def _compute_insurance(self):
        Insurance = self.env['hr.insurance']
        for rec in self:
            insurances = Insurance.search([('sale_order_id', '=', rec.id)])
            rec.insurance_count = len(insurances)

    def action_insurance(self):
        self.ensure_one()
        action = self.env.ref('hr_insurance.action_hr_insurance_sales').sudo().read()[0]
        action['domain'] = [('sale_order_id', '=', self.id)]
        action['context'] = {
            'default_insurance_type': 'sales',
            'default_sale_order_id': self.id,
            'default_motor_vehicle_id': self.vehicle_id.id,
        }

        return action

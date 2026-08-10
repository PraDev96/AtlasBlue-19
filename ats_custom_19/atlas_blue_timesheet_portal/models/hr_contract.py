# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Contract(models.Model):
    _inherit = "hr.contract"

    per_hour_wage = fields.Float(string="Per Hour Wage", compute="compute_per_hour_wage", store=True)

    @api.depends('total_salary')
    def compute_per_hour_wage(self):
        for contract in self:
            contract.per_hour_wage = (contract.total_salary / 26 / 8) or 0

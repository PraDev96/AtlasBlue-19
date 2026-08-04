# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    is_insurance_company = fields.Boolean(string="Is Insurance Company")

    @api.onchange('is_insurance_company')
    def _onchange_is_insurance_company(self):
        if not self.is_insurance_company:
            self.parent_id = False

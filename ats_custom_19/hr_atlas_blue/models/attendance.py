# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    project_id = fields.Many2one('project.project', string="Project")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('employee_id') and vals.get('check_in'):
                check_in = fields.Datetime.from_string(vals['check_in']).strftime("%Y-%m-%d")
                historyemployee = self.env['history.project.employee'].sudo().search([
                    ('employee_id', '=', vals['employee_id']), ('start_date', '<=', check_in), '|', ('end_date', '>=', check_in), ('end_date', '=', False)
                ])
                if historyemployee:
                    vals['project_id'] = historyemployee.project_id.id

        return super(HrAttendance, self).create(vals_list)

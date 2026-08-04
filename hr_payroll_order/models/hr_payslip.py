# -*- coding: utf-8 -*-

from odoo import models, fields


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    company_id = fields.Many2one(readonly=False)
    department_id = fields.Many2one('hr.department', string="Department")
    category_id = fields.Many2one('hr.employee.category', string="Employee Tags")

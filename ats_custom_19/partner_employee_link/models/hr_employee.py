# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    partner_id = fields.Many2one('res.partner', string="Partner")

    @api.model_create_multi
    def create(self, vals_list):
        employees = super(Employee, self).create(vals_list)
        for employee in employees:
            if employee.work_contact_id:
                employee.partner_id = employee.work_contact_id
        return employees


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    partner_id = fields.Many2one('res.partner', string="Partner")

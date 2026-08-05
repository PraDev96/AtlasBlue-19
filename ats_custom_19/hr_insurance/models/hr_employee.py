# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class EmployeeContractType(models.Model):
    _name = 'employee.contract.type'
    _description = "Contract Type"

    name = fields.Char(string="Name", required=True)


class HiringType(models.Model):
    _name = 'hiring.type'
    _description = "Hiring Type"

    name = fields.Char('Name', required=True)


class Employee(models.Model):
    _inherit = 'hr.employee'

    cotract_type_id = fields.Many2one('employee.contract.type', string="Contract Type")
    hiring_type_id = fields.Many2one('hiring.type', string="Hiring Type")
    departure_date = fields.Date(string="Departure Date")
    resume_work_date = fields.Date(string="Resume Work Date")
    is_suspended = fields.Boolean(string="Is Suspended?")

    insurance_ids = fields.One2many('hr.insurance', 'employee_id', string="Insurance")
    insurance_count = fields.Integer(string="Insurance Count", compute='_compute_employee_insurance')

    def _compute_employee_insurance(self):
        Insurance = self.env['hr.insurance']
        for rec in self:
            insurances = Insurance.search([('employee_id', '=', rec.id)])
            rec.insurance_count = len(insurances)

    def action_hr_employee_insurance(self):
        self.ensure_one()
        action = self.env.ref('hr_insurance.action_hr_insurance').sudo().read()[0]
        action['domain'] = [('employee_id', '=', self.id), ('insurance_type', '=', 'employee')]
        action['context'] = {
            'default_employee_id': self.id,
            'default_insurance_type': 'employee'
        }

        return action

    def action_suspend(self):
        dt = fields.Date.today()
        for employee in self:
            if not employee.departure_date:
                raise ValidationError(_("Employee does not have Departure Date!"))

            # employee.contract_id.write({'state': 'suspend'})
            dt = fields.Date.today()
            contract = employee._get_contracts(dt, dt)
            contract.write({'state': 'suspend'})
            employee.write({'is_suspended': True, 'active': False})

    def action_resume(self):
        for rec in self:
            if not rec.resume_work_date:
                raise ValidationError(_("Employee does not have Resume Work Date!"))

            rec.write({'is_suspended': True, 'active': True})


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    cotract_type_id = fields.Many2one('employee.contract.type', string="Contract Type")
    hiring_type_id = fields.Many2one('hiring.type', string="Hiring Type")
    departure_date = fields.Date(string="Departure Date")
    resume_work_date = fields.Date(string="Resume Work Date")
    is_suspended = fields.Boolean(string="Is Suspended?")

# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    emp_driver_id = fields.Many2one('hr.employee', string="Driver Employee", store=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    phone = fields.Char(related='emp_driver_id.work_phone', store=True)
    mobile = fields.Char(related='emp_driver_id.mobile_phone', store=True)
    work_location = fields.Char(related='emp_driver_id.work_location_id.name', store=True)

    future_emp_driver_id = fields.Many2one('hr.employee', string="Future Driver Employee", copy=False, check_company=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('emp_driver_id'):
                driver_employee = self.env['hr.employee'].sudo().browse(vals.get('emp_driver_id'))
                vals['driver_id'] = driver_employee.work_contact_id.id if driver_employee and driver_employee.work_contact_id else False
                vals['driver_employee_id'] = vals.get('emp_driver_id')

            if vals.get('future_emp_driver_id'):
                future_driver_employee = self.env['hr.employee'].sudo().browse(vals.get('future_emp_driver_id'))
                vals['future_driver_id'] = future_driver_employee.work_contact_id.id if future_driver_employee and future_driver_employee.work_contact_id else False
                vals['future_driver_employee_id'] = vals.get('future_emp_driver_id')

        return super(FleetVehicle, self).create(vals_list)

    def write(self, vals):
        if 'emp_driver_id' in vals and vals.get('emp_driver_id'):
            driver_employee = self.env['hr.employee'].sudo().browse(vals.get('emp_driver_id'))
            vals['driver_id'] = driver_employee.work_contact_id.id if driver_employee and driver_employee.work_contact_id else False
            vals['driver_employee_id'] = vals.get('emp_driver_id')

        if vals.get('future_emp_driver_id'):
            future_driver_employee = self.env['hr.employee'].sudo().browse(vals.get('future_emp_driver_id'))
            vals['future_driver_id'] = future_driver_employee.work_contact_id.id if future_driver_employee and future_driver_employee.work_contact_id else False
            vals['future_driver_employee_id'] = vals.get('future_emp_driver_id')

        return super(FleetVehicle, self).write(vals)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    plan_to_change_car = fields.Boolean('Plan To Change Car', default=False)


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    plan_to_change_car = fields.Boolean('Plan To Change Car', default=False)

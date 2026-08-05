# -*- coding: utf-8 -*-

from odoo import models, fields


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    is_auto_approve = fields.Boolean(string="Is Auto Approve ?")


class HolidaysAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    def create_auto_type_leave_allocation(self):
        LeaveType = self.env['hr.leave.type']
        Employee = self.env['hr.employee']
        employees = Employee.search([('contract_id.leave_allocation', '>', 0.0)])
        leave_types = LeaveType.search([('is_auto_allocate', '=', True)])
        today = fields.Date.today()
        for employee in employees:
            for leave_type in leave_types.filtered(lambda l: l.company_id == employee.company_id or not l.company_id):
                if leave_type.auto_allocation_date:
                    month_allocation = leave_type.auto_allocation_date.strftime('%m')
                    year_allocation = leave_type.auto_allocation_date.strftime('%Y')
                    today_month_allocation = today.strftime('%m')
                    today_year_allocation = today.strftime('%Y')

                    if int(month_allocation) >= int(today_month_allocation) and int(year_allocation) >= int(today_year_allocation):
                        continue

                if employee.company_id == leave_type.company_id and employee.contract_id and employee.contract_id.leave_allocation > 0.0:
                    allocation_leave = self.create({
                        'name': leave_type.name + ' - ' + today.strftime('%B'),
                        'holiday_type': 'employee',
                        'employee_id': employee.id,
                        'holiday_status_id': leave_type.id,
                        'allocation_type': 'regular',
                        'number_of_days': employee.contract_id.leave_allocation,
                        'is_auto_generate': True,
                        'mode_company_id': employee.company_id.id,
                    })
                    if leave_type.is_auto_approve and allocation_leave.state == 'confirm':
                        allocation_leave.action_validate()

        for leave_type in leave_types.filtered(lambda l: l.company_id == employee.company_id or not l.company_id):
            leave_type.write({'auto_allocation_date': today})

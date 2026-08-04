# -*- coding:utf-8 -*-

import logging
from odoo import models, fields
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta


class LeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    def create_missing_allocation(self):
        LeaveType = self.env['hr.leave.type']
        Employee = self.env['hr.employee']
        leave_allocations = self.env['hr.leave.allocation']

        employees = Employee.search([('contract_id.leave_allocation', '>', 0), ('contract_id', '!=', False), ('date_joining', '!=', False)])
        logging.info("__ Leave Auto Allocation Check Employees : %s" % (employees))
        leave_type = LeaveType.search([('is_auto_allocate', '=', True)], limit=1)
        for employee in employees:
            emp_join_date = employee.date_joining
            today = fields.Date.today()
            diff_months = list(rrule(MONTHLY, dtstart=emp_join_date, until=today))
            logging.info("____ Today to Joining : %s - %s - %s = %s (%s)" % (employee, today, emp_join_date, len(diff_months), diff_months))
            for dt_by_month in diff_months:
                start_month = dt_by_month.replace(day=1)
                next_start_month = dt_by_month.replace(day=1) + relativedelta(months=1)
                leave_allocation = leave_allocations.search([
                    ('employee_id', '=', employee.id),
                    ('date_from', '>=', start_month),
                    ('date_from', '<=', next_start_month),
                    ('date_to', '=', False)])
                logging.info("______ Already allocated : %s - %s - %s" % (leave_allocation, dt_by_month, employee))
                if not leave_allocation:
                    new_alloc = self.create({
                        'name': leave_type.name + ' - ' + start_month.strftime('%B'),
                        'holiday_type': 'employee',
                        'employee_id': employee.id,
                        'holiday_status_id': leave_type.id,
                        'allocation_type': 'regular',
                        'number_of_days': employee.contract_id.leave_allocation,
                        'is_auto_generate': True,
                        'mode_company_id': employee.company_id.id,
                        'date_from': start_month,
                    })
                    logging.info("________ Allocation Created : %s - %s - %s" % (new_alloc, dt_by_month, employee))
                    new_alloc.action_validate()

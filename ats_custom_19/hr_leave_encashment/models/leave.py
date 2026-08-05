# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models, fields, _, api, tools


class LeaveType(models.Model):
    _inherit = 'hr.leave.type'

    allow_encashment = fields.Boolean(string="Allow Leave Encasement")

    @api.constrains('allow_encashment', 'allocation_validation_type')
    def _check_allocation_encash(self):
        for rec in self:
            if rec.allow_encashment and rec.allocation_validation_type == 'no':
                raise UserError(_('Encasement allowed only for Allocatable Leave Mode.'))


class LeaveReport(models.Model):
    _inherit = "hr.leave.report"

    leave_type = fields.Selection(selection_add=[('encash', 'Encashed')])
    # payslip_state = fields.Boolean(string="Reported in last payslips", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'hr_leave_report')

        self._cr.execute("""
            CREATE or REPLACE view hr_leave_report as (
                SELECT row_number() over(ORDER BY leaves.employee_id) as id,
                leaves.leave_id as leave_id,
                leaves.employee_id as employee_id, leaves.name as name,
                leaves.number_of_days as number_of_days, leaves.leave_type as leave_type,
                leaves.category_id as category_id, leaves.department_id as department_id,
                leaves.holiday_status_id as holiday_status_id, leaves.state as state,
                leaves.holiday_type as holiday_type, leaves.date_from as date_from,
                leaves.date_to as date_to, leaves.company_id
                from (select
                    allocation.id as leave_id,
                    allocation.employee_id as employee_id,
                    allocation.private_name as name,
                    allocation.number_of_days as number_of_days,
                    allocation.category_id as category_id,
                    allocation.department_id as department_id,
                    allocation.holiday_status_id as holiday_status_id,
                    allocation.state as state,
                    allocation.holiday_type,
                    allocation.date_from as date_from,
                    allocation.date_to as date_to,
                    'allocation' as leave_type,
                    allocation.employee_company_id as company_id
                from hr_leave_allocation as allocation
                inner join hr_employee as employee on (allocation.employee_id = employee.id)
                where employee.active IS True AND
                allocation.active IS True

                union all select
                    request.id as leave_id,
                    request.employee_id as employee_id,
                    request.private_name as name,
                    (request.number_of_days * -1) as number_of_days,
                    request.category_id as category_id,
                    request.department_id as department_id,
                    request.holiday_status_id as holiday_status_id,
                    request.state as state,
                    request.holiday_type,
                    request.date_from as date_from,
                    request.date_to as date_to,
                    'request' as leave_type,
                    request.employee_company_id as company_id
                from hr_leave as request

                union all select
                    encash.holiday_id as leave_id,
                    encash.employee_id as employee_id,
                    encash.name as name,
                    (encash.payable_leave_count * -1) as number_of_days,
                    null as category_id,
                    encash.department_id as department_id,
                    encash.holiday_status_id,
                    CASE
                        WHEN encash.state = 'paid' THEN 'validate'
                        ELSE encash.state
                    END AS state,
                    'employee' AS holiday_type,
                    null as date_from,
                    encash.date_payslip as date_to,
                    -- FALSE as payslip_status,
                    'encash' as leave_type,
                    encash.company_id as company_id
                from emp_leave_encashment as encash) leaves
            );
        """)


class Leave(models.Model):
    _inherit = 'hr.leave'

    already_encashed = fields.Boolean(string="Already Encased", readonly=True)
    # payslip_state = fields.Boolean(string="Reported in last payslips", readonly=True, copy=False)

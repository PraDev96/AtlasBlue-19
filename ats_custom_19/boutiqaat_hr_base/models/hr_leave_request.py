# -*- coding: utf-8 -*-

from odoo import _
from collections import defaultdict
from odoo.exceptions import ValidationError
from odoo.addons.hr_holidays.models.hr_leave import HolidaysRequest as LeaveRequest


def _check_validity(self):
    """
        Overwrite this method from the base to bypass the future allocation issue.
        source: hr_holidays/models/hr_leave.py  ---- line 785
    """
    sorted_leaves = defaultdict(lambda: self.env['hr.leave'])
    for leave in self:
        sorted_leaves[(leave.holiday_status_id, leave.date_from.date())] |= leave
    for (leave_type, date_from), leaves in sorted_leaves.items():
        if leave_type.requires_allocation == 'no':
            continue

        employees = self.env['hr.employee']
        for leave in leaves:
            employees |= leave._get_employees_from_holiday_type()
        leave_data = leave_type.get_allocation_data(employees, date_from)
        if leave_type.allows_negative:
            max_excess = leave_type.max_allowed_negative
            for employee in employees:
                if not leave_data[employee]:
                    raise ValidationError(_("You do not have any allocation for this time off type.\n Please request an allocation before submitting your time off request."))

                if leave_data[employee] and leave_data[employee][0][1]['virtual_remaining_leaves'] < -max_excess:
                    raise ValidationError(_("%(name)s does not have a valid allocation for the leave type %(leave_type)s to cover that request - 1.", name=employee.name,
                                            leave_type=leave_type.name))
            continue

        previous_leave_data = leave_type.with_context(ignored_leave_ids=leaves.ids).get_allocation_data(employees, date_from)
        for employee in employees:
            previous_emp_data = previous_leave_data[employee] and previous_leave_data[employee][0][1]['virtual_excess_data']
            emp_data = leave_data[employee] and leave_data[employee][0][1]['virtual_excess_data']

            if not leave_data[employee]:
                raise ValidationError(_("You do not have any allocation for this time off type.\n Please request an allocation before submitting your time off request."))

            if not previous_emp_data and not emp_data:
                continue

            # The below commented is to fix the leave in future months, and it is an udaipp
            # if previous_emp_data != emp_data and len(emp_data) >= len(previous_emp_data):
            #     raise ValidationError(_("%(name)s does not have a valid allocation for the leave type %(leave_type)s to cover that request - 2.", name=employee.name,
            #                             leave_type=leave_type.name))


LeaveRequest._check_validity = _check_validity

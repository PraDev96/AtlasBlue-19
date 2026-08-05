# -*- coding: utf-8 -*-

from odoo import models, fields


class Employee(models.Model):
    _inherit = 'hr.employee'

    encashment_ids = fields.One2many("emp.leave.encashment", "employee_id", string="Leave Encasement")
    leave_encashed = fields.Float(string="Leave Encashed", compute="_compute_leave_encashed")

    def _compute_leave_encashed(self):
        # Encashment = self.env['emp.leave.encashment']
        for emp in self:
            encashments = emp.encashment_ids.filtered(lambda r: r.state in ('confirm', 'paid'))
            print('___ encashments : ', encashments)
            emp.leave_encashed = sum(encashments.mapped('payable_leave_count'))

    def _get_encashment_remaining_leaves(self, holiday_status_id):
        """
            Helper to compute the remaining leaves for the current employees
            :returns dict where the key is the employee id, and the value is the remain leaves
        """
        self._cr.execute("""
            SELECT
                sum(h.number_of_days) AS days, h.employee_id
            FROM
                (
                    SELECT holiday_status_id, number_of_days, state, employee_id
                    FROM hr_leave_allocation
                    UNION ALL
                    SELECT holiday_status_id, (number_of_days * -1) as number_of_days, state, employee_id
                    FROM hr_leave
                ) h
                join hr_leave_type s ON (s.id=h.holiday_status_id)
            WHERE
                s.active = true AND h.state='validate' AND
                (s.allocation_type='fixed' OR s.allocation_type='fixed_allocation') AND
                s.allow_encashment = true AND
                h.employee_id in %s AND
                h.holiday_status_id = %s
            GROUP BY h.employee_id
        """, (tuple(self.mapped('').ids), holiday_status_id))

        return dict((row['employee_id'], row['days']) for row in self._cr.dictfetchall())

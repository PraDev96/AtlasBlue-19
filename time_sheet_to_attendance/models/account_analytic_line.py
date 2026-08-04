# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo.addons.resource.models.utils import make_aware


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    attendance_id = fields.Many2one('hr.attendance', string="Attendance", readonly=True)

    def create_attendance(self):
        attendance = self.attendance_id
        if attendance:
            # Replace current check-out
            checkout = attendance.check_in
            checkout = checkout + timedelta(hours=self.unit_amount)
            attendance.write({'check_out': fields.Datetime.to_string(checkout)})
        else:
            Attendance = self.env['hr.attendance']
            domain = [
                ('employee_id', '=', self.employee_id.id), ('check_in', '>=', "%s %s" % (str(self.date), "00:00:00")),
                "|", ('check_out', '<=', "%s %s" % (str(self.date), "23:59:59")), ('check_out', "=", False),
            ]
            attendance = Attendance.search(domain, limit=1)

            # Find existing attendance
            if attendance:
                # Checkout + Worked Hours
                checkout = attendance.check_out or attendance.check_in
                checkout = checkout + timedelta(hours=self.unit_amount)
                attendance.write({'check_out': fields.Datetime.to_string(checkout)})
                self.write({'attendance_id': attendance.id})
            else:
                # Create New Attendance from Working Schedule Start Time
                dt0 = datetime.combine(self.date, time.min)
                dt0 = make_aware(dt0)[0]

                start_dtime = self.employee_id.resource_id.calendar_id._get_closest_work_time(dt0)
                attendance = Attendance.create({
                    'employee_id': self.employee_id.id,
                    'check_in': fields.Datetime.to_string(start_dtime),
                    'check_out': fields.Datetime.to_string(start_dtime + relativedelta(hours=self.unit_amount)),
                })
                self.write({'attendance_id': attendance.id})

# -*- coding: utf-8 -*-

from pytz import timezone, UTC
from odoo import models, fields
from dateutil.relativedelta import relativedelta


def to_naive_user_tz(datetime, tz_name):
    tz = tz_name and timezone(tz_name) or UTC
    return UTC.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(tz).replace(tzinfo=None)


def to_naive_utc(datetime, tz_name='Asia/Kolkata'):
    tz = tz_name and timezone(tz_name) or UTC
    return tz.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(UTC).replace(tzinfo=None)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    from_date = fields.Datetime(string="From Date", copy=False)
    to_date = fields.Datetime(string="To Date", copy=False)
    is_started = fields.Boolean(string="Is Start?")
    is_finished = fields.Boolean(string="Is Finished?")
    is_attendance = fields.Boolean(string="Is Attendance?")
    restaurant_id = fields.Many2one('fleet.restaurant', string="Restaurant")

    def action_start(self):
        self.ensure_one()
        self.write({
            'from_date': fields.Datetime.now(),
            'is_started': True
        })

    def action_end(self):
        self.ensure_one()
        duration = (fields.Datetime.now() - self.from_date).total_seconds() / 3600
        self.write({
            'to_date': fields.Datetime.now(),
            'unit_amount': round(duration, 2),
            'is_finished': True
        })

    def action_transfer_atten(self):
        self.ensure_one()
        HrAttendance = self.env['hr.attendance']

        start_date = self.date.strftime('%Y-%m-%d') + ' 00:00:00'
        end_date = self.date.strftime('%Y-%m-%d') + ' 23:59:59'
        check_in = fields.Datetime.from_string(start_date)
        check_out = fields.Datetime.from_string(end_date)

        tz_name = self.env.user.tz or 'UTC'
        naive_in = to_naive_utc(check_in, tz_name)
        naive_out = to_naive_utc(check_out, tz_name)

        attendance = HrAttendance.search([('check_in', '>=', naive_in), ('check_in', '<=', naive_out), ('employee_id', '=', self.employee_id.id), ], limit=1)
        if attendance:
            vals = {'check_out': attendance.check_out + relativedelta(hours=self.unit_amount)}
            attendance.write(vals)
        else:
            check_in = fields.Datetime.from_string(start_date)
            check_out = check_in + relativedelta(hours=self.unit_amount)

            if check_in.strftime('%Y-%m-%d') != check_out.strftime('%Y-%m-%d'):
                check_out = check_out + relativedelta(seconds=-1)

            vals = {
                'employee_id': self.employee_id.id,
                'check_in': to_naive_utc(check_in, tz_name),
                'check_out': to_naive_utc(check_out, tz_name),
                'state': 'draft',
            }
            attendance = HrAttendance.sudo().create(vals)

        self.write({'is_attendance': True})

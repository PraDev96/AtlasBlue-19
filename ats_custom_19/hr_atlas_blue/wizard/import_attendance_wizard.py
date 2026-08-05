# -*- coding: utf-8 -*-

import xlrd
import base64
import logging
from dateutil import parser
from datetime import datetime
from pytz import timezone, UTC
from odoo import models, fields, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from odoo.addons.base.models.res_partner import _tz_get

_logger = logging.getLogger(__name__)

IGNORE_WORDS = ['', ' ', '-']


def to_naive_user_tz(datetime, tz_name):
    tz = tz_name and timezone(tz_name) or UTC
    return UTC.localize(
        datetime.replace(tzinfo=None),
        is_dst=False).astimezone(tz).replace(tzinfo=None)


def to_naive_utc(datetime, tz_name='Asia/Kolkata'):
    tz = tz_name and timezone(tz_name) or UTC
    return tz.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(UTC).replace(tzinfo=None)


class ImportRentalAttendanceWizard(models.TransientModel):
    _name = 'import.rental.attendance.wizard'
    _description = "Employee Attendance Wizard"

    file = fields.Binary(string="File")
    name = fields.Char(string="File Name")
    tz = fields.Selection(_tz_get, string="Timezone", required=True, default=lambda self: self._context.get('tz') or self.env.user.tz or 'UTC',
                          help="This field is used in order to define in which timezone the resources will work.")

    def parse_file(self, sheet):
        self.ensure_one()
        Employee = self.env['hr.employee']

        file_data = []
        emp_not_found = []
        ignored_lines = []
        skipped_lines = []

        def shouldIgnore(s):
            if not s or s in IGNORE_WORDS:
                return True

            return False

        def xl_dtime(value):
            if type(value) == float:
                return datetime(*xlrd.xldate.xldate_as_tuple(value, sheet.book.datemode))
            elif type(value) == str:
                return parser.parse(value)

            return ''

        cr = self.env.cr

        for r in range(1, sheet.nrows):
            row = sheet.row_values(r)
            if shouldIgnore(row[0]) or shouldIgnore(row[2]) or not row[3] or not row[6]:
                _logger.info("____ IGNORE : %s %s", row[0], row[1])
                ignored_lines.append(','.join(map(str, row)))
                continue

            try:
                from_date = xl_dtime(row[2])
                to_date = xl_dtime(row[3])
                start_date = datetime.combine(from_date, datetime.min.time())
                end_date = datetime.combine(to_date, datetime.max.time())
                emp_code = str(int(row[0]))
                emp_name = str(row[1])

                working_hours = str(row[8])
                if end_date < start_date:
                    s = '%s :: %s :: End Date `%s` Less then Start Date `%s`' % (r, emp_code, from_date, to_date)
                    _logger.info("____ %s ", s)
                    skipped_lines.append(s)
                    continue

                sql = """SELECT id FROM hr_employee WHERE identification_id = %s LIMIT 1"""
                cr.execute(sql, (emp_code,))
                res = cr.fetchone()
                if res and res[0]:
                    emp_id = res[0]
                    emp = Employee.browse(emp_id)

                    sql = """SELECT id FROM resource_calendar WHERE name ilike %s LIMIT 1"""
                    cr.execute(sql, (working_hours,))
                    working_hours_res = cr.fetchone()

                    if working_hours_res:
                        emp.write({'resource_calendar_id': working_hours_res[0]})

                    worked = emp._get_work_days_data_batch(start_date, end_date, domain=[])[emp.id]['days']
                    if not start_date.tzinfo:
                        start_date = start_date.replace(tzinfo=UTC)

                    if not end_date.tzinfo:
                        end_date = end_date.replace(tzinfo=UTC)

                    intervals = emp.resource_calendar_id._work_intervals(start_date, end_date, emp.resource_id, tz=UTC)
                    resource_work_intervals = [start for start, stop, meta in intervals]
                    attendances_list = list(map(lambda dt: dt.astimezone(UTC), resource_work_intervals))

                    # intervals = emp.resource_calendar_id._work_intervals(start_date, end_date)
                    # resource_work_intervals = [start for start, stop, meta in intervals]
                    total_hours = float(row[6])
                    per_day_hours = total_hours / round(worked)

                    already_date_list = []
                    for date in attendances_list:
                        if date.strftime('%Y-%m-%d') in already_date_list:
                            continue

                        attendace_date = date.strftime('%Y-%m-%d') + ' 00:00:00'
                        add_attendace_date = fields.Datetime.from_string(attendace_date)

                        from_date = add_attendace_date
                        to_date = from_date + relativedelta(hours=per_day_hours)
                        file_data.append({
                            'row_index': r,
                            'emp_code': emp_code,
                            'check_in': from_date,
                            'check_out': to_date,
                            'emp': emp,
                        })
                        already_date_list.append(date.strftime('%Y-%m-%d'))
                else:
                    emp_str = '%s:: %s, %s, %s, %s' % (r, emp_code, emp_name, from_date, to_date)
                    emp_not_found.append(emp_str)
            except Exception as e:
                line = ','.join(map(str, row[:4]))
                raise UserError(_('Please Check Row #%s\nLine : %s\nProblem : %s') % (r, line, e))

        return file_data, emp_not_found, ignored_lines, skipped_lines

    def import_attendance(self):
        self.ensure_one()
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))

        sheet = wb.sheets()[0]
        attendance_data, emp_not_found, ignored_lines, skipped_lines = self.parse_file(sheet)
        log, _ = self.create_attendance(attendance_data, emp_not_found, ignored_lines, skipped_lines)
        if log:
            action = self.env.ref('hr_attendance_time.att_upload_log_action').sudo().read()[0]
            action.update({
                'res_id': log.id,
                'view_mode': 'form',
                'domain': [('id', '=', log.id)]
            })

            return action

    def create_attendance(self, attendance_data, emp_not_found, ignored_lines, skipped_lines, name=None, file=None):
        name = name or self.name
        file = file or self.file
        attendances = Attendance = self.env['hr.attendance']
        _logger.info("____ Skipped Lines : %s", ignored_lines)

        def get_public_holiday(global_leaves, dt):
            for global_leave in global_leaves:
                if global_leave['date_from'] <= dt and dt <= global_leave['date_to']:
                    return global_leave

            return {}

        cr = self.env.cr
        for att in sorted(attendance_data, key=lambda a: (a['check_in'])):
            calendar = att['emp'].resource_calendar_id
            working_days = calendar.attendance_ids.mapped('dayofweek')
            global_leaves = calendar.global_leave_ids.read(['name', 'date_from', 'date_to'])
            check_in_day = str(att['check_in'].weekday())
            public_holiday = get_public_holiday(global_leaves, att['check_in'])

            if public_holiday:
                continue

            if check_in_day not in working_days:
                continue

            attendances += Attendance.sudo().create({
                'employee_id': att['emp'].id,
                'check_in': att['check_in'],
                'check_out': att['check_out'],
            })

        log = self.env['att.upload.log']
        if attendances:
            log = log.create({
                'name': name,
                'file': file,
                'skipped_count': len(skipped_lines),
                'skipped_text': '\n'.join(skipped_lines),
                'ignored_count': len(ignored_lines),
                'ignored_text': '\n'.join(ignored_lines),
                'no_emp_count': len(emp_not_found),
                'no_emp_text': '\n'.join(emp_not_found),
            })
            sql = """UPDATE hr_attendance SET att_log_id = %s WHERE id IN %s"""
            cr.execute(sql, (log.id, tuple(attendances.ids),))

        return log, attendances

# -*- coding: utf-8 -*-

import xlrd
import logging
from odoo import models, _
from dateutil import parser
from datetime import datetime
from odoo.exceptions import UserError
from odoo.addons.resource.models.utils import float_to_time
from odoo.addons.hr_attendance_time.models.attendance import to_naive_utc

_logger = logging.getLogger(__name__)
IGNORE_WORDS = ['', ' ', '-']

START_ROW_AT = 1
STOP_ROW_AT = START_ROW_AT + 20000


class ImportEmployeeAttendance(models.TransientModel):
    _inherit = 'import.employee.attendance'

    def parse_file(self, sheet):
        Employee = self.env['hr.employee']
        file_data = []
        ignored_lines = []
        skipped_lines = []

        def shouldIgnore(s):
            if not s or s in IGNORE_WORDS:
                return True

            return False

        file_tz = self.tz

        def xl_dtime(value):
            if type(value) == float:
                return datetime(*xlrd.xldate.xldate_as_tuple(value, sheet.book.datemode))
            elif type(value) == str:
                return parser.parse(value)

            return ''

        for r in range(START_ROW_AT or 1, min(STOP_ROW_AT, sheet.nrows)):
            row = sheet.row_values(r)
            # Check IN Time Must be present
            if shouldIgnore(row[0]) or shouldIgnore(row[2]) or not any(row[:4]):
                _logger.info("____ IGNORE : %s %s %s", row[0], row[1], any(row[:4]))
                ignored_lines.append(','.join(map(str, row)))
                continue

            try:
                emp_code = str(int(row[0]))
                check_in = xl_dtime(row[2])
                is_missed = False

                check_out = False
                if row[3]:
                    check_out = xl_dtime(row[3])
                else:
                    check_out = check_in
                    is_missed = True

                sql = """SELECT id FROM hr_employee WHERE identification_id = %s LIMIT 1"""
                self.env.cr.execute(sql, (emp_code,))
                res = self.env.cr.fetchone()

                hour_from = '00:00:00'
                if res:
                    employee = Employee.browse(res)
                    resource_calendar_id = employee.resource_calendar_id or self.env.company.resource_calendar_id
                    # domain = [('calendar_id', '=', resource_calendar_id.id), ('display_type', '=', False)]
                    # attendances = self.env['resource.calendar.attendance'].read_group(domain, ['hour_from:min(hour_from)'], ['dayofweek'], lazy=False)
                    attendances = resource_calendar_id.attendance_ids.mapped('hour_from')
                    hour_from = float_to_time(min(attendances))

                if check_out < check_in:
                    s = '%s :: %s :: Check Out Time `%s` Less then Check In Time `%s`' % (r, emp_code, check_out, check_in)
                    _logger.info("____ %s ", s)
                    skipped_lines.append(s)
                    continue

                # datetime.combine(compensated_request_date_from, hour_from)
                _logger.info("____ Adding : %s :: %s %s", emp_code, check_in, check_out)

                if check_in.strftime("%H:%M:%S") == '00:00:00':
                    check_in = datetime.combine(check_in, hour_from)
                    check_out = datetime.combine(check_in, hour_from)

                file_data.append({
                    'row_index': r,
                    'emp_code': emp_code,
                    'check_in': to_naive_utc(check_in, file_tz),
                    'check_out': to_naive_utc(check_out, file_tz),
                    'is_missed': is_missed,
                })
            except Exception as e:
                line = ','.join(map(str, row[:4]))
                raise UserError(_('Please Check Row #%s\nLine : %s\nProblem : %s') % (r, line, e))

        _logger.info("____ Total Records : %s", len(file_data))
        _logger.info("____ Total Ignored : %s", len(ignored_lines))
        _logger.info("____ Total Skipped : %s", len(skipped_lines))

        return file_data, ignored_lines, skipped_lines

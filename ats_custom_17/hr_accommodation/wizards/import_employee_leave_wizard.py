# -*- coding: utf-8 -*-

import xlrd
import base64
from odoo import models, fields


class ImportEmployeeLeaveWizard(models.TransientModel):
    _name = 'import.employee.leave.wizard'
    _description = "import.employee.leave.wizard"

    file = fields.Binary(string="File")
    filename = fields.Char(string="Filename")

    def import_leave(self):
        self.ensure_one()
        Employee = self.env['hr.employee']
        LeaveAllocation = self.env['hr.leave.allocation']
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))

        for sheet in wb.sheets():
            for r in range(1, sheet.nrows):
                data = sheet.row_values(r)

                employee_id = data[1]
                duration = data[44]

                print("data::::::::", data)
                print("duration::::::::", duration)
                print("employee_id::::", employee_id)
                if employee_id:
                    employee = Employee.search([('identification_id', '=', str(employee_id).strip())], limit=1)
                    print("employee:::::::::", employee)
                    if employee and float(duration) > 0.0:
                        # employee.write({'identification_id': employee_id})
                        leave_alloc = LeaveAllocation.create({
                            'employee_id': employee.id,
                            'holiday_status_id': 9,
                            # 'allocation_type': 'regular',
                            'holiday_type': 'employee',
                            'number_of_days': duration,
                            'state': 'validate',
                        })
                        # leave_alloc.action_approve()

        return {'type': 'ir.actions.act_window_close'}

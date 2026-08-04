# -*- coding: utf-8 -*-

import xlrd
import base64
from odoo import models, fields


class ImportEmployeeNumberWizard(models.TransientModel):
    _name = 'import.employee.number.wizard'
    _description = "import.employee.number.wizard"

    file = fields.Binary(string="File")
    filename = fields.Char(string="Filename")

    def import_employee(self):
        self.ensure_one()
        Employee = self.env['hr.employee']
        EmployeeBank = self.env['employee.bank']
        Bank = self.env['res.bank']
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))

        for sheet in wb.sheets():
            for r in range(1, sheet.nrows):
                data = sheet.row_values(r)
                employee_id = data[1]
                employee_name = data[2]
                leave_balance_year = data[45]
                leave_balance_month = data[46]
                iban_number = data[31]
                bank = data[30]

                if employee_id:
                    employee = Employee.search([('name', '=', str(employee_name).strip())], limit=1)
                    if employee:
                        employee.write({
                            'leave_balance_per_year': leave_balance_year,
                            'leave_balance_per_month': leave_balance_month,
                            'iban_number': iban_number,
                        })

                        bank_id = Bank.search([('name', '=', bank)], limit=1)
                        EmployeeBank.create({
                            'bank_id': bank_id.id,
                            'iban_number': iban_number,
                            'employee_id': employee.id,
                        })

        return {'type': 'ir.actions.act_window_close'}

# -*- coding: utf-8 -*-

import xlrd
import base64
from odoo import models, fields


class ImportEmployeeLineProjectWizard(models.TransientModel):
    _name = 'import.employee.link.project.wizard'
    _description = "import.employee.link.project.wizard"

    file = fields.Binary(string="File")
    filename = fields.Char(string="Filename")

    def import_employee(self):
        self.ensure_one()
        Employee = self.env['hr.employee']
        Project = self.env['project.project']
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))

        for sheet in wb.sheets():
            for r in range(1, sheet.nrows):
                data = sheet.row_values(r)
                employee_id = data[1]
                current_project = data[11]

                if employee_id:
                    employee = Employee.search([('identification_id', '=', str(employee_id).strip())], limit=1)
                    if employee:
                        project = Project.search([('name', '=', str(current_project).strip())], limit=1)
                        if project:
                            project.write({
                                'employee_ids': [(4, employee.id)],
                            })

        return {'type': 'ir.actions.act_window_close'}

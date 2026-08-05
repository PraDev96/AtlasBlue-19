# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class AddEmployeeWizard(models.TransientModel):
    _name = 'add.employee.wizard'
    _description = "Add Employee Wizard"

    start_date = fields.Date(string="Start Date", required=True, default=fields.Date.context_today)
    employee_ids = fields.Many2many('hr.employee', string="Employees", required=True)

    def add_employee(self):
        self.ensure_one()
        Project = self.env['project.project']
        HistoryProjectEmployee = self.env['history.project.employee']

        project_id = self.env.context.get('active_id')

        already_project_employee = []
        if project_id:
            proj = Project.browse(project_id)
            for employee in self.employee_ids:
                history_employees = HistoryProjectEmployee.search([
                    ('employee_id', '=', employee.id), ('project_id', '!=', project_id),
                    '|', ('end_date', '>=', self.start_date), ('end_date', '=', False)
                ], limit=1)
                if history_employees:
                    already_project_employee.append(employee.name)
                else:
                    history_employees = HistoryProjectEmployee.search([('employee_id', '=', employee.id), ('project_id', '=', project_id), ('end_date', '=', False)], limit=1)
                    if not history_employees:
                        HistoryProjectEmployee.create({
                            'project_id': project_id,
                            'employee_id': employee.id,
                            'start_date': self.start_date,
                        })
                        proj.write({'employee_ids': [(4, employee.id)]})
                        employee.restaurant_id.write({'project_id': project_id})

        if already_project_employee:
            employee_name = ', '.join(already_project_employee)
            raise ValidationError(_('Employee %s already working in project. First remove from existing project!') % employee_name)

        return True

# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RemoveEmployeeWizard(models.TransientModel):
    _name = 'remove.employee.wizard'
    _description = "Remove Employee Wizard"

    @api.model
    def _get_default_project(self):
        project_id = False
        if self.env.context.get('active_id'):
            project_id = self.env.context['active_id']

        return project_id

    end_date = fields.Date(string="End Date", required=True, default=fields.Date.context_today)
    employee_ids = fields.Many2many('hr.employee', string="Employees", required=True)
    project_id = fields.Many2one('project.project', string="Project", default=_get_default_project)

    def remove_employee(self):
        self.ensure_one()
        Project = self.env['project.project']
        HistoryProjectEmployee = self.env['history.project.employee']

        project_id = self.env.context.get('active_id')
        if project_id:
            proj = Project.browse(project_id)
            for employee in self.employee_ids:
                history_employee = HistoryProjectEmployee.search(
                    [('employee_id', '=', employee.id), ('project_id', '=', project_id), ('end_date', '=', False)], order='id desc', limit=1
                )
                history_employee.write({
                    'end_date': self.end_date,
                })
                proj.write({'employee_ids': [(3, employee.id)]})

        return True

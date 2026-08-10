# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api


class EmployeeCost(models.Model):
    _inherit = 'employee.cost'

    opportunity_type = fields.Selection(related='project_id.opportunity_type', store=True)
    team_id = fields.Many2one(related="task_id.team_id", store=True)
    user_id = fields.Many2one(related="task_id.user_id", store=True)
    description = fields.Char(string="Description")
    task_id = fields.Many2one('project.task', string="Task")
    contract_id = fields.Many2one('hr.contract', string="Contract", compute='_compute_contract_details', store=True)
    price_unit = fields.Float(compute='_compute_contract_details', string="Unit Price", store=True)
    subtotal = fields.Monetary(compute='_compute_amount', string="Subtotal", readonly=True, store=True, groups="hr_payroll.group_hr_payroll_manager")
    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")
    from_portal = fields.Boolean(string="Is From Portal")
    is_signature = fields.Boolean(string="Is Signature")

    @api.depends('employee_id')
    def _compute_contract_details(self):
        for rec in self:
            rec.contract_id = rec.employee_id.contract_id.id if rec.employee_id and rec.employee_id.contract_id else False
            rec.price_unit = rec.employee_id.contract_id.id if rec.employee_id and rec.employee_id.contract_id and rec.employee_id.contract_id.per_hour_wage else False

    @api.model
    def create_cost_from_portal(self, args):
        user_id = args.get('user_id', False)
        employee_rec = False
        if user_id:
            employee_rec = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)], limit=1)

        project_id = args.get('project_id', False)
        project_rec = self.env['project.project'].sudo().browse(project_id)
        employee_cost_line_id = args.get('employee_cost_line_id', False)
        if employee_cost_line_id:
            employee_cost_line_rec = self.env['employee.cost'].sudo().browse(eval(employee_cost_line_id))
        else:
            employee_cost_line_rec = self.env['employee.cost'].sudo().create({
                'employee_id': employee_rec.id,
                'project_id': project_rec and project_rec.id,
                'start_date': datetime.now(),
                'from_portal': True,
                'is_signature': True,
                'user_id': user_id,
            })

        start_date = fields.Datetime.context_timestamp(employee_cost_line_rec, employee_cost_line_rec.start_date)
        return {
            'employee_cost_line_rec': employee_cost_line_rec.id,
            'start_date': start_date,
        }

    @api.model
    def update_cost_from_portal(self, args):
        """
        :return:
        """
        if args.get("employee_cost_line_id"):
            employee_cost_line_rec = self.env['employee.cost'].sudo().browse(int(args.get("employee_cost_line_id")))
            if employee_cost_line_rec:
                delta = datetime.now() - employee_cost_line_rec.start_date
                worked_hours = delta.total_seconds() / 3600.0
                employee_cost_line_rec.write({'end_date': datetime.now(), 'hours_spent': worked_hours})
                end_date = fields.Datetime.context_timestamp(employee_cost_line_rec, employee_cost_line_rec.end_date)
                return {
                    'employee_cost_line_rec': employee_cost_line_rec.id,
                    'end_date': end_date,
                    'hours_spent': '{0:02.0f}:{1:02.0f}'.format(*divmod(worked_hours * 60, 60)),
                }

        return {}

    @api.model
    def submit_cost_from_portal(self, args):
        if args.get("employee_cost_line_id"):
            employee_cost_line_rec = self.env['employee.cost'].sudo().browse(args.get("employee_cost_line_id"))
            if employee_cost_line_rec:
                employee_cost_line_rec.write({'description': args.get('description'), 'is_signature': False})
                return {
                    'description': employee_cost_line_rec.description
                }

        return False

# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Calendar(models.Model):
    _inherit = 'calendar.event'

    project_id = fields.Many2one('project.project', string="Project")
    team_id = fields.Many2one('crm.team', string="Project Team")
    partner_id = fields.Many2one(related='project_id.partner_id', store=True)
    type_of_project_id = fields.Many2one(related='project_id.project_type_id', string="Project Type", store=True)
    project_type_id = fields.Many2one(related='project_id.partner_id', string="Project Partner", store=True)
    user_id = fields.Many2one('res.users', store=True)
    end_type = fields.Selection(selection_add=[('count', 'Number of repetitions'), ('end_date', 'End date')])
    task_id = fields.Many2one('project.task', string="Task")

    @api.onchange('team_id')
    def onchange_team_id(self):
        for rec in self:
            if rec.team_id and rec.team_id.user_id:
                rec.user_id = rec.team_id.user_id.id

    @api.model
    def _get_public_fields(self):
        afields = super()._get_public_fields()
        return set(list(afields) + ['project_id', 'team_id', 'partner_id', 'task_id', 'user_id', 'type_of_project_id', 'project_type_id'])

    def create_task_from_calendar_event(self):
        Task = self.env['project.task']
        for rec in self.filtered(lambda e: not e.task_id):
            emp_id = False
            if rec.user_id:
                emp_id = self.env['hr.employee'].search([('user_id', '=', rec.user_id.id)])

            task_id = Task.create({
                'name': rec.name,
                'project_id': rec.project_id.id,
                'partner_id': rec.partner_id.id,
                'team_id': rec.team_id.id,
                'user_id': rec.user_id.id,
                'date_start': rec.start.date(),
                'employee_id': emp_id.id if emp_id else False,
            })
            rec.task_id = task_id.id


class CrmTeamInherit(models.Model):
    _inherit = 'crm.team'

    user_id = fields.Many2one('res.users', required=True, default=lambda self: self.env.user)


class RecurrenceRule(models.Model):
    _inherit = 'calendar.recurrence'

    end_type = fields.Selection(selection_add=[('count', 'Number of repetitions'), ('end_date', 'End date')])

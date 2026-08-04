# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    completion_history_ids = fields.One2many('project.completion.history', 'task_id', string="Completion History Lines", copy=False)
    project_completion_history_count = fields.Integer(string="Project Complete History Count", compute="_compute_project_completion_count")

    def action_view_completion_history(self):
        self.ensure_one()
        action = self.env.ref('ats_project_completion_history.project_completion_history_action').sudo().read()[0]
        project_completion_history = self.env['project.completion.history'].search([('task_id', '=', self.id)])
        action['domain'] = [('id', 'in', project_completion_history.ids)]
        action['views'] = [(False, 'tree')]
        action['context'] = {
            'default_task_id': self.id,
            'search_default_task_id': self.id,
        }

        return action

    def _compute_project_completion_count(self):
        for rec in self:
            if rec.project_id:
                rec.project_completion_history_count = self.env['project.completion.history'].search_count([('task_id', '=', rec.id)])
            else:
                rec.project_completion_history_count = 0

    @api.model_create_multi
    def create(self, vals_list):
        res_values = super(ProjectTask, self).create(vals_list)
        if len(res_values.user_ids.ids) > 1:
            """ This is to restrict the Multiple Assignees. """
            raise ValidationError(_("Not Able to Add Multiple Assignees in the Task!"))

        return res_values

    def write(self, vals):
        # Skip logging if we are in a nested write call triggered by our logic or atlas_base
        if self.env.context.get('skip_completion_history_log'):
            return super(ProjectTask, self).write(vals)

        # Dictionary to store project's data before the change
        project_before = {}
        for task in self:
            if task.project_id and task.project_id.id not in project_before:
                project_before[task.project_id.id] = {
                    'total_completion_percent': task.project_id.total_completion_percent,
                    'total_so_amount': task.project_id.total_so_amount,
                }

        # Use context to prevent double entries during the write operation (e.g. from _update_progress_percentage)
        res = super(ProjectTask, self.with_context(skip_completion_history_log=True)).write(vals)

        if 'user_ids' in vals and len(self.user_ids.ids) > 1:
            """ This is to restrict the Multiple Assignees in the Task. """
            raise ValidationError(_("Not Able to Add Multiple Assignees!"))

        logged_projects = set()
        for task in self:
            project = task.project_id
            if not project or project.id in logged_projects:
                continue

            old_data = project_before.get(project.id)
            if old_data is None:
                continue

            old_val = old_data['total_completion_percent']
            new_val = project.total_completion_percent

            if old_val != new_val:
                if task.user_ids:
                    assigned_for = task.user_ids[0].id
                elif project.user_id.id:
                    assigned_for = project.user_id.id
                else:
                    assigned_for = False
                self.env['project.completion.history'].create({
                    'name': project.name,
                    'project_id': project.id,
                    'old_completion': old_val,
                    'new_completion': new_val,
                    'user_id': self.env.user.id,
                    'difference': new_val - old_val,
                    'track_date': fields.Date.today(),
                    'task_stage_id': task.stage_id.id,
                    'tracked_for_user_id': assigned_for,
                    'customer_id': project.partner_id.id,
                    'project_manager_user_id': project.user_id.id,
                    'task_progress': task.task_progress_percentage,
                    'task_id': task.id if len(self) == 1 else False,
                    'project_team_id': task.team_id.id if task.team_id else False,
                })
                logged_projects.add(project.id)

        return res

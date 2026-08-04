# -*- coding: utf-8 -*-

from odoo import models, fields


class ProjectProject(models.Model):
    _inherit = 'project.project'

    completion_history_ids = fields.One2many('project.completion.history', 'project_id', string="Completion History Lines", copy=False)
    project_completion_history_count = fields.Integer(string="Project Complete History Count", compute="_compute_project_completion_count")

    def action_view_completion_history(self):
        self.ensure_one()
        action = self.env.ref('ats_project_completion_history.project_completion_history_action').sudo().read()[0]
        project_completion_history = self.env['project.completion.history'].search([('project_id', '=', self.id)])
        action.update({
            'domain': [('id', 'in', project_completion_history.ids)],
            'views': [(False, 'tree')],
            'context': {
                'default_project_id': self.id,
                'search_default_project_id': self.id,
            },
        })

        return action

    def _compute_project_completion_count(self):
        for rec in self:
            rec.project_completion_history_count = self.env['project.completion.history'].sudo().search_count([('project_id', '=', rec.id)]) or 0

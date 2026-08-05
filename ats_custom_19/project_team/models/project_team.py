# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    members_ids = fields.Many2many('hr.employee', 'project_emp_rel', 'project_id', 'emp_id', string="Project Members", help="""Project's
                                   members are employees who can have an access to the tasks related to this project.""", tracking=True)
    team_id = fields.Many2one('crm.team', string="Project Team", tracking=True, domain=[('type_team', '=', 'project')])

    @api.onchange('team_id')
    def _get_team_members(self):
        self.update({"members_ids": [(6, 0, self.team_id.team_members_ids.ids)]})

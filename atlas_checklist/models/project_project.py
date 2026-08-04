# -*- coding: utf-8 -*-

from odoo import models, fields


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_checklist_ids = fields.One2many('project.checklist', 'projects_id', string="Project Checklist", tracking=True)

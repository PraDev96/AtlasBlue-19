# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    project_task_checklist_ids = fields.One2many('project.checklist', 'task_id', string="Project Task Checklist")
    is_checklist_task = fields.Boolean(string="Is a Checklist Task", help="Differentiate the task checklist for Civil Work", store=True, tracking=True)
    checklist_type = fields.Selection([
        ('concrete', 'Concrete'),
        ('embedded_piping', 'Embedded Piping'),
        ('work_before_waterproofing', 'Work Before Waterproofing'),
        ('waterproofing', 'Waterproofing'),
        ('acrylic', 'Acrylic'),
        ('tiling', 'Tiling'),
        ('eqsi', 'EQSI'),
        ('commissioning', 'Commissioning'),
        ('service', 'Service'),
    ], string="Checklist Type", store=True, tracking=True)

    is_readonly_checklist = fields.Boolean(string="Is Readonly Checklist", compute="_compute_readonly_checklist", help="Is Checklist Readonly")
    is_task_checklist_data_readonly = fields.Boolean(string="Is Task Checklist Data Readonly", compute="_compute_task_checklist_data_readonly")
    is_show_checklist = fields.Boolean(string="Is Show Checklist", compute="_compute_show_checklist", help="Is Checklist Show")

    def _compute_show_checklist(self):
        for rec in self:
            if rec.is_checklist_task or rec.project_id and rec.project_id.project_type_id and rec.project_id.project_type_id.name == 'Service':
                rec.is_show_checklist = True
            else:
                rec.is_show_checklist = False

    def _compute_readonly_checklist(self):
        for rec in self:
            if rec.project_task_checklist_ids or rec.checklist_type not in ('concrete', 'waterproofing', 'tiling', 'acrylic') or not self.env.user.has_group('ats_civil_project_checklist.group_civil_checklist_backend_creation'):
                rec.is_readonly_checklist = True
            else:
                rec.is_readonly_checklist = False

    def _compute_task_checklist_data_readonly(self):
        for rec in self:
            if not self.env.user.has_group('ats_civil_project_checklist.group_civil_project_checklist_approval'):
                print("yeah")
                rec.is_task_checklist_data_readonly = True
            else:
                rec.is_task_checklist_data_readonly = False

    @api.onchange('is_checklist_task')
    def _onchange_is_checklist_task(self):
        for rec in self:
            if not rec.is_checklist_task:
                rec.checklist_type = False

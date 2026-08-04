# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectCompletionHistory(models.Model):
    _name = 'project.completion.history'
    _description = "Project Completion History"
    _order = 'create_date desc'

    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company, readonly=True)
    project_id = fields.Many2one('project.project', string="Project", required=True, ondelete='cascade')
    project_team_id = fields.Many2one('crm.team', string="Project Team")
    project_total_so_amount = fields.Float(related='project_id.total_so_amount', string="Project Sale Amount", store=True, digits=(16, 3))
    project_value_amount = fields.Float(related='project_id.project_value', string="Project Value", store=True, digits=(16, 3))
    project_subtotal_amount = fields.Float(compute="_compute_project_subtotal_amount", string="Project Net Amount", store=True, digits=(16, 3))
    name = fields.Char(string="Project Name", store=True, translate=True)
    project_manager_user_id = fields.Many2one('res.users', string="Project Manager")
    project_created_user_id = fields.Many2one(related="project_id.create_uid", string="Project Created By")
    project_area_id = fields.Many2one(related="project_id.project_city", string="Project Area")
    customer_id = fields.Many2one('res.partner', string="Customer")
    task_id = fields.Many2one('project.task', string="Task", ondelete='set null')
    task_created_user_id = fields.Many2one(related="task_id.create_uid", string="Task Created By")
    task_stage_id = fields.Many2one('project.task.type', string="Task Stage")
    user_id = fields.Many2one('res.users', string="Tracked By", default=lambda self: self.env.user, required=True)
    tracked_for_user_id = fields.Many2one('res.users', string="Tracked For", required=True)
    task_progress = fields.Float(string="Task Progress(%)", digits=(16, 3))
    track_date = fields.Date(string="Track Date", required=True)
    old_completion = fields.Float(string="Old Completion(%)", digits=(16, 3))
    new_completion = fields.Float(string="New Completion(%)", digits=(16, 3))
    difference = fields.Float(string="Difference(%)", compute="_compute_difference", store=True, digits=(16, 3))

    weightage_pulling_amount = fields.Float(compute="_compute_weightage_pulling_amount", string="Weightage Pulled Amount", store=True, digits=(16, 3))

    @api.depends('project_total_so_amount', 'project_value_amount')
    def _compute_project_subtotal_amount(self):
        for record in self:
            record.project_subtotal_amount = record.project_total_so_amount + record.project_value_amount

    @api.depends('old_completion', 'new_completion')
    def _compute_difference(self):
        for record in self:
            record.difference = record.new_completion - record.old_completion

    @api.depends('difference', 'project_total_so_amount', 'project_value_amount', 'project_subtotal_amount')
    def _compute_weightage_pulling_amount(self):
        for rec in self:
            rec.weightage_pulling_amount = (rec.project_subtotal_amount * rec.difference) / 100

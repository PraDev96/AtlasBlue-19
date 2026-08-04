# -*- coding: utf-8 -*-

from odoo import models, fields


class CrmTeamInherit(models.Model):
    _inherit = 'crm.team'

    type_team = fields.Selection([('sale', 'Sale'), ('project', 'Project')], string="Type", default="sale")
    team_members_ids = fields.Many2many('hr.employee', 'project_team_emp_rel', 'team_id', 'user_id', string="Project Members",
                                        help="""Project's members are employees who can have an access to the tasks related to this project.""")

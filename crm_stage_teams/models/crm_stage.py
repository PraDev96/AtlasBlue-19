# -*- coding: utf-8 -*-

from odoo import models, fields


class Stage(models.Model):
    _inherit = 'crm.stage'

    team_ids = fields.Many2many('crm.team', string="Sales Teams", domain="[('type_team', '=', 'sale')]")

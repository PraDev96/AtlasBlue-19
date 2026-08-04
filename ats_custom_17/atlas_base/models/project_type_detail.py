# -*- coding: utf-8 -*-

from odoo import models, fields


class ProjectType(models.Model):
    _name = 'project.type.detail'
    _description = "Project Type Detail"
    _rec_name ="project_type_detail"

    project_type_detail = fields.Char(string="Type Name", required=True)

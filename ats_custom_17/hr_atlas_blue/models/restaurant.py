# -*- coding: utf-8 -*-

from odoo import models, fields


class FleetRestaurant(models.Model):
    _name = 'fleet.restaurant'
    _description = "Fleet Restaurant"

    name = fields.Char(string="Name", required=True)
    location = fields.Char(string="Location")
    restaurant_id = fields.Char(string="Restaurant ID")
    project_id = fields.Many2one('project.project', string="Project")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)

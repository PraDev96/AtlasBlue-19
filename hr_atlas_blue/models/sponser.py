# -*- coding: utf-8 -*-

from odoo import models, fields


class FleetSponser(models.Model):
    _name = 'fleet.sponser'
    _description = "Fleet Sponsor"

    name = fields.Char(string="Name", required=True)

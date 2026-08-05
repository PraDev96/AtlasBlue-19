# -*- coding: utf-8 -*-

from odoo import models, fields


class LeadTime(models.Model):
	_name = 'lead.time'
	_description = "Lead Time"

	name = fields.Char(string="Lead Name", required=True)

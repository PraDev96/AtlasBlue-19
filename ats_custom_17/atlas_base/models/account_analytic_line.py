# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    active = fields.Boolean(string="Active", default=True)

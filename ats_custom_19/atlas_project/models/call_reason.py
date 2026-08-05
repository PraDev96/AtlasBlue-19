# -*- coding: utf-8 -*-

from odoo import models, fields


class CallReason(models.Model):
    _name = "call.reason"
    _description = "Call Reason"

    name = fields.Char(string="Call Reason Name", required=True)

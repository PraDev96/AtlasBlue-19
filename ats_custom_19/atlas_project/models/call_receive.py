# -*- coding: utf-8 -*-

from odoo import models, fields


class CallReceive(models.Model):
    _name = "call.receive"
    _description = "Call Receive"

    name = fields.Char(string="Call Received On", required=True)

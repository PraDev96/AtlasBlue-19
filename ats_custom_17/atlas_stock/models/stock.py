# -*- coding: utf-8 -*-

from odoo import fields, models


class Layer(models.Model):
    _inherit = 'stock.valuation.layer'

    categ_id = fields.Many2one(related="product_id.categ_id", store=True)

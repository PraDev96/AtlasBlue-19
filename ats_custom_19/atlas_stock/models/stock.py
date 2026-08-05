# -*- coding: utf-8 -*-

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    categ_id = fields.Many2one(related="product_id.categ_id", store=True, string="Category")

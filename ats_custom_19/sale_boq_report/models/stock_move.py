# -*- coding: utf-8 -*-

from odoo import models, fields


class Move(models.Model):
    _inherit = 'stock.move'

    product_category_id = fields.Many2one(related='product_id.categ_id', string="Product Category", readonly=True, store=True)
    product_qty_available = fields.Float(string="On Hand Qty", compute='_compute_product_qty_available', readonly=True)

    def _compute_product_qty_available(self):
        for move in self:
            if move.product_id:
                move.product_qty_available = move.product_id.qty_available

# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_hide_all_qty = fields.Boolean(string="Hide All Quantity", store=True)
    is_hide_all_subtotal = fields.Boolean(string="Hide All Subtotal", store=True)

    @api.onchange('is_hide_all_qty')
    def _onchange_hide_all_quantity(self):
        for rec in self:
            for line in rec.order_line:
                line.is_hide_qty = rec.is_hide_all_qty

    @api.onchange('is_hide_all_subtotal')
    def _onchange_hide_all_subtotal(self):
        for rec in self:
            for line in rec.order_line:
                line.is_hide_subtotal = rec.is_hide_all_subtotal


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_hide_row = fields.Boolean(string="Hide Row", store=True)
    is_hide_qty = fields.Boolean(string="Hide Quantity", store=True, readonly=False)
    is_hide_subtotal = fields.Boolean(string="Hide Subtotal", store=True, readonly=False)


class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    is_hide_row = fields.Boolean(string="Hide Row", store=True)
    is_hide_qty = fields.Boolean(string="Hide Quantity", store=True, readonly=False)
    is_hide_subtotal = fields.Boolean(string="Hide Subtotal", store=True, readonly=False)

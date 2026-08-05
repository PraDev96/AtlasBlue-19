# -*- coding: utf-8 -*-

from odoo import models, fields


class ProjectProject(models.Model):
    _inherit = "purchase.order"

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string="Discount Type", default='percent')
    discount_rate = fields.Float(string="Discount", readonly=True)
    amount_discount = fields.Monetary(string="Bulk Discount", readonly=True, compute='_amount_all', store=True)

    def apply_bulk_discount(self):
        for rec in self:
            total_amount = sum([line.product_qty * line.price_unit for line in rec.order_line])
            discount_per = (rec.discount_rate / total_amount) * 100
            for line in rec.order_line:
                if rec.discount_type == "amount":
                    line.discount = discount_per
                elif rec.discount_type == "percent":
                    if rec.discount_rate != 0.0:
                        line.discount = rec.discount_rate
                        rec.amount_discount = (rec.amount_untaxed + rec.amount_tax) * rec.discount_rate / 100
                    else:
                        rec.amount_discount = 0
                elif not rec.discount_type:
                    rec.amount_discount = 0
                    rec.discount_rate = 0

                rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.amount_discount

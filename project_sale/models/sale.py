# -*- coding: utf-8 -*-

from markupsafe import Markup
from odoo import models, fields, _, api


class SaleOrders(models.Model):
    _inherit = 'sale.order'

    # Replaced these below two field to fix the tracking issue from the base code.
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_total = fields.Monetary(string="Total", store=True, compute='_compute_amounts', tracking=4)

    so_line_ids = fields.Many2many('sale.order.line', string="Hide Subtotal for Sections", domain="[('order_id', '=', id), ('display_type', '=', 'line_section')]")

    def write(self, vals):
        """
            This is to achieve tracking of Total Amount and Untaxed Amount.
            It is not resolved even after replace the amount_total and amount_untaxed
            Therefore we post the message forcefully by code and keep the field the replacement as it is.
        """
        old_total = self.amount_total
        old_untaxed = self.amount_untaxed
        res = super().write(vals)
        if 'order_line' in vals or 'amount_total' in vals:
            audit_log_preview = Markup(
                "<li style='margin-left: 25px;'>%(old_value)s <i class='o_TrackingValue_separator fa fa-long-arrow-right mx-1 text-600' title='%(title)s' role='img' aria-label='%(title)s'></i>%(new_value)s (%(field)s)</li>"
            ) % {
                'old_value': old_total,
                'new_value': self.amount_total,
                'title': _("Changed"),
                'field': 'Total',
            }
            audit_log_preview += Markup(
                "<li style='margin-left: 25px;'>%(old_value)s <i class='o_TrackingValue_separator fa fa-long-arrow-right mx-1 text-600' title='%(title)s' role='img' aria-label='%(title)s'></i>%(new_value)s (%(field)s)</li>"
            ) % {
                'old_value': old_untaxed,
                'new_value': self.amount_untaxed,
                'title': _("Changed"),
                'field': 'Untaxed Amount',
            }
            if self.amount_total != old_total:
                self.message_post(body=audit_log_preview)

        return res

    def message_subscribe(self, partner_ids=None, subtype_ids=None):
        new_partner_ids = []
        for pid in partner_ids:
            if pid not in self.mapped('partner_id.id'):
                new_partner_ids.append(pid)

        return super().message_subscribe(partner_ids=new_partner_ids, subtype_ids=subtype_ids)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    project_id = fields.Many2one(related='order_id.project_id', store=True)

    # This field is replaced from the base sale module
    price_unit = fields.Float(string="Unit Price", compute='_compute_unit_price', required=True,
                              digits='Product Price', store=True, readonly=False, precompute=True)

    @api.onchange('product_id', 'product_uom')
    def _compute_unit_price(self):
        """
            This is to overcome the unit price change issue while change the Quantity.
            Replaced the default field price_unit and added a new compute method instead default _compute_price_unit
            Source : addons/sale/models/sale_order_line.py - 462
            Raised By: Chady Nakhle - 05/11/2025
        """
        for line in self:
            # check if there is already invoiced amount. if so, the price shouldn't change as it might have been
            # manually edited
            if (line.qty_invoiced > 0 or (line.product_id.expense_policy == 'cost' and line.is_expense) or line._is_discount_line()):
                continue

            if not line.product_uom or not line.product_id:
                line.price_unit = 0.0
            else:
                line = line.with_company(line.company_id)
                price = line._get_display_price()
                product_taxes = line.product_id.taxes_id._filter_taxes_by_company(line.company_id)
                line.price_unit = line.product_id._get_tax_included_unit_price_from_price(
                    price,
                    line.currency_id or line.order_id.currency_id,
                    product_taxes=product_taxes,
                    fiscal_position=line.order_id.fiscal_position_id,
                )

    @api.depends('state')
    def _compute_product_uom_readonly(self):
        """
            This is replaced for make the UOM field as readonly for fixing the price change issue while change the quantity.
            Source : addons/sale/models/sale_order_line.py - 947
        """
        for line in self:
            # line.ids checks whether it's a new record not yet saved
            line.product_uom_readonly = True


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        ctx = self.env.context.copy()
        if self.env.context.get('mark_so_as_sent') and 'mail_post_autofollow' in ctx:
            ctx.update({'mail_post_autofollow': False})

        return super(MailThread, self.with_context(**ctx)).message_post(**kwargs)

# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderOption(models.Model):
    _name = 'sale.order.option'
    _inherit = ['sale.order.option', 'analytic.mixin']

    tax_id = fields.Many2many('account.tax', string="Taxes", context={'active_test': False})
    order_id = fields.Many2one('sale.order', string="Order Reference", required=True, ondelete='cascade', index=True, copy=False)
    price_subtotal = fields.Monetary(compute='_compute_amount', string="Subtotal", readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string="Total Tax", readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string="Total", readonly=True, store=True)
    product_uom_qty = fields.Float(string="Product Quantity", digits="Product Unit of Measure", required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string="Product Unit of Measure", domain="[('category_id', '=', product_uom_category_id)]")
    state = fields.Selection(related='order_id.state', string="Order Status", readonly=True, copy=False, store=True)
    display_type = fields.Selection([('line_section', "Section"), ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    customer_lead = fields.Float(string="Lead Time", required=True, default=0.0,
                                 help="Number of days between the order confirmation and the shipping of the products to the customer")
    margin = fields.Float(string="Margin", compute='_compute_margin', digits="Product Price", store=True, groups="base.group_user")
    margin_percent = fields.Float(string="Margin (%)", compute='_compute_margin', store=True, groups="base.group_user", group_operator="avg")
    purchase_price = fields.Float(string="Cost", compute="_compute_purchase_price", digits="Product Price", store=True, readonly=False)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string="Currency", readonly=True)
    company_id = fields.Many2one(related='order_id.company_id', string="Company", store=True, readonly=True, index=True)

    @api.depends('price_subtotal', 'quantity', 'product_uom_qty', 'purchase_price')
    def _compute_margin(self):
        for line in self:
            line.product_uom_qty = line.quantity
            line.margin = line.price_subtotal - (line.purchase_price * line.product_uom_qty)
            line.margin_percent = line.price_subtotal and line.margin / line.price_subtotal

    @api.depends('quantity', 'product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
            Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            line.product_uom_qty = line.quantity
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.depends('product_id', 'order_id.date_order', 'order_id.partner_id')
    def _compute_analytic_distribution(self):
        for line in self:
            if not line.display_type:
                distribution = self.env['account.analytic.distribution.model']._get_distribution({
                    "product_id": line.product_id.id,
                    "product_categ_id": line.product_id.categ_id.id,
                    "partner_id": line.order_id.partner_id.id,
                    "partner_category_id": line.order_id.partner_id.category_id.ids,
                    "company_id": line.company_id.id,
                })
                line.analytic_distribution = distribution or line.analytic_distribution

    @api.depends('product_id', 'company_id', 'currency_id', 'product_uom')
    def _compute_purchase_price(self):
        for line in self:
            if not line.product_id:
                line.purchase_price = 0.0
                continue
            line = line.with_company(line.company_id)
            product = line.product_id
            product_cost = product.standard_price
            if not product_cost:
                # If the standard_price is 0
                # Avoid unnecessary computations
                # and currency conversions
                if not line.purchase_price:
                    line.purchase_price = 0.0
                continue

            fro_cur = product.cost_currency_id
            to_cur = line.currency_id or line.order_id.currency_id
            if line.product_uom and line.product_uom != product.uom_id:
                product_cost = product.uom_id._compute_price(product_cost, line.product_uom)

            line.purchase_price = fro_cur._convert(
                from_amount=product_cost,
                to_currency=to_cur,
                company=line.company_id or self.env.company,
                date=line.order_id.date_order or fields.Date.today(),
                round=False,
            ) if to_cur and product_cost else product_cost
            # The pricelist may not have been set, therefore no conversion
            # is needed because we don't know the target currency..


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_untaxed_op = fields.Monetary(string="Optional Untaxed Amount", store=True, readonly=True, compute='_optional_amount_all', tracking=5)
    amount_tax_op = fields.Monetary(string="Optional Taxes", store=True, readonly=True, compute='_optional_amount_all')
    amount_total_op = fields.Monetary(string="Optional Total", store=True, readonly=True, compute='_optional_amount_all', tracking=4)

    @api.depends('sale_order_option_ids.price_total')
    def _optional_amount_all(self):
        """
            Compute the total amounts of the Optional Products in the Sale Order.
        """
        for order in self:
            amount_untaxed_op = amount_tax_op = 0.0
            for line in order.sale_order_option_ids:
                amount_untaxed_op += line.price_subtotal
                amount_tax_op += line.price_tax

            order.update({
                'amount_untaxed_op': amount_untaxed_op,
                'amount_tax_op': amount_tax_op,
                'amount_total_op': amount_untaxed_op + amount_tax_op,
            })

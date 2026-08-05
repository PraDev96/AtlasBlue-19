# -*- coding: utf-8 -*-

from odoo import api
from odoo.addons.sale_stock_margin.models.sale_order_line import SaleOrderLine as SOL


@api.depends('move_ids', 'move_ids.stock_valuation_layer_ids', 'move_ids.picking_id.state')
def _compute_purchase_price(self):
    """
        To fix the cost disappear issue while confirm the sale order.
        Source : addons/sale_stock_margin/models/sale_order_line.py - 10
        Raised By: Chady Nakhle - 24/11/2025
    """
    line_ids_to_pass = set()
    for line in self:
        product = line.product_id.with_company(line.company_id)
        if not line.has_valued_move_ids():
            line_ids_to_pass.add(line.id)
        elif line.product_id and line.product_id.categ_id.property_cost_method != 'standard':
            # don't overwrite any existing value unless non-standard cost method
            qty_from_delivery = line.qty_delivered if line.product_id.invoice_policy == 'order' else line.qty_to_invoice
            purch_price = product._compute_average_price(0, line.product_uom_qty or qty_from_delivery, line.move_ids.with_company(line.company_id))

            # this is the fix code.
            if not purch_price and line.purchase_price:
                purch_price = line.purchase_price

            if line.product_uom != product.uom_id:
                purch_price = product.uom_id._compute_price(purch_price, line.product_uom)

            line.purchase_price = line._convert_to_sol_currency(purch_price, product.cost_currency_id,)
        elif not line.product_uom_qty and line.qty_delivered:
            # if line added from delivery and standard price, pass to super
            line_ids_to_pass.add(line.id)

    return super(SOL, self.browse(line_ids_to_pass))._compute_purchase_price()


SOL._compute_purchase_price = _compute_purchase_price

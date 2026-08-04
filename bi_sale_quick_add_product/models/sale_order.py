# -*- coding: utf-8 -*-

from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def quick_add_product(self):
        self.ensure_one()
        ctx = self._context.copy()
        ctx.update({
            'sale_quick_products': True,
            'quick_sale_order_id': self.id,
        })
        return {
            'name': 'Select Bulk Products',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.quick.add.product.sale',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'context': ctx
        }

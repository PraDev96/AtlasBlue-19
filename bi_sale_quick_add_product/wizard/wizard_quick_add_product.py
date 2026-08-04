# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WizardQuickAddProductSale(models.TransientModel):
    _name = 'wizard.quick.add.product.sale'
    _description = "Quick Add Product Sale Order Wizard"

    search_product = fields.Char(string="Search Products")
    quick_product_line_ids = fields.One2many('wizard.quick.add.product.sale.line', 'quick_product_wizard_id')
    selected_product_ids = fields.Many2many('product.product', string="Selected Products", compute='_compute_selected_products', store=True)

    @api.depends('quick_product_line_ids')
    def _compute_selected_products(self):
        for rec in self:
            if rec.quick_product_line_ids.filtered(lambda l: l.is_select):
                if rec.selected_product_ids:
                    rec.selected_product_ids = rec.selected_product_ids.ids + rec.quick_product_line_ids.filtered(lambda product_line: product_line.is_select).mapped(
                        'product_id').ids
                else:
                    rec.selected_product_ids = rec.quick_product_line_ids.filtered(lambda product_line: product_line.is_select).mapped('product_id')

            if rec.selected_product_ids:
                rec.write({'selected_product_ids': [(3, qpl.product_id.id) for qpl in rec.quick_product_line_ids.filtered(lambda l: not l.is_select) if
                                                    qpl.product_id.id in rec.selected_product_ids.ids]})

    @api.onchange('search_product')
    def onchange_search_product(self):
        for rec in self:
            selected_products = False
            if rec.selected_product_ids:
                selected_products = rec.selected_product_ids.ids

            rec.quick_product_line_ids = False
            rec.quick_product_line_ids = self.get_products(search_text=self.search_product)

            if selected_products:
                rec.selected_product_ids = selected_products

    def get_products(self, search_text=False):
        if search_text:
            selected_data = []
            for product in self.env['product.product'].sudo().search([('name', 'ilike', search_text)]):
                is_select = False
                if product.id in self.selected_product_ids.ids:
                    is_select = True
                selected_data.append((0, 0, {'is_select': is_select, 'product_id': product.id}))

            return selected_data
        else:
            selected_data = []
            for product in self.env['product.product'].sudo().search([], limit=5):
                is_select = False
                if product.id in self.selected_product_ids.ids:
                    is_select = True
                selected_data.append((0, 0, {'is_select': is_select, 'product_id': product.id}))

            return selected_data

    @api.model
    def default_get(self, fields):

        """ Allow support of active_id / active_model instead of jut default_lead_id
        to ease window action definitions, and be backward compatible. """
        result = super(WizardQuickAddProductSale, self).default_get(fields)
        result['quick_product_line_ids'] = self.get_products()

        return result

    def confirm_products(self):
        sale_order = self.env['sale.order'].sudo().browse(self._context.get('quick_sale_order_id')).exists()
        if sale_order:
            sale_order.write({
                'order_line': [(0, 0, {
                    "order_id": sale_order.id,
                    "name": sop.name,
                    "product_id": sop.id,
                    "product_uom_qty": 1,
                    "product_uom": sop.uom_id.id,
                    "price_unit": sop.lst_price,
                }) for sop in self.selected_product_ids]
            })


class WizardQuickAddProductSaleLine(models.TransientModel):
    _name = 'wizard.quick.add.product.sale.line'
    _description = "Quick Add Product Sale Order Line Wizard"

    quick_product_wizard_id = fields.Many2one('wizard.quick.add.product.sale')
    is_select = fields.Boolean(string="Select", default=False)
    product_id = fields.Many2one('product.product', string="Product")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_bulk_id = fields.Many2many('wizard.quick.add.product.sale', 'bulk_product_add')

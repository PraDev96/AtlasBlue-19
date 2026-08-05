# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models, fields, _, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.onchange('standard_price', 'list_price', 'default_code')
    def onchange_standard_price(self):
        for rec in self:
            if not rec.user_has_groups('atlas_base.group_create_edit_product'):
                raise UserError(_("You have no access to Update Product!!!. Please contact your Administrator."))

    def update_sales_cost_price(self):
        for rec in self.filtered('pack_ids'):
            tot_sales_price = 0
            tot_cost = 0
            for line in rec.pack_ids:
                tot_sales_price += line.product_id.lst_price * line.qty_uom
                tot_cost += line.product_id.standard_price * line.qty_uom

            if tot_sales_price:
                rec.write({'list_price': tot_sales_price})
            if tot_cost:
                rec.write({'standard_price': tot_cost})

    @api.model_create_multi
    def create(self, vals_list):
        # Restrict to Create product, people who don't have the group
        if not self._context.get('from_fleet') and not self.user_has_groups('atlas_base.group_create_edit_product'):
            raise UserError(_("You have no access to Create and Update Product!!!. Please contact your Administrator."))

        record = super(ProductTemplate, self).create(vals_list)
        record.update_sales_cost_price()

        return record

    def write(self, vals):
        # Restrict to Update product, people who don't have the group
        # if not self._context.get('button_validate_picking_ids') and not self._context.get('sale_quick_products') and not self.user_has_groups('atlas_base.group_create_edit_product'):
        #     raise UserError(_("You have no access to Update Product!!!. Please contact your Administrator."))

        res = super(ProductTemplate, self).write(vals)
        if 'pack_ids' in vals:
            self.update_sales_cost_price()

        return res


class Product(models.Model):
    _inherit = "product.product"

    supplie_id = fields.Char(string="Supplier ID")

    @api.onchange('standard_price', 'lst_price', 'default_code')
    def onchange_standard_price(self):
        for rec in self:
            if not rec.user_has_groups('atlas_base.group_create_edit_product'):
                raise UserError(_("You have no access to Update Product!!!. Please contact your Administrator."))

    @api.model_create_multi
    def create(self, vals_list):
        # Restrict to Create product, people who don't have the group
        if not self._context.get('from_fleet') and not self.user_has_groups('atlas_base.group_create_edit_product'):
            raise UserError(_("You have no access to Create and Update Product!!!. Please contact your Administrator."))

        return super(Product, self).create(vals_list)

    def write(self, vals):
        # Restrict to Update product, people who don't have the group
        # if not self._context.get('button_validate_picking_ids') and not self._context.get('sale_quick_products') and not self.user_has_groups('atlas_base.group_create_edit_product'):
        #     raise UserError(_("You have no access to Update Product!!!. Please contact your Administrator."))

        res = super(Product, self).write(vals)
        if vals.get('lst_price') or vals.get('standard_price'):
            pack_lines = self.env['product.pack'].search([('product_id', 'in', self.ids)])
            if pack_lines:
                pack_lines.mapped('bi_product_template').update_sales_cost_price()

        return res

    def btn_electrical_load(self):
        for rec in self:
            rec.electrical_load = sum(pack_rec.product_id.electrical_load for pack_rec in rec.pack_ids) if rec.is_pack else 0


class PackageConfig(models.Model):
    _inherit = 'package.config'

    def update_product(self):
        for rec in self:
            for component in rec.component_ids:
                if component.price_unit:
                    component.update({'price_unit': component.product_id.lst_price})


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        result = super(PurchaseOrder, self).button_confirm()
        if self.project_id:
            store_picking = self.order_line.move_ids.picking_id
            store_picking.write({'project_id': self.project_id.id})

        return result


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    first_serv_due = fields.Date(string="First Service Due")
    last_serv_due = fields.Date(string="Last Service Due")
    axis = fields.Float(string="Axis")
    frequency_time = fields.Integer(string="Frequency Time", compute="_compute_frequency_time")

    @api.depends('opportunity_id')
    def _compute_frequency_time(self):
        for line in self:
            if line.opportunity_id:
                line.frequency_time = line.opportunity_id.number_of_days_per_week
            else:
                line.frequency_time = 0

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'project_id': self.project_id.id,
        })

        return invoice_vals

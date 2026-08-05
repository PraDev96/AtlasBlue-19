# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = "Product Brand"

    name = fields.Char(string="Name", required=True)
    image = fields.Binary(string="Image")
    is_publish = fields.Boolean(string="Publish ?", default=True)

    @api.constrains('name')
    def _name_unique(self):
        for brand in self:
            already_brands = self.env['product.brand'].search([('name', '=', brand.name), ('id', '!=', brand.id)])
            if already_brands:
                raise ValidationError(_('Brand Name Must Be Unique!!!'))


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('product.brand', string="Brand")


class SaleReport(models.Model):
    _inherit = 'sale.report'

    brand_id = fields.Many2one("product.brand", string="Brand")

    def _select_additional_fields(self):
        additional_fields = super(SaleReport, self)._select_additional_fields()
        additional_fields.update({'brand_id': """ t.brand_id"""})

        return additional_fields

    def _group_by_sale(self):
        group_by = super(SaleReport, self)._group_by_sale()
        group_by += """, t.brand_id"""

        return group_by

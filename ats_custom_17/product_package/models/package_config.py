# -*- coding: UTF-8 -*-

from odoo import models, fields, api


class PackageConfig(models.Model):
    _name = 'package.config'
    _description = "Package Config"

    name = fields.Char(required=True)
    sequence = fields.Integer(required=False)  # Unused
    is_root_package = fields.Boolean(string="Is Root Package?")
    is_facility = fields.Boolean(string="Is Facility ?")
    next_package_ids = fields.Many2many('package.config', 'package_config_rel', 'parent_id', 'child_id', domain="[('id', '!=', id)]", string="Next Packages")
    component_ids = fields.One2many('package.component', 'package_id', string="Components", copy=True)
    opportunity_type = fields.Selection(
        [('project', 'Project'), ('service', 'Service'), ('maintenance', 'Maintenance'), ('renovation', 'Renovation'), ('retail_sale', 'Retail Sale')],
        string="Opportunity Type", required=False, default="project")
    skip_package_ids = fields.Many2many('package.config', 'skip_package_config_rel', 'parent_id', 'child_id', domain="[('id', '!=', id)]", string="Skip Packages")


class PackageComponent(models.Model):
    _name = 'package.component'
    _description = 'Package Components'

    package_id = fields.Many2one('package.config', string="Package", required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_uom_qty = fields.Float(string="Quantity", digits='Product Unit of Measure', required=True, default=1.0)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    product_uom = fields.Many2one('uom.uom', string="Unit of Measure", domain="[('category_id', '=', product_uom_category_id)]", required=True)
    price_unit = fields.Float('Unit Price', related='product_id.lst_price', digits='Product Price')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
            # self.price_unit = self.product_id.lst_price


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        ctx = self.env.context.copy()
        for vals in vals_list:
            if 'default_parent_id' in ctx and 'default_b_subcontact' in ctx:
                vals['parent_id'] = ctx['default_parent_id']
                ctx.pop('default_parent_id')

        return super(Partner, self.with_context(ctx)).create(vals_list)

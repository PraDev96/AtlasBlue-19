# -*- coding: UTF-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    root_facility_ids = fields.Many2many('package.config', string="Root Facilities")
    opportunity_type = fields.Selection(
        [('project', 'Project'), ('service', 'Service'), ('maintenance', 'Maintenance'), ('renovation', 'Renovation'), ('retail_sale', 'Retail Sale')],
        string="Opportunity Type", required=True, default="project")

    def action_configure_packages(self):
        ctx = dict(default_sale_order_id=self.id, default_opportunity_type=self.opportunity_type)
        return {
            'name': 'Quotation Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'product.package.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'context': ctx
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    facility_id = fields.Many2one("package.config", string="Package Config")


class ProductPackageWizard(models.TransientModel):
    _name = 'product.package.wizard'
    _description = "Product Package Wizard"

    @api.model
    def _default_line_ids(self):
        vals = []
        default_opportunity_type = self._context.get('default_opportunity_type')
        for record in self.env['package.config'].search([('is_root_package', '=', True), ('opportunity_type', '=', default_opportunity_type)]):
            vals.append((0, 0, {'is_selected': False, 'package_id': record.id}))

        return vals

    check_next_pkg = fields.Boolean(string="Check Next Package", compute="compute_check_next_skip_package", store=True)
    check_skip_pkg = fields.Boolean(string="Skip Package", compute="compute_check_next_skip_package", store=True)
    highlight_confirm = fields.Boolean(string="Highlight Confirm Button", compute="_compute_highlight_confirm", store=True)
    line_ids = fields.One2many('product.package.wizard.line', 'product_pkg_wizard_id', string="Lines", default=_default_line_ids)
    selected_package_ids = fields.One2many('selected.package', 'product_pkg_wizard_id', string="Selected Items")
    package_component_ids = fields.One2many('selected.package.component1', 'product_pkg_wizard_id', string="Components")
    sale_order_id = fields.Many2one('sale.order')
    opportunity_type = fields.Selection(
        [('project', 'Project'), ('service', 'Service'), ('maintenance', 'Maintenance'), ('renovation', 'Renovation'), ('retail_sale', 'Retail Sale')],
        string="Opportunity Type", required=True, default="project")
    show_confirm_button = fields.Boolean(default=False)
    sale_partner_id = fields.Many2one(related='sale_order_id.partner_id', store=True)
    partner_id = fields.Many2one('res.partner', string="Address", required=True)
    system_type = fields.Selection([('skimmer', 'Skimmer'), ('overflow', 'Overflow')], string="System Type")
    water_surface = fields.Float(string="Water Surface (m²)")
    all_selected = fields.Boolean(string="Select All Components")
    volume = fields.Float(string="Volume (m³)")

    @api.depends('check_next_pkg', 'check_skip_pkg')
    def _compute_highlight_confirm(self):
        for wizard in self:
            wizard.highlight_confirm = not wizard.check_next_pkg and not wizard.check_skip_pkg

    @api.depends('line_ids')
    def compute_check_next_skip_package(self):
        self.check_next_pkg = False
        self.check_skip_pkg = False
        filtered_line_ids = self.line_ids
        if not all([not line.is_selected for line in self.line_ids]):
            filtered_line_ids = self.line_ids.filtered(lambda rec: rec.is_selected)

        if any([line.package_id.next_package_ids for line in filtered_line_ids]):
            self.check_next_pkg = True

        if any([line.package_id.skip_package_ids for line in filtered_line_ids]):
            self.check_skip_pkg = True

    @api.onchange('line_ids', 'line_ids.is_selected')
    def onchange_line_ids_is_selected(self):
        selected_line_id = self.line_ids.filtered('is_selected')
        self.package_component_ids = False
        if selected_line_id:
            vals = []
            for component in selected_line_id.package_id.component_ids:
                vals.append((0, 0, {
                    'product_pkg_wizard_id': self.id,
                    'product_id': component.product_id.id,
                    'product_uom_qty': component.product_uom_qty,
                    'product_uom': component.product_uom.id,
                    'price_unit': component.price_unit,
                }))

            self.package_component_ids = vals

    @api.onchange('all_selected')
    def onchange_all_selected(self):
        for val in self:
            for rec in val.package_component_ids:
                rec.is_selected = val.all_selected

    def action_confirm(self):
        self.check_last_package_selected()
        root_facility = self.mapped('selected_package_ids.package_ids').filtered('is_root_package')
        root_facility_id = root_facility.id
        lines_with_same_package = self.sale_order_id.order_line.filtered(lambda l: l.facility_id.id == root_facility_id)
        for line in lines_with_same_package:
            self.sale_order_id.order_line = [(2, line.id)]

        line_seq = self.sale_order_id.mapped('order_line.sequence')
        line_seq.sort()
        line_seq = line_seq[-1] if line_seq else 0

        if self.sale_order_id.partner_shipping_id != self.partner_id:
            self.sale_order_id.partner_shipping_id = self.partner_id.id

        SaleOrderLine = self.env['sale.order.line']
        facilitys = self.env['facility.facility']
        facilitys.create({
            'name': self.sale_order_id.name,
            'location_id': self.partner_id.id,
            'partner_id': self.sale_order_id.partner_id.id,
            'facility_type_id': root_facility.facility_type_id.id,
            'facility_id': root_facility_id,
            'facility_project_id': self.sale_order_id.project_id.id,
            'crm_lead_id': self.sale_order_id.opportunity_id.id,
            'system_type': self.system_type,
            'water_surface': self.water_surface,
            'volume': self.volume
        })

        for selected_line in self.mapped('selected_package_ids'):
            rec = selected_line.package_ids
            line_seq += 1
            if rec.is_root_package:
                vals = {
                    'name': self.sale_order_id.name + ' : ' + rec.name,
                    'location_id': self.partner_id.id,
                    'facility_id': rec.id,
                    'system_type': self.system_type,
                    'water_surface': self.water_surface,
                    'volume': self.volume,
                    'sale_order_id': self.sale_order_id.id
                }
                root_facility_id = rec.id
                facility_id = self.sale_order_id.facility_ids.filtered(lambda l: l.facility_id.id == root_facility_id)
                if facility_id:
                    facility_id.write(vals)
                else:
                    self.sale_order_id.facility_ids = [(0, 0, vals)]
                self.sale_order_id.root_facility_ids = [(4, rec.id)]

            if selected_line.component_ids:
                SaleOrderLine.create({
                    'name': rec.name,
                    'display_type': 'line_section',
                    'order_id': self.sale_order_id.id,
                    'sequence': line_seq,
                    'facility_id': root_facility_id,
                })
            for line in selected_line.component_ids:
                line_seq += 1
                SaleOrderLine.create({
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'order_id': self.sale_order_id.id,
                    'sequence': line_seq,
                    'facility_id': root_facility_id,
                })

    def check_last_package_selected(self):
        """
            This is for adding the last component to the sale order line while confirming the Quotation Wizard.
        """
        if not self.line_ids.filtered('is_selected'):
            return True

        selected_pkg_ids = self.line_ids.filtered('is_selected').mapped('package_id')
        if len(selected_pkg_ids.ids) != 1:
            raise ValidationError(_("You must select one package at a time!"))

        if selected_pkg_ids[0] in self.selected_package_ids.mapped('package_ids'):
            return True

        line_vals = []
        for component in self.package_component_ids.filtered('is_selected'):
            line_vals.append((0, 0, {
                'product_id': component.product_id.id,
                'product_uom_qty': component.product_uom_qty,
                'product_uom': component.product_uom.id,
                'price_unit': component.price_unit,
            }))

        self.selected_package_ids = [(0, 0, {'package_ids': [(4, pkg_id.id) for pkg_id in selected_pkg_ids], 'component_ids': line_vals})]

    def next_packages(self):
        selected_pkg_ids = self.line_ids.filtered('is_selected').mapped('package_id')
        if len(selected_pkg_ids.ids) != 1:
            raise ValidationError(_("You must select one package at a time!"))

        line_vals = []
        for component in self.package_component_ids.filtered('is_selected'):
            line_vals.append((0, 0, {
                'product_id': component.product_id.id,
                'product_uom_qty': component.product_uom_qty,
                'product_uom': component.product_uom.id,
                'price_unit': component.price_unit,
            }))

        self.package_component_ids = False
        self.selected_package_ids = [(0, 0, {'package_ids': [(4, pkg_id.id) for pkg_id in selected_pkg_ids], 'component_ids': line_vals})]
        next_pkgs = selected_pkg_ids.mapped('next_package_ids')
        self.line_ids = False
        if next_pkgs:
            vals = []
            for record in next_pkgs:
                vals.append((0, 0, {'is_selected': False, 'package_id': record.id}))
            self.line_ids = vals
            self.show_confirm_button = True

        ctx = self.env.context.copy()
        ctx.update({
            'default_opportunity_type': self.opportunity_type,
        })
        return {
            'name': 'Quotation Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'product.package.wizard',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'res_id': self.id,
            'context': ctx,
        }

    def previous_packages(self):
        selected_package_ids = self.mapped('selected_package_ids.id')
        if selected_package_ids:
            self.selected_package_ids = [(3, selected_package_ids[-1])]
            self.show_confirm_button = False
        vals = []
        self.line_ids = False
        if self.selected_package_ids:
            for package_id in self.selected_package_ids[-1].mapped('package_ids.next_package_ids'):
                vals.append((0, 0, {'is_selected': False, 'package_id': package_id.id}))
        else:
            for record in self.env['package.config'].search([('is_root_package', '=', True), ('opportunity_type', '=', self.opportunity_type)]):
                vals.append((0, 0, {'is_selected': False, 'package_id': record.id}))

        self.line_ids = vals
        return {
            'name': 'Quotation Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'product.package.wizard',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'res_id': self.id,
        }

    def skip_packages(self):
        selected_pkg_ids = self.line_ids.mapped('package_id')
        skip_pkgs = selected_pkg_ids.mapped('skip_package_ids')
        if not skip_pkgs:
            raise ValidationError(_("You cannot skip the package. Please confirm it or select the next package!"))

        self.line_ids.unlink()
        vals = [(0, 0, {'is_selected': False, 'package_id': pkg.id}) for pkg in skip_pkgs]
        self.line_ids = vals
        return {
            'name': 'Quotation Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'product.package.wizard',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'res_id': self.id,
        }


class ProductPackageWizardLine(models.TransientModel):
    _name = 'product.package.wizard.line'
    _description = "Product Package Wizard Line"

    is_selected = fields.Boolean(string="Select")
    package_id = fields.Many2one('package.config')
    product_pkg_wizard_id = fields.Many2one('product.package.wizard')


class SelectedPackage(models.TransientModel):
    _name = 'selected.package'
    _description = "Selected Package"
    _order = 'id'

    package_ids = fields.Many2many('package.config')
    product_pkg_wizard_id = fields.Many2one('product.package.wizard')
    component_ids = fields.One2many('selected.package.component', 'select_package_id', string='Components')


class SelectedPackageComponent(models.TransientModel):
    _name = 'selected.package.component'
    _description = "Selected Package Components"

    select_package_id = fields.Many2one('selected.package', string="Package", ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_uom_qty = fields.Float(string="Quantity", digits='Product Unit of Measure', required=True, default=1.0)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    product_uom = fields.Many2one('uom.uom', string="Unit of Measure", domain="[('category_id', '=', product_uom_category_id)]", required=True)
    price_unit = fields.Float(string="Unit Price", required=True, digits='Product Price', default=0.0)


class SelectedPackageComponent1(models.TransientModel):
    _name = 'selected.package.component1'
    _description = "Selected Package Components1"

    product_pkg_wizard_id = fields.Many2one('product.package.wizard', ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_uom_qty = fields.Float(string="Quantity", digits='Product Unit of Measure', required=True, default=1.0)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    product_uom = fields.Many2one('uom.uom', string="Unit of Measure", domain="[('category_id', '=', product_uom_category_id)]", required=True)
    price_unit = fields.Float(string="Unit Price", required=True, digits='Product Price', default=0.0)
    is_selected = fields.Boolean(string="Select")

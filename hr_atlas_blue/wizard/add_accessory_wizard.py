# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class AddAccessoryWizard(models.TransientModel):
    _name = 'add.accessory.wizard'
    _description = "Add Accessory Wizard"

    wizard_line_ids = fields.One2many('add.accessory.wizard.line', 'accessory_wizard_id', string="Lines")

    def add_accessory(self):
        self.ensure_one()
        StockMove = self.env['stock.move']
        FleetVehicle = self.env['fleet.vehicle']
        stock_moves = self.env['stock.move']

        fleet_id = self.env.context.get('active_id')
        if fleet_id:
            warehouse = self.env['stock.warehouse'].sudo().search([('company_id', '=', self.env.user.company_id.id)], limit=1)

            location_id = warehouse.lot_stock_id
            location_dest_id = self.env.ref('hr_atlas_blue.stock_fleet_locations_partner')

            fleet = FleetVehicle.browse(fleet_id)
            for line in self.wizard_line_ids:
                if line.lot_id:
                    available_qty = line.product_id.with_context(lot_id=line.lot_id).free_qty
                else:
                    available_qty = line.product_id.free_qty  # self.env['stock.quant']._get_available_quantity(self.product_id)

                if line.quantity > available_qty:
                    raise ValidationError(_("You can not add more quantity then available quantity for %s!") % line.product_id.name)

                stock_move = StockMove.sudo().create({
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.uom_id.id,
                    'location_id': location_id.id,
                    'location_dest_id': location_dest_id.id,
                    'reference': fleet.model_id.name,
                    'quantity': line.quantity,
                    'fleet_vehicle_id': fleet_id,
                    'company_id': self.env.user.company_id.id,
                })
                stock_moves += stock_move

        stock_moves._action_done()


class AddAccessoryWizardLine(models.TransientModel):
    _name = 'add.accessory.wizard.line'
    _description = "Add Accessory Wizard Line"

    product_id = fields.Many2one('product.product', string="Product", required=True)
    uom_id = fields.Many2one('uom.uom', string="UoM", required=True)
    quantity = fields.Float(string="Quantity", default=1.0, required=True)
    available_quantity = fields.Float(string="Available Quantity")
    lot_id = fields.Many2one('stock.lot', string="Lot")
    accessory_wizard_id = fields.Many2one('add.accessory.wizard', string="Accessory Lines")

    @api.onchange('product_id', 'lot_id')
    def onchange_product_id(self):
        self.available_quantity = 0.0
        if self.product_id:
            if self.lot_id:
                available_qty = self.product_id.with_context(lot_id=self.lot_id).free_qty
            else:
                available_qty = self.product_id.free_qty  # self.env['stock.quant']._get_available_quantity(self.product_id)

            self.available_quantity = available_qty
            self.uom_id = self.product_id.uom_id

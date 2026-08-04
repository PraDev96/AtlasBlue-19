# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class RemoveAccessoryWizard(models.TransientModel):
    _name = 'remove.accessory.wizard'
    _description = "Remove Accessory Wizard"

    def _get_default_from_fleet(self):
        from_fleet_id = False
        if self.env.context.get('active_id'):
            from_fleet_id = self.env.context['active_id']

        return from_fleet_id

    # product_ids = fields.Many2many('product.product', string='Products')
    wizard_line_ids = fields.One2many('remove.accessory.wizard.line', 'remove_wizard_id', string="Lines")
    from_fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="From Fleet", default=_get_default_from_fleet, required=True)
    to_fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="To Fleet")

    def remove_accessory(self):
        self.ensure_one()
        StockMove = self.env['stock.move']
        stock_moves = self.env['stock.move']

        from_fleet_vehicle_id = self.from_fleet_vehicle_id
        to_fleet_vehicle_id = self.to_fleet_vehicle_id

        warehouse = self.env['stock.warehouse'].sudo().search([('company_id', '=', self.env.user.company_id.id)], limit=1)

        location_id = self.env.ref('hr_atlas_blue.stock_fleet_locations_partner')
        location_dest_id = warehouse.lot_stock_id

        for line in self.wizard_line_ids:
            if from_fleet_vehicle_id and to_fleet_vehicle_id:
                stock_move = StockMove.search([('product_id', '=', line.product_id.id), ('fleet_vehicle_id', '=', from_fleet_vehicle_id.id)], limit=1)
                if stock_move.product_uom_qty > line.quantity:
                    values = {
                        'product_uom_qty': line.quantity,
                        'fleet_vehicle_id': to_fleet_vehicle_id.id,
                    }
                    stock_move.copy(default=values)
                    stock_move.write({'product_uom_qty': (stock_move.product_uom_qty - line.quantity)})
                elif stock_move.product_uom_qty < line.quantity:
                    raise ValidationError(_("You can not remove more quantity then existing quantity for %s!") % line.product_id.name)
                else:
                    values = {
                        'fleet_vehicle_id': to_fleet_vehicle_id.id,
                    }
                    stock_move.write(values)
            else:
                stock_move = StockMove.sudo().create({
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.uom_id.id,
                    'location_id': location_id.id,
                    'location_dest_id': location_dest_id.id,
                    'reference': to_fleet_vehicle_id.model_id.name,
                    'quantity': line.quantity,
                    'fleet_vehicle_id': to_fleet_vehicle_id.id,
                    'company_id': self.env.user.company_id.id,
                })
                stock_moves += stock_move

        stock_moves._action_done()


class RemoveAccessoryWizardLine(models.TransientModel):
    _name = 'remove.accessory.wizard.line'
    _description = "Remove Accessory Wizard Line"

    product_id = fields.Many2one('product.product', string="Product", required=True)
    uom_id = fields.Many2one('uom.uom', string="UoM", required=True)
    quantity = fields.Float(string="Quantity", default=1.0, required=True)
    lot_id = fields.Many2one('stock.lot', string="Lot")
    remove_wizard_id = fields.Many2one('remove.accessory.wizard', string="Remove Lines")

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.uom_id = False
        if self.product_id:
            self.uom_id = self.product_id.uom_id

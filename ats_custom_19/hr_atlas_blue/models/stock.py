# -*- coding: utf-8 -*-

from odoo import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_fleet_location = fields.Boolean(string="Is Fleet Location?")


class StockMove(models.Model):
    _inherit = 'stock.move'

    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Fleet Vehicle")
    fleet_log_services_id = fields.Many2one('fleet.vehicle.log.services', string="Fleet Vehicle Services")
    stock_on_hand = fields.Float(string="Qty Available", related='product_id.qty_available')

    # stock_on_specific_hand = fields.Float('Qty Available Source Location')

    # @api.onchange('product_id', 'picking_type_id')
    # def onchange_product(self):
    #     super(StockMove, self).onchange_product()
    #     if self.product_id:
    #         qty_available = self.product_id.with_context(location=self.picking_id.location_id.id).qty_available
    #         self.stock_on_specific_hand = qty_available

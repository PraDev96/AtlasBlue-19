# -*- coding: utf-8 -*-

from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_force_availability(self):
        for picking in self:
            for move in picking.move_lines:
                move.write({'quantity': move.product_uom_qty, 'state': 'assigned'})
            picking._check_entire_pack()

    def action_force_validate(self):
        for picking in self:
            picking.action_force_availability()
            picking.button_validate()

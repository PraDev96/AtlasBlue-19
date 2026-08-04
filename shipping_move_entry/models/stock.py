# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    picking_id = fields.Many2one('stock.picking', string="Picking")


class Picking(models.Model):
    _inherit = 'stock.picking'

    move_picking_ids = fields.Many2many('account.move', 'account_move_picking_default_rel', 'move_id', 'picking_id', string="Moves")
    account_move_line_ids = fields.One2many('account.move.line', 'picking_id', string="Move Lines", tracking=True)
    total_debit = fields.Float(string="Total Debit", store=True, compute="_compute_total_debit")

    @api.depends('account_move_line_ids', 'account_move_line_ids.debit')
    def _compute_total_debit(self):
        for rec in self:
            rec.total_debit = sum(rec.account_move_line_ids.mapped('debit'))


class StockMove(models.Model):
    _inherit = 'stock.move'

    picking_code = fields.Selection(related='picking_id.picking_type_id.code', string="Transfer Type", readonly=True, store=True)

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description):
        result = super()._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description)

        picking_id = self.picking_id.id
        analytic_distribution = self.purchase_line_id.analytic_distribution or {self.picking_id.account_analytic_id.id: 100} if self.picking_id.account_analytic_id else False
        if result.get('credit_line_vals'):
            result['credit_line_vals'].update({
                'picking_id': picking_id,
                'analytic_distribution': analytic_distribution,
            })

        if result.get('debit_line_vals'):
            result['debit_line_vals'].update({
                'picking_id': picking_id,
                'analytic_distribution': analytic_distribution,
            })

        if result.get('price_diff_line_vals'):
            result['price_diff_line_vals'].update({
                'picking_id': picking_id,
            })

        return result

    @api.depends('state', 'picking_id.is_locked')
    def _compute_is_initial_demand_editable(self):
        """
            Replaced it for edit demand quantity (product_uom_qty).
        """
        for move in self:
            move.is_initial_demand_editable = not move.state in ('draft', 'waiting')


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    picking_code = fields.Selection(related='picking_type_id.code', string="Transfer Type", readonly=True, store=True)

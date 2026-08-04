# -*- coding: utf-8 -*-

from odoo import models, fields, _


class Move(models.Model):
    _inherit = 'account.move'

    recurrent_ref_id = fields.Many2one("sale.recurring.invoice", string="Recurrent Ref", tracking=True)

    def action_invoice_recurrent(self):
        return {
            'name': _('Generate Recurrent Invoice'),
            'res_model': 'sale.recurring.invoice',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
                'default_ref_invoice_id': self.id,
            },
            'res_id': self.recurrent_ref_id.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

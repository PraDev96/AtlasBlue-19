# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')

    def _prepare_move_line_default_vals(self, *args, **kwargs):
        lines = super(AccountPayment, self)._prepare_move_line_default_vals(*args, **kwargs)
        for line in lines:
            if self.analytic_account_id:
                line.update({
                    'analytic_distribution': {str(self.analytic_account_id.id): 100.0},
                })

        return lines


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        payment_vals.update({
            'analytic_account_id': self.analytic_account_id.id,
        })

        return payment_vals

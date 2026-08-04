# -*- coding: utf-8 -*-

from odoo import models


class ClaimConfirmWizard(models.TransientModel):
    _name = 'claim.confirm.wizard'
    _description = "Claim Confirm Wizard"

    def action_confirm(self):
        self.ensure_one()
        claim_ids = self.env.context.get('active_ids')
        if claim_ids:
            claims = self.env['hr.claim'].browse(claim_ids)
            claims.action_confirm()

        return True

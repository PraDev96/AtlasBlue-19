# -*- coding: utf-8 -*-

from odoo import models


class ClaimPendingWizard(models.TransientModel):
    _name = 'claim.pending.wizard'
    _description = "Claim Pending Wizard"

    def action_pending(self):
        self.ensure_one()
        claim_ids = self.env.context.get('active_ids')
        if claim_ids:
            claims = self.env['hr.claim'].browse(claim_ids)
            claims.action_pending()

        return True

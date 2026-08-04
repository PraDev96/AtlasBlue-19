# -*- coding: utf-8 -*-

from odoo import models


class ClaimDoneWizard(models.TransientModel):
    _name = 'claim.done.wizard'
    _description = "Claim Done Wizard"

    def action_done(self):
        self.ensure_one()
        claim_ids = self.env.context.get('active_ids')
        if claim_ids:
            claims = self.env['hr.claim'].browse(claim_ids)
            claims.action_done()

        return True

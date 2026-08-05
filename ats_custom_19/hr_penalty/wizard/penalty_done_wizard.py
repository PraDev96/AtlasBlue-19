# -*- coding: utf-8 -*-

from odoo import models


class PenaltyDoneWizard(models.TransientModel):
    _name = 'penalty.done.wizard'
    _description = "Penalty Done Wizard"

    def action_done(self):
        self.ensure_one()
        penalty_ids = self.env.context.get('active_ids')
        if penalty_ids:
            penaltys = self.env['hr.penalty'].browse(penalty_ids)
            penaltys.action_done()

        return True

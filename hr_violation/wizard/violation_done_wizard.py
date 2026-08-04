# -*- coding: utf-8 -*-

from odoo import models


class ViolationDoneWizard(models.TransientModel):
    _name = 'violation.done.wizard'
    _description = "Violation Done Wizard"

    def action_done(self):
        self.ensure_one()
        Violation_ids = self.env.context.get('active_ids')
        if Violation_ids:
            violations = self.env['hr.violation'].browse(Violation_ids)
            violations.action_done()

        return True

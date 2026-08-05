# -*- coding: utf-8 -*-

from odoo import models


class InsuranceDoneWizard(models.TransientModel):
    _name = 'insurance.done.wizard'
    _description = 'Insurance Done Wizard'

    def action_done(self):
        self.ensure_one()
        insurance_ids = self.env.context.get('active_ids')
        if insurance_ids:
            insurances = self.env['hr.insurance'].browse(insurance_ids)
            insurances.action_claim()
        return True

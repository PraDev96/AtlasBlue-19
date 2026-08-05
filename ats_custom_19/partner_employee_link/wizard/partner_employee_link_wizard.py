# -*- coding: utf-8 -*-

from odoo import models


class WizardPartnerEmployeeLink(models.TransientModel):
    _name = 'wizard.partner.employee.link'
    _description = "Wizard Partner Employee Link"

    def action_link(self):
        self.ensure_one()
        Partner = self.env['res.partner']
        employee_ids = self.env.context.get('active_ids')
        if employee_ids:
            employees = self.env['hr.employee'].browse(employee_ids).filtered(lambda x: not x.partner_id)
            for employee in employees:
                partner = Partner.create({
                    'name': employee.name,
                    'phone': employee.work_phone,
                    'email': employee.work_email,
                    'mobile': employee.mobile_phone,
                })
                employee.write({'partner_id': partner.id})

        return True

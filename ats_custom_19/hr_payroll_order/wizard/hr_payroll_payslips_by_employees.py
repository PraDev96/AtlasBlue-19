# -*- coding: utf-8 -*-

from odoo import models


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _get_available_contracts_domain(self):
        PayslipRun = self.env['hr.payslip.run']
        domain = [('contract_ids.state', 'in', ('open', 'close'))]
        if self.env.context.get('active_id'):
            payslip_run = PayslipRun.browse(self.env.context['active_id'])
            domain.append(('company_id', '=', payslip_run.company_id.id))
            if payslip_run.department_id:
                domain.append(('department_id', '=', payslip_run.department_id.id))

            if payslip_run.category_id:
                domain.append(('category_ids', 'in', payslip_run.category_id.ids))

        return domain

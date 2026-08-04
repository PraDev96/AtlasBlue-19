# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    """ Extends the 'hr.payslip' model to include
    additional functionality related to employee loans."""
    _inherit = 'hr.payslip'

    is_refund = fields.Boolean(string="Is Refund?")

    def refund_sheet(self):
        for payslip in self:
            already_refund_payslips = self.search([
                ('date_from', '<=', payslip.date_to),
                ('date_to', '>=', payslip.date_from),
                ('employee_id', '=', payslip.employee_id.id),
                ('id', '!=', payslip.id),
                ('state', 'in', ('verify', 'done')),
                ('is_refund', '=', True)
            ])
            if already_refund_payslips:
                raise ValidationError(_("For given period and employee already refund payslip exits!"))

            copied_payslip = payslip.copy(default={'credit_note': True, 'name': _('Refund: ') + payslip.name, 'is_refund': True})
            copied_payslip.compute_sheet()
            copied_payslip.action_payslip_done()

        formview_ref = self.env.ref('hr_payroll.view_hr_payslip_form', False)
        treeview_ref = self.env.ref('hr_payroll.view_hr_payslip_tree', False)
        return {
            'name': ("Refund Payslip"),
            'view_mode': 'tree, form',
            'view_id': False,
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id', 'in', %s)]" % copied_payslip.ids,
            'views': [(treeview_ref and treeview_ref.id or False, 'tree'), (formview_ref and formview_ref.id or False, 'form')],
            'context': {}
        }

    def get_inputs(self, contract_ids, date_from, date_to):
        """Compute additional inputs for the employee payslip,
        considering active loans.
        :param contract_ids: Contract ID of the current employee.
        :param date_from: Start date of the payslip.
        :param date_to: End date of the payslip.
        :return: List of dictionaries representing additional inputs for
        the payslip."""
        res = super(HrPayslip, self).get_inputs(contract_ids, date_from,
                                                date_to)
        employee_id = self.env['hr.contract'].browse(
            contract_ids[0].id).employee_id if contract_ids \
            else self.employee_id
        loan_id = self.env['hr.loan'].search(
            [('employee_id', '=', employee_id.id), ('state', '=', 'approve')])
        for loan in loan_id:
            for loan_line in loan.loan_lines:
                if (date_from <= loan_line.date <= date_to and
                        not loan_line.paid):
                    for result in res:
                        if result.get('code') == 'LO':
                            result['amount'] = loan_line.amount
                            result['loan_line_id'] = loan_line.id
        return res

    def action_payslip_done(self):
        """ Compute the loan amount and remaining amount while confirming
            the payslip"""
        for line in self.input_line_ids:
            if line.loan_line_id:
                line.loan_line_id.paid = True
                line.loan_line_id.loan_id._compute_total_amount()
        return super(HrPayslip, self).action_payslip_done()

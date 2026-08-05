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
from odoo import fields, models, _


class HrEmployee(models.Model):
    """Extends the 'hr.employee' model to include loan_count."""
    _inherit = "hr.employee"

    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        Loan = self.env['hr.loan']
        for rec in self:
            loans = Loan.search([('employee_id', '=', rec.id)])
            rec.loan_count = len(loans)
            rec.loan_balance = round(sum(loans.mapped('balance_amount')), 4)
            rec.loan_total = round(sum(loans.mapped('total_amount')), 4)
            rec.total_paid_amount = round(sum(loans.mapped('total_paid_amount')), 4)

    loan_count = fields.Integer(
        string="Loan Count",
        help="Number of loans associated with the employee",
        compute='_compute_loan_count')
    loan_balance = fields.Float(string='Loan Balance', compute='_compute_employee_loans', digits=(16, 4))
    loan_total = fields.Float(string='Loan Total', compute='_compute_employee_loans', digits=(16, 4))
    loan_total_paid = fields.Float(string='Loan Total Paid', compute='_compute_employee_loans', digits=(16, 4))
    total_paid_amount = fields.Float(string='Total Paid Amount', compute='_compute_employee_loans', digits=(16, 4))

    def _compute_loan_count(self):
        """Compute the number of loans associated with the employee."""
        for rec in self:
            rec.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', rec.id)])

    def action_hr_employee_loan_request(self):
        """ Opens a view to list all documents related to the current
         employee."""
        self.ensure_one()
        return {
            'name': _('Loan'),
            'domain': [('employee_id', '=', self.id)],
            'res_model': 'hr.loan',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Loan
                        </p>'''),
            'limit': 80,
            'context': "{'default_employee_id': %s}" % self.id
        }

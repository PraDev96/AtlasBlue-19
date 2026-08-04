# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class Loan(models.Model):
    _inherit = 'hr.loan'

    receiving_date = fields.Date(string="Receiving Date")
    payment_type = fields.Selection([('cash', 'Cash'), ('cheque', 'Cheque'), ('transaction', 'Transaction')], string="Payment of Method")
    identification_id = fields.Char(related='employee_id.identification_id', store=True)
    settlement_date = fields.Date(string="Settlement Date")

    attachment_number = fields.Integer(string="Number of Attachments", compute='_compute_attachment_number')

    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'hr.loan'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for loan in self:
            loan.attachment_number = attachment.get(loan.id, 0)

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'hr.loan'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'hr.loan', 'default_res_id': self.id}

        return res

    def action_reset_draft(self):
        for loan in self:
            if any(line.payslip_id for line in loan.loan_lines):
                raise ValidationError(_("You can not reset Loan, if installment link with payslip!"))

            loan.loan_lines.unlink()
            loan.write({'state': 'draft'})


class Employee(models.Model):
    _inherit = 'hr.employee'

    def action_hr_employee_loan(self):
        self.ensure_one()
        action = self.env.ref('ohrms_loan.act_hr_employee_loan_request').sudo().read()[0]
        action['domain'] = [('employee_id', '=', self.id)]
        action['context'] = {'default_employee_id': self.id}

        return action

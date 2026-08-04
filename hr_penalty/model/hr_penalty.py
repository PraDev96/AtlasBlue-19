# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class Penalty(models.Model):
    _name = 'hr.penalty'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Penalty"

    name = fields.Char(string="Name", readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, tracking=True)
    basic_salary = fields.Float(string="Basic Salary", readonly=True)
    date_penalty = fields.Date(string="Date of Penalty", tracking=True)
    detail = fields.Char(string="Penalty Details")
    decision = fields.Char(string="Penalty Decision")
    deducted_payslip = fields.Boolean(string="Payslip Deduction")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    amount = fields.Float(string="Amount", default=0.0, tracking=True)
    payslip_date = fields.Date(string="Payslip Date", tracking=True)
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
    warning_type = fields.Selection([
        ('written', 'Written Warning'), ('verbal', 'Verbal Warning'), ('investigation', 'Investigation'), ('final', 'Final Warning')], string="Warning Type", tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')], string="State", default='draft', tracking=True)
    joining_date = fields.Date(string="Joining Date")
    job_position_id = fields.Many2one('hr.job', string="Position")
    attachment_number = fields.Integer(string="Number of Attachments", compute='_compute_attachment_number')

    installment = fields.Integer(string="No Of Installments", default=1)
    # date = fields.Date(string="Date", default=fields.Date.today(), readonly=True)
    payment_date = fields.Date(string="Payslip Start Date", required=True, default=fields.Date.today())
    penalty_lines = fields.One2many('hr.penalty.installment.line', 'penalty_id', string="Penalty Line")

    total_amount = fields.Float(string="Total Amount", readonly=True, compute='_compute_penalty_amount')
    balance_amount = fields.Float(string="Balance Amount", compute='_compute_penalty_amount')
    total_paid_amount = fields.Float(string="Total Paid Amount", compute='_compute_penalty_amount')

    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'hr.penalty'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for penalty in self:
            penalty.attachment_number = attachment.get(penalty.id, 0)

    def _compute_penalty_amount(self):
        total_paid = 0.0
        for penalty in self:
            for line in penalty.penalty_lines:
                if line.paid:
                    total_paid += line.amount

            balance_amount = penalty.amount - total_paid
            self.total_amount = penalty.amount
            self.balance_amount = balance_amount
            self.total_paid_amount = total_paid

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res.update({
            'domain': [('res_model', '=', 'hr.penalty'), ('res_id', 'in', self.ids)],
            'context': {'default_res_model': 'hr.penalty', 'default_res_id': self.id},
        })

        return res

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.joining_date = False
        self.job_position_id = False
        self.basic_salary = 0.0
        if self.employee_id:
            self.joining_date = self.employee_id.date_joining
            self.job_position_id = self.employee_id.job_id.id
            self.basic_salary = self.employee_id.contract_id.wage

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update({'name': self.env['ir.sequence'].next_by_code('hr.penalty') or '/'})

        return super(Penalty, self).create(vals_list)

    def action_done(self):
        for penalty in self:
            if not penalty.penalty_lines:
                raise ValidationError(_("Please Compute installment"))
            else:
                penalty.write({'state': 'done'})

        return True

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_reset_draft(self):
        return self.write({'state': 'draft'})

    def compute_installment(self):
        for penalty in self:
            penalty.penalty_lines.unlink()
            date_start = datetime.strptime(str(penalty.payment_date), '%Y-%m-%d')
            amount = penalty.amount / penalty.installment
            for i in range(1, penalty.installment + 1):
                self.env['hr.penalty.installment.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': penalty.employee_id.id,
                    'penalty_id': penalty.id
                })
                date_start = date_start + relativedelta(months=1)

        return True


class PenaltyInstallmentLine(models.Model):
    _name = 'hr.penalty.installment.line'
    _description = 'Installment Line'

    date = fields.Date(string="Payment Date", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    amount = fields.Float(string="Amount", required=True)
    paid = fields.Boolean(string="Paid")
    penalty_id = fields.Many2one('hr.penalty', string="Penalty Ref.")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
    reference = fields.Char(string="Reference")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        PenaltyLine = self.env['hr.penalty.installment.line']
        for payslip in self:
            penalty_lines = PenaltyLine.search([
                ('employee_id', '=', payslip.employee_id.id), ('date', '>=', payslip.date_from), ('date', '<=', payslip.date_to), ('paid', '=', False)
            ])
            penalty_lines.write({'paid': True, 'payslip_id': payslip.id})

        return res

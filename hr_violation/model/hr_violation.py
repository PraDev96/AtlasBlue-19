# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class ViolationType(models.Model):
    _name = 'hr.violation.type'
    _description = "Violation Type"

    name = fields.Char(string="Name", required=True)


class Violation(models.Model):
    _name = 'hr.violation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Violation"

    def _default_employee(self):
        return self.env.user.employee_id

    name = fields.Char(string="Description", readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee)
    amount = fields.Float(string="Amount")
    basic_salary = fields.Float(string="Basic Salary", readonly=True)
    violation_type_id = fields.Many2one('hr.violation.type', string="Violation Type", required=True)
    violation_date = fields.Date(string="Violation Date", required=True)
    deducted_payslip = fields.Boolean(string="Payslip Deduction?")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),
    ], string="State", default='draft', required=True, copy=False)
    payslip_date = fields.Date(string="Payslip Date")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
    # violation_detail_id = fields.Many2one('violation.detail', string='Violation Detail')
    violation_detail = fields.Text(string="Violation Detail")
    joining_date = fields.Date(string="Joining Date")
    job_position_id = fields.Many2one('hr.job', string="Position")
    covered_up_by = fields.Selection([('employee', 'Employee'), ('company', 'Company')], string="Covered Up By", default='employee')
    attachment_number = fields.Integer(string="Number of Attachments", compute='_compute_attachment_number')

    installment = fields.Integer(string="No Of Installments", default=1)
    # date = fields.Date(string="Date", default=fields.Date.today(), readonly=True)
    payment_date = fields.Date(string="Payslip Start Date", required=True, default=fields.Date.today())
    violation_installment_lines = fields.One2many('hr.violation.installment.line', 'violation_id', string="Violation Installment Line")

    total_amount = fields.Float(string="Total Amount", readonly=True, compute='_compute_violation_amount')
    balance_amount = fields.Float(string="Balance Amount", compute='_compute_violation_amount')
    total_paid_amount = fields.Float(string="Total Paid Amount", compute='_compute_violation_amount')

    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'hr.violation'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for violation in self:
            violation.attachment_number = attachment.get(violation.id, 0)

    def _compute_violation_amount(self):
        total_paid = 0.0
        for violation in self:
            for line in violation.violation_installment_lines:
                if line.paid:
                    total_paid += line.amount

            balance_amount = violation.amount - total_paid
            self.total_amount = violation.amount
            self.balance_amount = balance_amount
            self.total_paid_amount = total_paid

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res.update({
            'domain': [('res_model', '=', 'hr.violation'), ('res_id', 'in', self.ids)],
            'context': {'default_res_model': 'hr.violation', 'default_res_id': self.id},
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
            vals.update({'name': self.env['ir.sequence'].next_by_code('hr.violation') or '/'})

        return super(Violation, self).create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirm'})
        return True

    def action_done(self):
        return self.write({'state': 'done'})

    def action_reset(self):
        return self.write({'state': 'draft'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def compute_installment(self):
        for violation in self:
            violation.violation_installment_lines.unlink()
            date_start = datetime.strptime(str(violation.payment_date), '%Y-%m-%d')
            amount = violation.amount / violation.installment
            for i in range(1, violation.installment + 1):
                self.env['hr.violation.installment.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': violation.employee_id.id,
                    'violation_id': violation.id
                })
                date_start = date_start + relativedelta(months=1)

        return True


class ViolationInstallmentLine(models.Model):
    _name = 'hr.violation.installment.line'
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    amount = fields.Float(string="Amount", required=True)
    paid = fields.Boolean(string="Paid")
    violation_id = fields.Many2one('hr.violation', string="Violation Ref.")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
    reference = fields.Char(string="Reference")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        ViolationInstallmentLine = self.env['hr.violation.installment.line']
        for payslip in self:
            violation_lines = ViolationInstallmentLine.search([
                ('employee_id', '=', payslip.employee_id.id),
                ('date', '>=', payslip.date_from),
                ('date', '<=', payslip.date_to),
                ('paid', '=', False)
            ])
            violation_lines.write({'paid': True, 'payslip_id': payslip.id})

        return res


class ViolationDetail(models.Model):
    _name = 'violation.detail'
    _description = "Violation Detail"

    name = fields.Char(string="Name", required=True)

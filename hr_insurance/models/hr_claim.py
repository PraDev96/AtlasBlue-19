# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class Claim(models.Model):
    _name = 'hr.claim'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "HR Claim"

    def _default_employee_id(self):
        employee_id = False
        if self.env.context.get('employee_id'):
            employee_id = self.env.context['employee_id']

        return employee_id

    def _get_default_currency(self):
        return self.env.company.currency_id.id

    name = fields.Char(string="Name", readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", readonly=True, default=_default_employee_id)
    amount = fields.Float(string="Amount", readonly=True)
    claim_date = fields.Date(string="Claim Date", required=True, readonly=True)
    accident_date = fields.Date(string="Accident Date", required=True, readonly=True)
    resume_work_date = fields.Date(string="Resume Work Date", readonly=True)
    insurance_company_id = fields.Many2one('res.partner', string="Insurance Company", readonly=True, domain="[('is_insurance_company', '=', True), ('parent_id', '=', False)]")
    claim_invoice_id = fields.Many2one('account.move', string="Claim Invoice", readonly=True, domain="[('move_type', '=', 'in_refund'), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),
    ], string="State", default='draft', required=True, copy=False)
    insurance_id = fields.Many2one('hr.insurance', string="Insurance")
    expense_ids = fields.One2many('hr.expense', 'claim_id', string="Expenses", readonly=True)
    claim_number = fields.Char(string="Claim Number", readonly=True)
    total_expense = fields.Float(string="Total Expense", compute="_compute_expense", store=True)
    currency_id = fields.Many2one('res.currency', store=True, readonly=True, string="Currency", default=_get_default_currency)
    claim_type_id = fields.Many2one('hr.claim.type', string="Claim Type")
    claim_payment_date = fields.Date(string="Claim Payment Date")
    confirm_date = fields.Datetime(string="Confirm Date", readonly=True, tracking=True)
    joining_date = fields.Date(string="Joining Date")
    job_position_id = fields.Many2one('hr.job', string="Position")
    attachment_number = fields.Integer(string="Number of Attachments", compute='_compute_attachment_number')

    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'hr.claim'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for claim in self:
            claim.attachment_number = attachment.get(claim.id, 0)

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'hr.claim'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'hr.claim', 'default_res_id': self.id}
        return res

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.joining_date = False
        self.job_position_id = False
        if self.employee_id:
            self.joining_date = self.employee_id.date_joining
            self.job_position_id = self.employee_id.job_id.id

    @api.depends('expense_ids.total_amount')
    def _compute_expense(self):
        for rec in self:
            rec.total_expense = sum(rec.expense_ids.mapped('total_amount'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update({'name': self.env['ir.sequence'].next_by_code('hr.claim') or '/'})

        return super(Claim, self).create(vals_list)

    def _prepare_invoice_vals(self):
        self.ensure_one()
        invoice_vals = {
            'type': 'out_invoice',
            'invoice_user_id': self.env.user.id,
            'partner_id': self.insurance_company_id.id,
            'fiscal_position_id': self.insurance_company_id.property_account_position_id.id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.insurance_company_id.property_payment_term_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'Claim' + ' - ' + self.name,
                    'quantity': 1.0,
                    'price_unit': self.amount,
                })
            ],
        }
        return invoice_vals

    def action_confirm(self):
        # AccountMove = self.env['account.move']
        # for rec in self:
        #     invoice_vals = self._prepare_invoice_vals()
        #     invoice = AccountMove.with_context(default_type='out_invoice').create(invoice_vals)
        #     invoice.post()
        #     self.write({'insurance_invoice_id': invoice.id, 'state': 'confirm'})
        self.write({'state': 'confirm', 'confirm_date': fields.Datetime.now()})
        return True

    def action_reset_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    def action_pending(self):
        self.write({'state': 'pending'})
        return True

    def action_done(self):
        for rec in self:
            if not rec.claim_invoice_id:
                raise ValidationError(_("You can not done claim until invoice attached!"))

            rec.write({'state': 'done'})
        return True


class ClaimType(models.Model):
    _name = 'hr.claim.type'
    _description = "Claim Type"

    name = fields.Char(string="Name", required=True)


class Expense(models.Model):
    _inherit = 'hr.expense'

    state = fields.Selection(
        selection=[
            ('draft', 'To Report'),
            ('reported', 'To Submit'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('done', 'Done'),
            ('refused', 'Refused')
        ],
        string="Status",
        compute='_compute_state', store=True, readonly=True,
        index=True,
        copy=False,
        default='draft',
    )

    @api.depends('sheet_id', 'sheet_id.account_move_ids', 'sheet_id.state')
    def _compute_state(self):
        for expense in self:
            if not expense.sheet_id:
                expense.state = 'draft'
            elif expense.sheet_id.state == 'draft':
                expense.state = 'reported'
            elif expense.sheet_id.state == 'cancel':
                expense.state = 'refused'
            elif expense.sheet_id.state in {'approve', 'post'}:
                expense.state = 'approved'
            elif not expense.sheet_id.account_move_ids:
                expense.state = 'submitted'
            else:
                expense.state = 'done'

    @api.model
    def _get_employee_id_domain(self):
        # res = [('id', '=', 0)]
        res = []  # Nothing accepted by domain, by default
        # if self.user_has_groups('hr_expense.group_hr_expense_user') or self.user_has_groups('account.group_account_user'):
        #     res = "['|', ('company_id', '=', False), ('company_id', '=', company_id)]"  # Then, domain accepts everything
        if self.user_has_groups('hr_expense.group_hr_expense_team_approver') and self.env.user.employee_ids:
            user = self.env.user
            employee = self.env.user.employee_id
            res = [
                '|', '|', '|',
                ('department_id.manager_id', '=', employee.id),
                ('parent_id', '=', employee.id),
                ('id', '=', employee.id),
                ('expense_manager_id', '=', user.id),
                '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id),
            ]
        elif self.env.user.employee_id:
            employee = self.env.user.employee_id
            res = [('id', '=', employee.id), '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id)]

        return res

    def _default_employee_id(self):
        employee_id = False
        if self.env.context.get('employee_id'):
            employee_id = self.env.context['employee_id']

        return employee_id

    employee_id = fields.Many2one(required=False, default=_default_employee_id)
    claim_id = fields.Many2one('hr.claim', string="Expense")
    requester_id = fields.Many2one('res.users', string="Requester")
    payment_date = fields.Date(string="Payment Date", default=fields.Date.context_today)

    @api.onchange('company_id')
    def onchange_expense_company_id(self):
        if self.env.context.get('employee_id'):
            self.employee_id = self.env.context['employee_id']

    def action_reset_draft(self):
        self.ensure_one()
        self.sheet_id.account_move_id.button_cancel()
        self.sheet_id.account_move_id.unlink()

        self.sheet_id.reset_expense_sheets()

        self.sheet_id.write({'state': 'draft'})
        self.sheet_id.unlink()
        return self.write({'state': 'draft'})

    def _prepare_move_values(self):
        self.ensure_one()
        result = super(Expense, self)._prepare_move_values()
        if self.sheet_id.employee_id.partner_id:
            result['partner_id'] = self.sheet_id.employee_id.partner_id.id

        return result


class AccountMove(models.Model):
    _inherit = 'account.move'

    employee_id = fields.Many2one('hr.employee', string="Employee")

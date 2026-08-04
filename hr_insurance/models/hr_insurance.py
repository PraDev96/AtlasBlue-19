# -*- coding: utf-8 -*-

import time
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class Insurance(models.Model):
    _name = 'hr.insurance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "HR Insurance"

    def _get_default_currency(self):
        return self.env.company.currency_id.id

    name = fields.Char(string="Name", readonly=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    insurance_company_id = fields.Many2one('res.partner', string="Insurance Company", required=True, domain="[('is_insurance_company', '=', True), ('parent_id', '=', False)]")
    amount = fields.Float(string="Amount", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", readonly=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, readonly=True)
    currency_id = fields.Many2one('res.currency', store=True, readonly=True, string="Currency", default=_get_default_currency)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')], string="State", default='draft', required=True)
    claim_id = fields.Many2one('hr.claim', string="Claim", readonly=True)
    invoice_ids = fields.Many2many('account.move', string="Insurance Invoices", domain="[('move_type', '=', 'in_invoice'), ('company_id', '=', company_id)]")
    claim_ids = fields.One2many('hr.claim', 'insurance_id', string="Claims")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Fleet")
    insurance_type = fields.Selection([
        ('fleet_vehicle', 'Fleet Vehicle'),
        ('employee', 'Employee'),
        ('sales', 'Sales')], string="Insurance Type", default='employee')
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    motor_vehicle_id = fields.Many2one('motor.vehicle', string="Customer Vehicle")
    transcation_date = fields.Date(string="Transaction Date", default=fields.Date.context_today)
    policy_number = fields.Char(string="Policy Number", copy=False)
    transcation_type_id = fields.Many2one('insurance.transcation.type', string="Type of Transaction")
    cancel_date = fields.Date(string="Cancellation Date")
    insurance_salary = fields.Char(string="Insurance Salary")
    birth_date = fields.Date(string="Date of Birth")
    civil_id = fields.Char(string="Civil Id")
    year = fields.Char(string="Year", default=lambda *a: time.strftime('%Y'))
    joining_date = fields.Date(string="Joining Date")
    job_position_id = fields.Many2one('hr.job', string="Position")
    work_permit_expiry = fields.Date(related='employee_id.work_permit_expiry', string="Work Permit Expiry")
    date_job_end = fields.Date(related='employee_id.date_job_end', string="Job End Date")
    chassis_number = fields.Char(string="Chassis Number", copy=False)

    @api.constrains('chassis_number', 'insurance_type')
    def _check_chassis_number(self):
        for insurance in self:
            if insurance.insurance_type == 'sales' and insurance.chassis_number:
                insurances = self.search([('chassis_number', '=', insurance.chassis_number), ('id', '!=', insurance.id)])
                if insurances:
                    raise ValidationError(_('For this Chassis Number %s already insurance exits!') % (insurance.chassis_number,))

    _sql_constraints = [('unique_policy_number', 'unique (policy_number)', 'Policy Number must be unique!')]

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.civil_id = False
        self.birth_date = False
        self.joining_date = False
        self.job_position_id = False
        if self.employee_id:
            self.birth_date = self.employee_id.birthday
            self.civil_id = self.employee_id.civil_id
            self.joining_date = self.employee_id.date_joining
            self.job_position_id = self.employee_id.job_id.id

    @api.onchange('insurance_type')
    def onchange_insurance_type(self):
        if self.insurance_type != 'sales':
            self.chassis_number = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update({'name': self.env['ir.sequence'].next_by_code('hr.insurance') or '/'})

        return super(Insurance, self).create(vals_list)

    def action_claim(self):
        # Claim = self.env['hr.claim']
        # for rec in self:
        #     claim = Claim.create({
        #         'employee_id': rec.employee_id.id,
        #         'amount': rec.amount,
        #         'claim_date': fields.Date.today(),
        #         'insurance_company_id': rec.insurance_company_id.id,
        #         'state': 'draft',
        #         'company_id': rec.company_id.id,
        #     })
        # 'claim_id': claim.id
        self.write({'state': 'done'})
        return True

    def action_cancel(self):
        return self.write({'state': 'cancel', 'cancel_date': fields.Date.today()})


class InsuranceTransactionType(models.Model):
    _name = 'insurance.transcation.type'
    _description = "Insurance Transaction Type"

    name = fields.Char(string="Name", required=True)
    insurance_count = fields.Integer(compute='_compute_insurance_count', string="Insurance Count")
    user_ids = fields.Many2many('res.users', string="Users")

    def _compute_insurance_count(self):
        insurance_data = self.env['hr.insurance'].read_group([('transcation_type_id', 'in', self.ids)], ['transcation_type_id'], ['transcation_type_id'])
        result = dict((data['transcation_type_id'][0], data['transcation_type_id_count']) for data in insurance_data)
        for transcation_type in self:
            transcation_type.insurance_count = result.get(transcation_type.id, 0)

    def open_insurance(self):
        ctx = dict(self._context)
        ctx.update({'search_default_transcation_type_id': self.id})
        action = self.env.ref("hr_insurance.action_hr_insurance").sudo().read()[0]

        return dict(action, context=ctx)

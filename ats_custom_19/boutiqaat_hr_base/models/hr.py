# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Employee(models.Model):
    _inherit = "hr.employee"

    display_name = fields.Char(string="Display Name", compute="_compute_display_name")
    job_pos_permit_id = fields.Many2one('hr.job', string="Position In Work Permit")
    social_media_account = fields.Char(string="Social Media Account")

    emp_asset_ids = fields.One2many("employee.asset", "employee_id", string="Assets")
    emp_asset_count = fields.Integer(string="Total Assets", compute="_compute_asset_count")

    passpory_history_ids = fields.One2many('passport.history', 'employee_id', string="Passport History")
    benefits_ids = fields.One2many('employee.benefits', 'employee_id', string="Benefits")
    exit_interview = fields.Char(string="Exit Interview")

    file_ids = fields.One2many('employee.document', 'employee_id', string="Files")
    file_count = fields.Integer(string="Total Files", compute="_compute_file_count")

    arabic_name = fields.Char(string="Arabic Name")
    section_id = fields.Many2one('hr.section', string="Section")
    work_address = fields.Char(string="Employee Work Address")
    private_address = fields.Char(string="Private Address")
    company_assets = fields.Char(string="Company Assets")
    certificate_level = fields.Char(string="Employee Certificate Level")
    grade_id = fields.Many2one('hr.grade', string="Grade")
    is_completed_hajj = fields.Boolean(string="Is Completed Hajj ?", readonly=True)
    sick_leave_days_in_cur_year = fields.Float(compute='_get_sick_leaves', string="Sick Leaves for Current Year")
    inv_discount_ids = fields.One2many("emp.discount", "employee_id", string="Invoice Discounts")

    bank_id = fields.Many2one("res.bank", string="Bank")
    bank_number = fields.Char(string="Bank Number")
    iban_number = fields.Char(string="IBAN")
    pay_through = fields.Selection([('bank', 'Bank'), ('cash', 'Cash'), ('other', 'Other')], default='bank', string="Pay Through")
    identification_id = fields.Char(string="Employee Number")

    # Inherited
    gender = fields.Selection(groups="")
    marital = fields.Selection(groups="")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            args += ['|', '|', ('identification_id', 'ilike', name), ('work_phone', 'ilike', name)]

        return super(Employee, self).name_search(name=name, args=args, operator=operator, limit=limit)

    @api.depends('identification_id', 'name')
    def _compute_display_name(self):
        for employee in self:
            if employee.identification_id:
                employee.display_name = _("[%s] %s", employee.identification_id, employee.name)
            else:
                employee.display_name = employee.name

    def _get_sick_leaves(self):
        HrLeave = self.env['hr.leave']
        sick_leave = self.env['hr.leave.type'].search([('leave_type', '=', 'sick')], limit=1)
        for emp in self:
            domain = [('holiday_status_id', '=', sick_leave.id), ('employee_id', '=', emp.id), ('state', '=', 'validate')]

            leaves = HrLeave.search(domain)
            total_days = 0
            if leaves:
                total_days = sum(leaves.mapped('number_of_days'))
            # for leave in leaves:
            #     total_days += (leave.request_date_to - leave.request_date_from).days + 1
            # total_days = sum(leave.number_of_days for leave in leaves)
            emp.sick_leave_days_in_cur_year = total_days

    def _compute_file_count(self):
        for rec in self:
            rec.file_count = len(rec.file_ids.ids)

    def _compute_asset_count(self):
        for rec in self:
            rec.emp_asset_count = len(rec.emp_asset_ids.ids)

    def get_inv_discount(self, payslip):
        sql = """SELECT sum(inv_amount) FROM emp_discount WHERE employee_id = %s AND date_payslip BETWEEN %s AND %s"""
        self.env.cr.execute(sql, (self.id, payslip.date_from, payslip.date_to))
        result = self.env.cr.fetchone()
        if result:
            return result[0] or 0

        return 0

    def get_loan_deduction(self, date_from, date_to):
        sql = """
            SELECT sum(line.amount) FROM hr_loan_line AS line LEFT JOIN hr_loan AS loan ON loan.id = line.loan_id WHERE loan.employee_id = %s AND line.date BETWEEN %s AND %s
        """
        self.env.cr.execute(sql, (self.id, date_from, date_to))
        result = self.env.cr.fetchone()

        return result and result[0] or 0

    def get_loan_amount(self, payslip):
        return self.get_loan_deduction(payslip.date_from, payslip.date_to)

    def get_last_holiday(self, date_payslip):
        leave = self.env['hr.leave'].search(
            [('employee_id', '=', self.id), ('state', '=', 'validate'), ('date_from', '<', date_payslip)], order='request_date_from desc', limit=1
        )

        return leave


class HrSection(models.Model):
    _name = 'hr.section'
    _description = 'Section'

    name = fields.Char(string="Section", required=True)


class HrGrade(models.Model):
    _name = 'hr.grade'
    _description = 'Grade'

    name = fields.Char(string="Grade", required=True)


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    arabic_name = fields.Char(string="Arabic Name")


class HrJob(models.Model):
    _inherit = 'hr.job'

    arabic_name = fields.Char(string="Arabic Name")


class Country(models.Model):
    _inherit = 'res.country'

    arabic_name = fields.Char(string="Arabic Name")


class Company(models.Model):
    _inherit = 'res.company'

    arabic_name = fields.Char(string="Arabic Name")
    font = fields.Selection(selection_add=[('Times New Roman', 'Times New Roman')], default="Times New Roman")


class Bank(models.Model):
    _inherit = 'res.bank'

    arabic_name = fields.Char(string="Arabic Name")


class HrTitle(models.Model):
    _name = 'hr.title'
    _description = "HR Title"

    name = fields.Char(string="Name", required=True)


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    job_pos_permit_id = fields.Many2one('hr.job', string="Position In Work Permit", readonly=True)
    social_media_account = fields.Char(string="Social Media Account", readonly=True)

    emp_asset_ids = fields.One2many("employee.asset", "employee_id", string="Assets", readonly=True)
    emp_asset_count = fields.Integer(string="Total Assets", compute="_compute_asset_count", readonly=True)

    passpory_history_ids = fields.One2many('passport.history', 'employee_id', string="Passport History", readonly=True)
    benefits_ids = fields.One2many('employee.benefits', 'employee_id', string="Benefits", readonly=True)
    exit_interview = fields.Char(string="Exit Interview", readonly=True)

    file_ids = fields.One2many('employee.document', 'employee_id', string="Files", readonly=True)
    file_count = fields.Integer(string="Total Files", compute="_compute_file_count", readonly=True)

    arabic_name = fields.Char(string="Arabic Name", readonly=True)
    section_id = fields.Many2one('hr.section', string="Section", readonly=True)
    work_address = fields.Char(string="Employee Work Address", readonly=True)
    private_address = fields.Char(string="Private Address", readonly=True)
    company_assets = fields.Char(string="Company Assets", readonly=True)
    certificate_level = fields.Char(string="Employee Certificate Level", readonly=True)
    grade_id = fields.Many2one('hr.grade', string="Grade", readonly=True)
    is_completed_hajj = fields.Boolean(string="Is Completed Hajj ?", readonly=True)
    sick_leave_days_in_cur_year = fields.Float(compute='_get_sick_leaves', string="Sick Leaves for Current Year")
    inv_discount_ids = fields.One2many("emp.discount", "employee_id", string="Invoice Discounts", readonly=True)

    bank_id = fields.Many2one("res.bank", string="Bank")
    bank_number = fields.Char(string="Bank Number")
    iban_number = fields.Char(string="IBAN")
    pay_through = fields.Selection([('bank', 'Bank'), ('cash', 'Cash'), ('other', 'Other')], default='bank', string="Pay Through")
    identification_id = fields.Char(string="Employee Number")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string="Gender", default="male", readonly=True)
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')], string="Marital Status", default='single', readonly=True)

# -*- coding: utf-8 -*-

import logging
import calendar
from odoo.exceptions import UserError
from odoo import models, fields, _, api
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class VisaType(models.Model):
    _name = 'visa.type'
    _description = "Visa Type"

    name = fields.Char(string="Name", required=True)


class Employee(models.Model):
    _inherit = "hr.employee"

    allow_over_time = fields.Float(string="Allowed Over Time", required=True, default=0.0, tracking=True)
    kuwait_phone_number = fields.Char(string="Kuwait Phone Number")
    visa_type_id = fields.Many2one('visa.type', string="Visa Type")
    non_resident = fields.Boolean(string="Non Resident?")

    # health_card_id = fields.Binary("Health Card Copy")
    health_card_start_date = fields.Date(string="Health Card Start Date", tracking=True)
    health_card_end_date = fields.Date(string="Health Card End Date", tracking=True)
    visa_issue_date = fields.Date(string="Visa Issue Date", tracking=True)
    bank_card_start_date = fields.Date(string="Bank Card Start Date", tracking=True)
    bank_card_expiry_date = fields.Date(string="Bank Card End Date", tracking=True)
    emp_code = fields.Char(string="Employee Code", tracking=True)
    license_expiry_date = fields.Date(string="License Expiry Date", tracking=True)
    civil_serial_number = fields.Char(string="Civil Serial Number")
    article_resideny_id = fields.Many2one('article.residency', string="Article Residency")
    residency_start_date = fields.Date(string="Residency Start Date")
    finger_print_date = fields.Date(string="Finger Print Date")
    passport_issue_country_id = fields.Many2one('res.country', string="Passport Issue Country")
    certificate_type_id = fields.Many2one('certificate.type', string="Certificate Type")
    address_home = fields.Char(string="Address")

    current_position_id = fields.Many2one('hr.job', string="Current Position in Project")
    medical_date = fields.Date(string="Medical Date")
    kuwait_entry_date = fields.Date(string="Kuwait Entry Date")
    employee_date_history_ids = fields.One2many('employee.date.history', 'employee_id', string="Employee Date History")
    employee_note_ids = fields.One2many('employee.note', 'employee_id', string="Employee Notes")
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicles")
    employee_state = fields.Selection([
        ('running', 'Running'),
        ('dismmis_absent', 'Dismiss for Absent'),
        ('dismmis_leave_absent', 'Dismiss for Leave Absent'),
        ('manpower_case', 'Manpower Case'),
        ('moi_case', 'MOI Case'),
        ('manpower_complain', 'Manpower Complain'),
        ('regination', 'Regination'),
        ('termination', 'Termination'),
        ('transfer_work_permit', 'Transfer Work Permit'),
        ('transfer_another_company', 'Transfer to Another Company'),
        ('death', 'Death'),
        ('cancel', 'Cancelled'),
        ('leave_country', 'Leaves the Country'),
        ('bring_transfer', 'Bring Transfer'),
        ('receive_transfer', 'Receive Transfer'),
        ('residency_cancelled_law', 'Residency Cancelled by Law'),
        ('residency_cancelled_letter', 'Work Permit Cancel by Letter'),
    ], string="Employee State")
    is_additional_leave_allocate = fields.Boolean(string="Is Additional Leave Allocation?")
    vaccination_date = fields.Date(string="Vaccination Date", copy=False)
    plan_to_change_car = fields.Boolean(string="Plan To Change Car", default=False)
    histroy_project_employee_ids = fields.One2many('history.project.employee', 'employee_id', string="History")

    eos_additional_work_days = fields.Float(string="Additional Work Days", default=0.0)
    eos_opening_balance_days = fields.Float(string="EOS Opening Balance Days", digits=(16, 4))
    employee_address = fields.Char(string="Employee Address")

    def _compute_eos_days(self):
        # Unpaid Leave
        unpaid_status = self.env.ref('hr_holidays.holiday_status_unpaid')
        for rec in self:
            holidays = self.env['hr.leave'].search([('employee_id', '=', rec.id), ('state', '=', 'validate'), ('holiday_status_id', '=', unpaid_status.id)])
            rec.eos_tot_leaves = tot_leaves = sum(holidays.mapped('number_of_days'))
            tot_year_days = tot_days = tdiff_year = 0
            if rec.work_start_issue_date:
                end_date = rec.date_job_end or fields.Date.today()
                diff_days = end_date - rec.work_start_issue_date
                tot_year_days = diff_days.days
                tot_days = tot_year_days - tot_leaves
                tdiff_year = tot_days / 365

            rec.eos_tot_year_days = tot_year_days
            rec.eos_net_days = tot_days
            rec.eos_net_year = tdiff_year

    def generate_eos_entries(self):
        self.ensure_one()
        # contracts = self.env['hr.contract'].search([('employee_id', '=', self.id)])
        contract = self.contract_id
        if not contract:
            raise UserError(_("Current Contract Not Found."))

        if not self.work_start_issue_date:
            raise UserError(_("Joining Date Missing."))

        curr_date = self.work_start_issue_date
        end_date = self.date_job_end or fields.Date.today()

        while curr_date < end_date:
            contract.generate_month_eos(curr_date, True, False)
            curr_date = curr_date + relativedelta(months=1)

    @api.depends('date_job_end', 'job_end_reason', 'work_start_issue_date')
    def _compute_eos_deserved_amount(self):
        for emp in self:
            eos_deserved = eos_amount = 0
            if all([emp.date_job_end, emp.work_start_issue_date, emp.job_end_reason]) or emp.job_end_reason in ('resign', 'dismissed', 'terminate'):
                eos_deserved, eos_amount = emp._calculate_eos_amount()

            emp.eos_deserved = eos_deserved
            emp.eos_amount = eos_amount

    def _calculate_eos_amount(self):
        self.ensure_one()
        eos_amount = eos_deserved = 0
        contract = self.contract_id
        if contract:
            monthly_salary = contract.get_eos_allowance()
            eos_deserved = self.get_eos_deserved(contract, self.eos_net_year)
            eos_amount = min(eos_deserved * monthly_salary / (contract.month_days or 26), monthly_salary * 18)

        return eos_deserved, eos_amount

    def get_eos_deserved(self, contract, tdiff_year, job_end_reason=None):
        job_end_reason = job_end_reason or self.job_end_reason
        eos_deserved = final_eos = 0
        after_5 = contract.eos_after_5_year_days * 12
        before_5 = contract.eos_bf_5_year_days * 12
        if tdiff_year >= 5:
            after5_year = tdiff_year - 5
            eos_deserved = (after_5 * after5_year) + (before_5 * 5)
        elif tdiff_year >= 0:
            eos_deserved = before_5 * tdiff_year

        # Max 18 Months EOS Applicable
        eos_deserved += self.eos_opening_balance_days
        eos_deserved = min(eos_deserved, (18 * contract.month_days))

        if self.job_end_reason in ['resign', 'dismissed']:
            if tdiff_year >= 10:
                final_eos = eos_deserved
            elif tdiff_year >= 5:
                final_eos = eos_deserved * 0.6667
            elif tdiff_year >= 3:
                final_eos = eos_deserved * 0.5

            # if tdiff_year >= 10:
            #     final_eos = eos_deserved
            # elif tdiff_year >= 5:
            #     final_eos = eos_deserved * 0.6667
            # elif tdiff_year >= 3:
            #     final_eos = eos_deserved * 0.5
        elif job_end_reason == 'terminate':
            final_eos = eos_deserved

        return round(final_eos, 4)

    def get_eos_report_details(self):
        detailed_result = super().get_eos_report_details()
        Leave = self.env['hr.leave.report']
        LeaveType = self.env['hr.leave.type']
        holiday_status = LeaveType.search([('code', '=', 'ANNUAL')])
        diff_period = relativedelta(self.date_job_end, self.work_start_issue_date)
        annual_leaves = Leave.search([('employee_id', '=', self.id), ('holiday_status_id', 'in', holiday_status.ids), ('state', '=', 'validate')])
        annual_bal = sum(annual_leaves.mapped('number_of_days'))
        eos_opening_balance_days = 0.0

        today = fields.Date.today()
        if self.date_job_end:
            worked_days = (self.date_job_end - today).days
            if worked_days <= 0.0:
                worked_days = 0.0

            contracts = self._get_contracts(today, today, states=['open', 'close'])
            if contracts:
                working_days = 0.0
                allocation_value = contracts[0].leave_allocation
                allocation_type = contracts[0].allocation_type

                if allocation_type == 'month':
                    month_days = calendar.monthrange(self.date_job_end.year, self.date_job_end.month)[1]
                    working_days = worked_days / month_days
                elif allocation_type == 'week':
                    working_days = worked_days / 7
                elif allocation_type == 'day':
                    working_days = worked_days

                eos_opening_balance_days = self.eos_opening_balance_days
                # working_days += eos_opening_balance_days

                working_days_balance = allocation_value * working_days
                annual_bal += working_days_balance

        detailed_result.update({
            'diff_period': diff_period,
            'leave_bal': round(annual_bal, 2),
            'eos_opening_balance_days': eos_opening_balance_days
        })
        return detailed_result

    def create_employee_date(self, vals):
        EmployeeDateHistory = self.env['employee.date.history']
        EmployeeDateHistory.create(vals)

    def get_lang_format(self):
        lang_code = self.env.user.lang or 'en_US'
        return self.env['res.lang']._lang_get(lang_code).date_format

    def get_date_format(self, dt, date_format=False):
        if not date_format:
            date_format = self.get_lang_format()

        dt = fields.Date.from_string(dt)
        return dt.strftime(date_format) if dt else ''

    def check_employee_val(self, vals):
        if vals.get('job_id'):
            job_position = self.env['hr.job'].browse(vals['job_id'])
            self.create_employee_date({
                'name': 'Job Position',
                'from_value': self.job_id.name,
                'to_value': job_position.name,
                'employee_id': self.id,
            })

        if vals.get('residency_start_date'):
            self.create_employee_date({
                'name': 'Residency Start Date',
                'from_value': self.get_date_format(self.residency_start_date),
                'to_value': self.get_date_format(vals['residency_start_date']),
                'employee_id': self.id,
            })

        if vals.get('residency_expiry_date'):
            self.create_employee_date({
                'name': 'Residency Expiry Date',
                'from_value': self.get_date_format(self.residency_expiry_date),
                'to_value': self.get_date_format(vals['residency_expiry_date']),
                'employee_id': self.id,
            })

        if vals.get('civil_end_date'):
            self.create_employee_date({
                'name': 'Civil End Date',
                'from_value': self.get_date_format(self.civil_end_date),
                'to_value': vals['civil_end_date'],
                'employee_id': self.id,
            })

        if vals.get('work_permit_expiry'):
            self.create_employee_date({
                'name': 'Work Permit Expiry',
                'from_value': self.get_date_format(self.work_permit_expiry),
                'to_value': self.get_date_format(vals['work_permit_expiry']),
                'employee_id': self.id,
            })

        if vals.get('visa_expiry'):
            self.create_employee_date({
                'name': 'Visa Expiry',
                'from_value': self.get_date_format(self.visa_expiry),
                'to_value': self.get_date_format(vals['visa_expiry']),
                'employee_id': self.id,
            })

        if vals.get('visa_issue_date'):
            self.create_employee_date({
                'name': 'Visa Issue Date',
                'from_value': self.get_date_format(self.visa_issue_date),
                'to_value': self.get_date_format(vals['visa_issue_date']),
                'employee_id': self.id,
            })

        if vals.get('vaccination_date'):
            self.create_employee_date({
                'name': 'Vaccination Date',
                'from_value': self.get_date_format(self.vaccination_date),
                'to_value': self.get_date_format(vals['vaccination_date']),
                'employee_id': self.id,
            })

        if vals.get('finger_print_date'):
            self.create_employee_date({
                'name': 'Finger Print Date',
                'from_value': self.get_date_format(self.finger_print_date),
                'to_value': self.get_date_format(vals['finger_print_date']),
                'employee_id': self.id,
            })

        if vals.get('bank_card_start_date'):
            self.create_employee_date({
                'name': 'Bank Card Start Date',
                'from_value': self.get_date_format(self.bank_card_start_date),
                'to_value': self.get_date_format(vals['bank_card_start_date']),
                'employee_id': self.id,
            })

        if vals.get('bank_card_expiry_date'):
            self.create_employee_date({
                'name': 'Bank Card End Date',
                'from_value': self.get_date_format(self.bank_card_expiry_date),
                'to_value': self.get_date_format(vals['bank_card_expiry_date']),
                'employee_id': self.id,
            })

        if vals.get('passport_start_date'):
            self.create_employee_date({
                'name': 'Passport Start Date',
                'from_value': self.get_date_format(self.passport_start_date),
                'to_value': self.get_date_format(vals['passport_start_date']),
                'employee_id': self.id,
            })

        if vals.get('passport_end_date'):
            self.create_employee_date({
                'name': 'Passport End Date',
                'from_value': self.get_date_format(self.passport_end_date),
                'to_value': self.get_date_format(vals['passport_end_date']),
                'employee_id': self.id,
            })

        if vals.get('birthday'):
            self.create_employee_date({
                'name': 'Date of Birth',
                'from_value': self.get_date_format(self.birthday),
                'to_value': self.get_date_format(vals['birthday']),
                'employee_id': self.id,
            })

        if vals.get('article_resideny_id'):
            article_residency = self.env['article.residency'].browse(vals['article_resideny_id'])
            self.create_employee_date({
                'name': 'Article Residency',
                'from_value': self.article_resideny_id.name,
                'to_value': article_residency.name,
                'employee_id': self.id,
            })

        if vals.get('passport_id'):
            self.create_employee_date({
                'name': 'Passport No',
                'from_value': self.passport_id,
                'to_value': vals['passport_id'],
                'employee_id': self.id,
            })

        if vals.get('vaccination_date'):
            self.create_employee_date({
                'name': 'Vaccination Date',
                'from_value': self.get_date_format(self.vaccination_date),
                'to_value': self.get_date_format(vals['vaccination_date']),
                'employee_id': self.id,
            })

        if vals.get('employee_state'):
            employee_state = {
                'running': 'Running',
                'dismmis_absent': 'Dismiss for Absent',
                'dismmis_leave_absent': 'Dismiss for Leave Absent',
                'manpower_case': 'Manpower Case',
                'moi_case': 'MOI Case',
                'manpower_complain': 'Manpower Complain',
                'regination': 'Regination',
                'termination': 'Termination',
                'transfer_work_permit': 'Transfer Work Permit',
                'transfer_another_company': 'Transfer to Another Company',
                'death': 'Death',
                'cancel': 'Cancelled',
                'leave_country': 'Leaves the Country',
                'bring_transfer': 'Bring Transfer',
                'receive_transfer': 'Receive Transfer',
                'residency_cancelled_law': 'Residency Cancelled by Law',
                'residency_cancelled_letter': 'Work Permit Cancel by Letter',
            }
            self.create_employee_date({
                'name': 'Employee State',
                'from_value': employee_state[self.employee_state] if self.employee_state else '',
                'to_value': employee_state[vals['employee_state']],
                'employee_id': self.id,
            })

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            result = super(Employee, self).create([vals])
            result.check_employee_val(vals)

        return result

    def write(self, vals):
        for employee in self:
            employee.check_employee_val(vals)

        return super(Employee, self).write(vals)

    @api.onchange('iban_number')
    def onchange_iban_number(self):
        self.iban_no = False
        if self.iban_number:
            self.iban_no = self.iban_number

    @api.onchange('country_id')
    def onchange_country_id(self):
        self.passport_country_id = False
        if self.country_id:
            self.passport_country_id = self.country_id

    @api.onchange('job_id')
    def onchange_job(self):
        self.current_position_id = False
        if self.job_id:
            self.current_position_id = self.job_id

    def get_pay_amount(self, payslip, full_amount, qty, by_days=True):
        if qty == 0:
            return 0

        # calendar = payslip.contract_id.resource_calendar_id
        # date_from = payslip.date_from
        # date_to = payslip.date_to
        # is_from_mid = False

        # employee = payslip.contract_id.employee_id

        # if employee.date_joining and employee.date_joining >= payslip.date_from and employee.date_joining <= payslip.date_to:
        #     date_from = employee.date_joining
        #     is_from_mid = True
        # if employee.date_job_end and employee.date_job_end >= payslip.date_from and employee.date_job_end <= payslip.date_to:
        #     date_to = employee.date_job_end
        #     is_from_mid = True

        # day_from = datetime.combine(date_from, time.min)
        # day_to = datetime.combine(date_to, time.max)

        # worked = calendar.get_work_duration_data(day_from, day_to)
        # days = worked['days']
        # hours = worked['hours']

        if by_days:
            working_units = payslip.countable_working_days
            actual_units = payslip.contract_id.month_days or 26
            # if is_from_mid:
            #     actual_units = days
        else:
            working_units = payslip.countable_working_hours
            actual_units = payslip.contract_id.tot_monthly_hours or 208
            # if is_from_mid:
            #     actual_units = hours

        if qty > actual_units:
            countable_units = actual_units
        else:
            countable_units = qty

        per_unit = full_amount / actual_units
        _logger.info("\n\nPer Unit :: Compute :: %s :: %s %s %s %s %s", by_days, working_units, actual_units, qty, countable_units, per_unit)

        return per_unit * countable_units

    def get_pay_amount_kuwait_payroll(self, payslip, full_amount, qty, by_days=True):
        if qty == 0:
            return 0

        # calendar = payslip.contract_id.resource_calendar_id
        # date_from = payslip.date_from
        # date_to = payslip.date_to
        is_from_mid = False

        employee = payslip.contract_id.employee_id

        if employee.date_joining and employee.date_joining >= payslip.date_from and employee.date_joining <= payslip.date_to:
            # date_from = employee.date_joining
            is_from_mid = True
        if employee.date_job_end and employee.date_job_end >= payslip.date_from and employee.date_job_end <= payslip.date_to:
            # date_to = employee.date_job_end
            is_from_mid = True

        # day_from = datetime.combine(date_from, time.min)
        # day_to = datetime.combine(date_to, time.max)

        # worked = calendar.get_work_duration_data(day_from, day_to)
        # days = worked['days']
        # hours = worked['hours']

        if by_days:
            working_units = payslip.calendar_working_days
            # actual_units = payslip.month_days or 26
            actual_units = payslip.contract_id.month_days or 26
            # if is_from_mid:
            #     actual_units = days
        else:
            working_units = payslip.calendar_working_hours
            # actual_units = payslip.contract_id.tot_monthly_hours or 208
            actual_units = payslip.contract_id.tot_monthly_hours or 208
            # if is_from_mid:
            #     actual_units = hours

        # leave_lines = payslip.worked_days_line_ids.filtered(lambda r: r.code == "LEAVE90")
        # leave_days_qty = sum(leave_lines.mapped('number_of_days'))

        # if is_from_mid:
        #     countable_units = qty
        # else:
        #     countable_units = actual_units - (working_units - qty)

        countable_units = qty
        per_unit = full_amount / actual_units
        _logger.info("\n\nPer Unit :: Compute :: %s :: %s %s %s %s %s",  by_days, working_units, actual_units, qty, countable_units, per_unit)

        return per_unit * countable_units


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    license_expiry_date = fields.Date(string="License Expiry Date")
    eos_opening_balance_days = fields.Float(string="EOS Opening Balance Days", digits=(16, 4))

    kuwait_phone_number = fields.Char(string="Kuwait Phone Number")
    visa_type_id = fields.Many2one('visa.type', string="Visa Type")
    non_resident = fields.Boolean(string="Non Resident?")

    # health_card_id = fields.Binary("Health Card Copy")
    health_card_start_date = fields.Date(string="Health Card Start Date")
    health_card_end_date = fields.Date(string="Health Card End Date")
    visa_issue_date = fields.Date(string="Visa Issue Date")
    bank_card_start_date = fields.Date(string="Bank Card Start Date")
    bank_card_expiry_date = fields.Date(string="Bank Card End Date")
    emp_code = fields.Char(string="Employee Code")

    civil_serial_number = fields.Char(string="Civil Serial Number")
    article_resideny_id = fields.Many2one('article.residency', string="Article Residency")
    residency_start_date = fields.Date(string="Residency Start Date")
    finger_print_date = fields.Date(string="Finger Print Date")
    passport_issue_country_id = fields.Many2one('res.country', string="Passport Issue Country")
    certificate_type_id = fields.Many2one('certificate.type', string="Certificate Type")
    address_home = fields.Char(string="Address")

    current_position_id = fields.Many2one('hr.job', string="Current Position in Project")
    medical_date = fields.Date(string="Medical Date")
    kuwait_entry_date = fields.Date(string="Kuwait Entry Date")

    employee_state = fields.Selection([
        ('running', 'Running'),
        ('dismmis_absent', 'Dismiss for Absent'),
        ('dismmis_leave_absent', 'Dismiss for Leave Absent'),
        ('manpower_case', 'Manpower Case'),
        ('moi_case', 'MOI Case'),
        ('manpower_complain', 'Manpower Complain'),
        ('regination', 'Regination'),
        ('termination', 'Termination'),
        ('transfer_work_permit', 'Transfer Work Permit'),
        ('transfer_another_company', 'Transfer to Another Company'),
        ('death', 'Death'),
        ('cancel', 'Cancelled'),
        ('leave_country', 'Leaves the Country'),
        ('bring_transfer', 'Bring Transfer'),
        ('receive_transfer', 'Receive Transfer'),
        ('residency_cancelled_law', 'Residency Cancelled by Law'),
        ('residency_cancelled_letter', 'Work Permit Cancel by Letter'),
    ], string="Employee State")
    is_additional_leave_allocate = fields.Boolean(string="Is Additional Leave Allocation?")
    vaccination_date = fields.Date(string="Vaccination Date")
    plan_to_change_car = fields.Boolean(string="Plan To Change Car", default=False)
    allow_over_time = fields.Float(string="Allowed Over Time", required=True, default=0.0)
    eos_additional_work_days = fields.Float(string="Additional Work Days", default=0.0)
    employee_address = fields.Char(string="Employee Address")


class ArticleResidency(models.Model):
    _name = 'article.residency'
    _description = "Article Residency"

    name = fields.Char(string="Name", required=True)


class CertificateType(models.Model):
    _name = 'certificate.type'
    _description = "Certificate Type"

    name = fields.Char(string="Name", required=True)


class EmployeeDateHistory(models.Model):
    _name = 'employee.date.history'
    _description = "Employee Date History"
    _order = 'write_date desc'

    name = fields.Char(string="Field")
    from_value = fields.Char(string="From Value")
    to_value = fields.Char(string="To Value")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user)


class EmployeeNote(models.Model):
    _name = 'employee.note'
    _description = "Employee Note"

    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")


class EmployeeAsset(models.Model):
    _name = 'employee.asset'
    _inherit = ['employee.asset', 'mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('employee.asset.type', string="Asset Name", required=True)
    date_return = fields.Date(string="Date Return")
    detail_info = fields.Text(string="Asset Detail")
    asset_category_id = fields.Many2one('employee.asset.category', string="Asset Category")
    date_assigned = fields.Date()
    asset_fuel_card_no_id = fields.Many2one('asset.fuel.card.no', string="Asset No")
    asset_service_no_id = fields.Many2one('asset.service.no', string="Asset Service No")

    asset_number_id = fields.Many2one('asset.number', string="Asset Number")
    asset_condition_id = fields.Many2one('asset.condition', string="Asset Condition")

    expiry_date = fields.Date(string="Expiry Date")
    joining_date = fields.Date(string="Joining Date")
    job_position_id = fields.Many2one('hr.job', string="Position")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)

    attachment_number = fields.Integer(string="Number of Attachments", compute='_compute_attachment_number')

    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'employee.asset'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for emp_asset in self:
            emp_asset.attachment_number = attachment.get(emp_asset.id, 0)

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'employee.asset'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'employee.asset', 'default_res_id': self.id}

        return res

    def action_return(self):
        self.write({'date_return': fields.Date.today()})
        return True

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.joining_date = False
        self.job_position_id = False
        if self.employee_id:
            self.joining_date = self.employee_id.date_joining
            self.job_position_id = self.employee_id.job_id.id


class EmployeeAssetType(models.Model):
    _name = 'employee.asset.type'
    _description = "Asset Type"

    name = fields.Char(string="Name", required=True)
    employee_asset_count = fields.Integer(compute='_compute_employee_asset_count', string="Employee Asset Count")

    def _compute_employee_asset_count(self):
        asset_data = self.env['employee.asset'].read_group([('name', 'in', self.ids)], ['name'], ['name'])
        result = dict((data['name'][0], data['name_count']) for data in asset_data)
        for asset in self:
            asset.employee_asset_count = result.get(asset.id, 0)

    def open_employee_asset(self):
        return self.create({'name': self.name})


class EmployeeAssetCategory(models.Model):
    _name = 'employee.asset.category'
    _description = "Asset Category"

    name = fields.Char(string="Name", required=True)


class AssetFuelCardNo(models.Model):
    _name = 'asset.fuel.card.no'
    _description = "Assets Fuel Card No"

    name = fields.Char(string="Name", required=True)


class AssetServiceNo(models.Model):
    _name = 'asset.service.no'
    _description = "Assets Service No"

    name = fields.Char(string="Name", required=True)


class AssetNumber(models.Model):
    _name = 'asset.number'
    _description = "Assets Number"

    name = fields.Char(string="Name", required=True)


class AssetCondition(models.Model):
    _name = 'asset.condition'
    _description = "Assets Condition"

    name = fields.Char(string="Name", required=True)


class HistoryProjectEmployee(models.Model):
    _name = 'history.project.employee'
    _rec_name = 'employee_id'
    _description = "History Project Employee"

    project_id = fields.Many2one('project.project', string="Project")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    employee_id = fields.Many2one('hr.employee', string="Employee")


class HistoryEmployeeVehicle(models.Model):
    _name = 'history.employee.vehicle'
    _description = "History Employee Vehicle"
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    fleet_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    from_date = fields.Datetime(string="From Date")
    to_date = fields.Datetime(string="To Date")


class Contract(models.Model):
    _inherit = 'hr.contract'

    ticket_amount = fields.Float(compute='_compute_ticket_amount', digits=(16, 2), string="Ticket Amount", store=True)
    ticket_per_month = fields.Float(string="Ticket per Month", digits=(16, 2), tracking=True)
    last_ticket_date = fields.Date(string="Last Ticket Date")
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string="Job Position", store=True)
    cost_per_hour = fields.Float(string="Cost per Hour")

    housing_allowance = fields.Monetary(tracking=True)
    transport_allowance = fields.Monetary(tracking=True)
    mobile_allowance = fields.Monetary(tracking=True)
    meal_allowance = fields.Monetary(tracking=True)
    motor_vehicle_allowance = fields.Monetary(tracking=True)
    driver_fuel_allowance = fields.Monetary(tracking=True)
    books_allowance = fields.Monetary(tracking=True)
    special_other_allowance = fields.Monetary(tracking=True)
    staff_discount = fields.Float(tracking=True)
    staff_max_discount = fields.Monetary(tracking=True)
    pf_allowance = fields.Monetary(tracking=True)
    night_shift_allowance = fields.Monetary(tracking=True)
    commission = fields.Monetary(tracking=True)

    @api.depends('ticket_per_month', 'date_start', 'date_end', 'last_ticket_date')
    def _compute_ticket_amount(self):
        for contract in self:
            ticket_amount = 0.0
            date_start = contract.date_start
            if contract.last_ticket_date:
                date_start = contract.last_ticket_date

            if contract.ticket_per_month and date_start:
                date_end = fields.Date.today()
                if contract.date_end:
                    date_end = contract.date_end

                diff = relativedelta(date_end, date_start)
                months = diff.months + (diff.years * 12) + 1
                ticket_amount = months * contract.ticket_per_month

            contract.ticket_amount = ticket_amount

    def _allocate_month_eos(self, month_date, payslip_id=None):
        self.ensure_one()
        emp = self.employee_id
        eos = EndOfService = self.env['hr.employee.eos']
        if emp.work_start_issue_date:
            eos_net_year = ((month_date - emp.work_start_issue_date).days - emp.eos_tot_leaves) / 365
            eos_days = self.eos_after_5_year_days if eos_net_year > 5 else self.eos_bf_5_year_days
            eos = EndOfService.create({
                'employee_id': emp.id,
                'eos_days_in_month': eos_days,
                'allocated_for_month': month_date,
                'eos_amount': self.get_per_day_salary() * eos_days,
                'payslip_id': payslip_id,
            })

        return eos

    def get_leave_salary(self, with_alw=True, with_wage=True):
        salary = self.get_eos_allowance(with_alw, with_wage)
        return salary

    def get_eos_allowance(self, with_alw=True, with_wage=True):
        tot = 0
        if with_alw:
            tot += self.housing_allowance + \
                   self.special_other_allowance
        if with_wage:
            tot += self.wage
        return tot

    @api.depends('wage', 'housing_allowance', 'transport_allowance', 'mobile_allowance', 'meal_allowance', 'motor_vehicle_allowance',
                 'driver_fuel_allowance', 'books_allowance', 'special_other_allowance', 'commission', 'pf_allowance', 'night_shift_allowance')
    def _compute_tot_salary(self):
        for rec in self:
            rec.total_salary = rec.get_all_allowance()
            rec.total_leave_salary = rec.get_leave_salary()

    def get_leave_deduction(self):
        debuctable_allowance = self.transport_allowance + self.meal_allowance + self.mobile_allowance + self.driver_fuel_allowance + self.motor_vehicle_allowance
        return debuctable_allowance


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        res = super(Payslip, self)._get_worked_day_lines(domain=domain, check_out_of_contract=check_out_of_contract)
        work_entry = self.env.ref('hr_work_entry.work_entry_type_attendance')
        total_days = sum(line['number_of_days'] for line in res)
        contract = self.contract_id
        calendar_days = contract.resource_calendar_id.month_days

        for r in res:
            if r.get('work_entry_type_id') == work_entry.id and contract.resource_calendar_id and calendar_days:
                if r.get('number_of_days') > calendar_days:
                    number_of_days = calendar_days
                    number_of_hours = number_of_days * contract.resource_calendar_id.hours_per_day
                    r['number_of_days'] = number_of_days
                    r['number_of_hours'] = number_of_hours
                elif total_days < calendar_days:
                    remain_days = (calendar_days - total_days)
                    r['number_of_days'] += remain_days

        return res

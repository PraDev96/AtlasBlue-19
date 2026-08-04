# -*- coding: utf-8 -*-

import calendar
from pytz import UTC
from pytz import timezone
from odoo.tools import date_utils
from datetime import datetime, time
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    before_request_days = fields.Integer(string="Request Before Days")
    is_business_type = fields.Boolean(string="Business Leave")
    allowed_after_service_period = fields.Float(string="Allowed After Service Period (in months)")
    include_in_eos = fields.Boolean(string="Include in EOS")
    max_at_a_time = fields.Float(string="Maximum at one Time")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('both', 'Both Gender')], string="Leave For", default='both')
    religion_in = fields.Selection([('all', 'All Religion'), ('muslim', 'Muslim'), ('non_muslim', 'Non Muslim')], string="Religion In", default='all')
    leave_type = fields.Selection([('general', 'General'), ('maternity', 'Maternity Leave'), ('hajj', 'Hajj Leave'), ('sick', 'Sick Leave')],
                                  string="Leave Type", default='general')

    @api.constrains('before_request_days')
    def _check_before_request_days(self):
        if self.before_request_days < 0.0:
            raise ValidationError(_("Request Before Days always zero or greater than zero!"))


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    total_accured_balance = fields.Float(compute='_compute_accured_balance_leave', string="Accured Balance", store=True)
    leave_unpaid_days = fields.Float(compute='_compute_accured_balance_leave', string="Unpaid Days", store=True)
    leave_paid_days = fields.Float(compute='_compute_accured_balance_leave', string="Paid Days", store=True)
    public_days = fields.Float(compute='_compute_accured_balance_leave', string="Public Days", store=True)
    working_days_balance = fields.Float(compute='_compute_accured_balance_leave', string="Working Days Balance", store=True)

    # Replaced for leave encasement fix for version 17.0
    number_of_days_display = fields.Float('Duration in days', compute='_compute_number_of_days_display', readonly=False,
                                          help='Number of days of the time off request according to your working schedule. Used for interface.')
    number_of_hours_display = fields.Float('Duration in hours', compute='_compute_number_of_hours_display', readonly=False,
                                           help='Number of hours of the time off request according to your working schedule. Used for interface.')

    def update_leave_completion(self):
        for leave in self:
            if leave.holiday_status_id.leave_type == 'hajj':
                leave.employee_id.write({'is_completed_hajj': True})

    def action_validate(self):
        res = super(HrLeave, self).action_validate()
        self.update_leave_completion()

        return res

    def _generate_future_allocations(self, employee, holiday_status, date_from, date_to):
        if not (employee and holiday_status and date_to):
            return 0.0
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            return 0.0

        date_from = fields.Date.to_date(date_from)
        date_to = fields.Date.to_date(date_to)
        today = fields.Date.today()

        if date_to < today:
            return 0.0

        # Check for any validated allocation by OdooBot for this employee/type
        odoobot_id = self.env.ref('base.user_root').id
        has_odoobot_alloc = self.env['hr.leave.allocation'].sudo().search_count([
            ('employee_id', '=', employee.id),
            ('holiday_status_id', '=', holiday_status.id),
            ('create_uid', '=', odoobot_id),
            ('state', '=', 'validate'),
            ('date_from', '=', date_from.replace(day=1))
        ])

        if not has_odoobot_alloc:
            return 0.0

        leave_type = holiday_status
        if leave_type.requires_allocation != 'yes':
            return 0.0

        contract = employee.sudo().contract_id
        if not (contract and 'leave_allocation' in contract._fields and contract.leave_allocation > 0):
            return 0.0

        start_date = today.replace(day=1)
        end_date = date_to.replace(day=1)

        diff_months = list(rrule(MONTHLY, dtstart=start_date, until=end_date))
        newly_allocated_days = 0.0

        for dt_by_month in [future_months for future_months in diff_months if future_months != datetime.combine(date_from.replace(day=1), time.min)]:
            month_start = dt_by_month.date()
            month_end = month_start + relativedelta(months=1, days=-1)

            existing_allocation = self.env['hr.leave.allocation'].search_count([
                ('employee_id', '=', employee.id),
                ('holiday_status_id', '=', leave_type.id),
                ('state', '=', 'validate'),
                ('date_from', '>=', month_start),
                ('date_from', '<=', month_end),
            ])

            if not existing_allocation:
                self.env['hr.leave.allocation'].sudo().create({
                    'name': _('Auto Allocation: %s - %s') % (leave_type.name, month_start.strftime('%B %Y')),
                    'holiday_type': 'employee',
                    'employee_id': employee.id,
                    'holiday_status_id': leave_type.id,
                    'allocation_type': 'regular',
                    'number_of_days': contract.leave_allocation,
                    'date_from': month_start,
                    'date_to': month_end,
                }).action_validate()
                newly_allocated_days += contract.leave_allocation
        return newly_allocated_days

    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_approve(self):
        super(HrLeave, self)._compute_can_approve()
        for leave in self:
            if leave.holiday_status_id.leave_validation_type == 'multiple':
                leave.can_approve = True

    def send_mail_leave_notification(self):
        start = UTC.localize(self.date_from).astimezone(timezone(self.employee_id.tz or 'UTC'))
        end = UTC.localize(self.date_to).astimezone(timezone(self.employee_id.tz or 'UTC'))
        email_body = _("New '%s' Request created by %s from %s to %s") % (self.holiday_status_id.name, self.create_uid.name, start, end)

        recipients = []
        for holiday in self.filtered(lambda r: r.validation_type == 'multiple'):
            for leave_type_id in holiday.leave_approval_history_ids:
                if leave_type_id.approver_type == 'coach' and self.employee_id.coach_id.work_email:
                    recipients.append(self.employee_id.coach_id.work_email)
                elif leave_type_id.approver_type == 'manager' and self.employee_id.parent_id.work_email:
                    recipients.append(self.employee_id.parent_id.work_email)
                elif leave_type_id.approver_type == 'dept_manager' and self.employee_id.department_id and self.employee_id.department_id:
                    recipients.append(self.employee_id.department_id.manager_id.work_email)
                elif leave_type_id.approver_type == 'hr_admin_manager':
                    recipients += self.env.ref('hr_leave_custom.group_hr_admin_manager').users.mapped('partner_id.email')
                elif leave_type_id.approver_type == 'hr_admin_officer':
                    recipients += self.env.ref('hr_leave_custom.group_hr_admin_officer').users.mapped('partner_id.email')
                elif leave_type_id.approver_type == 'hr_admin_admin':
                    recipients += self.env.ref('hr_holidays.group_hr_holidays_manager').users.mapped('partner_id.email')

        if self.state == 'confirm':
            Template = self.env.ref('boutiqaat_hr_base.leave_create')
            Template.send_mail(res_id=self.id, force_send=True, email_values={
                'body_html': email_body,
                'subject': 'leave Notification : ' + str(fields.Datetime.today()),
                'email_to': ", ".join(list(set(recipients))),
                'email_from': self.employee_id.work_email,
            })

    @api.model_create_multi
    def create(self, vals_list):
        record = super(HrLeave, self).create(vals_list)
        number_of_days_display = 0
        record.send_mail_leave_notification()
        for vals in vals_list:
            number_of_days_display = vals.get('number_of_days_display')
            if not self._context.get('leave_fast_create'):
                leave_type = self.env['hr.leave.type'].sudo().browse(vals.get('holiday_status_id'))
                # Handle no_validation
                if leave_type and leave_type.leave_validation_type == 'no_validation':
                    record.sudo().update_leave_completion()

        record.number_of_days = number_of_days_display
        record.number_of_days_display = number_of_days_display
        return record

    @api.constrains('employee_id', 'holiday_status_id', 'request_date_from', 'request_date_to')
    def _check_fixed_allocation_leave(self):
        Leave = self.env['hr.leave.report']
        for rec in self:
            holi_status = rec.holiday_status_id
            employee = rec.employee_id
            if holi_status.requires_allocation in ('yes', 'cron'):
                current_total_balance = 0.0
                working_days_balance = 0.0
                balance_leaves = Leave.search([('employee_id', '=', employee.id), ('holiday_status_id', '=', holi_status.id), ('state', '=', 'validate')])

                current_total_balance = sum(balance_leaves.mapped('number_of_days'))

                current_date = fields.Datetime.today()
                # worked = rec.employee_id.resource_calendar_id.get_work_duration_data(current_date, date_from)
                date_to = rec.date_to or fields.Datetime.today()
                worked_days = (date_to - current_date).days
                if worked_days <= 0.0:
                    worked_days = 0.0

                if employee.sudo().contract_id:
                    working_days = 0.0
                    allocation_value = employee.sudo().contract_id.leave_allocation
                    allocation_type = employee.sudo().contract_id.allocation_type
                    if allocation_type == 'month':
                        month_days = calendar.monthrange(date_to.year, date_to.month)[1]
                        working_days = worked_days / month_days
                    elif allocation_type == 'week':
                        working_days = worked_days / 7
                    elif allocation_type == 'day':
                        working_days = worked_days

                    working_days_balance = allocation_value * working_days

                if rec.number_of_days > current_total_balance:
                    if rec.employee_id and rec.holiday_status_id and rec.date_to and self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                        newly_allocated_days = rec._generate_future_allocations(rec.employee_id, rec.holiday_status_id, rec.request_date_from, rec.date_to)
                        current_total_balance += newly_allocated_days
                        self._cr.commit()

                total_accured_balance = round(current_total_balance + working_days_balance, 3)
                if rec.number_of_days > total_accured_balance:
                    raise ValidationError(
                        _("%s does not have a valid allocation for the leave type %s to cover that request.") % (rec.employee_id.name, holi_status.name)
                    )

    @api.constrains('employee_id', 'holiday_status_id', 'request_date_from', 'request_date_to')
    def _check_hajj_leave(self):
        holi_status = self.holiday_status_id
        employee = self.employee_id
        if holi_status.allowed_after_service_period > 0.0:
            if not employee.date_joining:
                raise ValidationError(_("Please mention joining date in Employee Form"))

            diff = relativedelta(self.request_date_from, employee.date_joining)
            service_in_months = diff.months + (diff.years * 12)
            if service_in_months < holi_status.allowed_after_service_period:
                raise ValidationError(_("For this leave, your service months have to complete %s months!") % holi_status.allowed_after_service_period)

        if holi_status.gender != 'both' and employee.gender != holi_status.gender:
            raise ValidationError(_("This Type of leave only for %s gender!") % holi_status.gender)

        if holi_status.leave_type == 'hajj' and employee.is_completed_hajj:
            raise ValidationError(_("You already completed Hajj. You can't apply this leave type!"))

        if holi_status.max_at_a_time > 0.0 and self.number_of_days > holi_status.max_at_a_time:
            raise ValidationError(_("You can't apply more than %s days same time!") % holi_status.max_at_a_time)

        if holi_status.religion_in != 'all' and holi_status.religion_in != employee.religion:
            raise ValidationError(_("This leave is applicable only for %s religion !") % holi_status.religion_in)

    @api.constrains('holiday_status_id', 'request_date_from')
    def _check_request_before_days(self):
        today = fields.Date.from_string(fields.Date.today())
        for leave in self:
            if leave.request_date_from:
                renew_date = fields.Date.from_string(leave.request_date_from)
                diff_days = (renew_date - today).days
                if leave.holiday_status_id.before_request_days > 0 and diff_days < leave.holiday_status_id.before_request_days:
                    raise ValidationError(_("For %s Leave you have to apply before %s days!") % (leave.holiday_status_id.name, leave.holiday_status_id.before_request_days))

    def get_last_holiday(self):
        leave = self.search([('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'), ('id', '!=', self.id)], order='request_date_from desc', limit=1)
        return leave

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_accured_balance_leave(self):
        Leave = self.env['hr.leave.report']
        for rec in self:
            leave_paid_days = 0.0
            leave_unpaid_days = 0.0
            total_accured_balance = 0.0
            public_days = 0.0
            current_total_balance = 0.0
            working_days_balance = 0.0

            balance_leaves = Leave.search([('employee_id', '=', rec.employee_id.id), ('holiday_status_id', '=', rec.holiday_status_id.id), ('state', '=', 'validate')])
            current_total_balance = sum(balance_leaves.mapped('number_of_days'))
            date_to = rec.date_to
            if rec.date_to:
                current_date = fields.Datetime.today()
                # worked = rec.employee_id.resource_calendar_id.get_work_duration_data(current_date, date_from)

                worked_days = (date_to - current_date).days
                if worked_days <= 0.0:
                    worked_days = 0.0

                if rec.employee_id.sudo().contract_id and 'leave_allocation' in rec.employee_id.sudo().contract_id._fields:
                    working_days = 0.0
                    allocation_value = rec.employee_id.sudo().contract_id.leave_allocation
                    allocation_type = rec.employee_id.sudo().contract_id.allocation_type
                    if allocation_type == 'month':
                        month_days = calendar.monthrange(date_to.year, date_to.month)[1]
                        working_days = worked_days / month_days
                    elif allocation_type == 'week':
                        working_days = worked_days / 7
                    elif allocation_type == 'day':
                        working_days = worked_days

                    working_days_balance = allocation_value * working_days

                total_accured_balance = (current_total_balance + working_days_balance)

                if rec.holiday_status_id.unpaid:
                    leave_unpaid_days = rec.number_of_days
                else:
                    leave_paid_days = rec.number_of_days
                public_days = rec.employee_id.with_context(global_only=True)._get_leave_days_data_batch(rec.date_from, rec.date_to, domain=[])[rec.employee_id.id]['days']
            rec.total_accured_balance = round(total_accured_balance, 2)
            rec.leave_unpaid_days = round(leave_unpaid_days, 2)
            rec.leave_paid_days = round(leave_paid_days, 2)
            rec.public_days = round(public_days, 2)
            rec.working_days_balance = round(working_days_balance, 2)

    def get_employee_accured_date(self):
        data = {}
        Leave = self.env['hr.leave.report']

        leave_paid_days = 0.0
        leave_unpaid_days = 0.0
        total_leave_balance = 0.0
        public_days = 0.0
        current_total_balance = 0.0
        public_days = 0.0

        balance_leaves = Leave.search([('employee_id', '=', self.employee_id.id), ('holiday_status_id', '=', self.holiday_status_id.id), ('state', '=', 'validate')])
        current_total_balance = sum(balance_leaves.mapped('number_of_days'))
        date_to = self.date_to
        if self.date_to:
            current_date = fields.Datetime.today()
            worked = self.employee_id.resource_calendar_id.get_work_duration_data(current_date, date_to)
            working_days_balance = 0.0
            if self.employee_id.sudo().contract_id:
                working_days = 0.0
                allocation_value = self.employee_id.sudo().contract_id.leave_allocation
                allocation_type = self.employee_id.sudo().contract_id.allocation_type
                if allocation_type == 'month':
                    month_days = calendar.monthrange(date_to.year, date_to.month)[1]
                    working_days = worked['days'] / month_days
                elif allocation_type == 'week':
                    working_days = worked['days'] / 7
                elif allocation_type == 'day':
                    working_days = worked['days']

                working_days_balance = allocation_value * working_days

            total_leave_balance = (current_total_balance + working_days_balance)
            leave_unpaid_days = 0.0
            leave_paid_days = 0.0
            if self.holiday_status_id.unpaid:
                leave_unpaid_days = self.number_of_days
            else:
                leave_paid_days = self.number_of_days

            public_days = self.employee_id.with_context(global_only=True)._get_leave_days_data(self.date_from, self.date_to, domain=[])['days']
            date_to = self.date_to
            if not date_to.tzinfo:
                date_to = date_to.replace(tzinfo=UTC)

        data.update({
            'leave_paid_balance': round(0.0, 2),
            'leave_unpaid_balance': round(0.0, 2),
            'accured_balance': round(total_leave_balance, 3),
            'balance_leave_days': round(current_total_balance, 2),
            'leave_unpaid_days': leave_unpaid_days,
            'leave_paid_days': leave_paid_days,
            'public_days': public_days,
        })

        return data

    def get_date_start_end(self, dt):
        from_date = dt.replace(day=1)
        to_date = dt + relativedelta(day=1, months=1, days=-1)
        return from_date, to_date

    def get_extra_line(self, input_type):
        start, end = self.get_date_start_end(self.request_date_from)
        rows = self.employee_id.get_emp_input_lines(start, end, input_type)
        total = sum(list(map(lambda r: r[1], rows)))

        return total

    def get_input_lines(self, input_type, date_from, date_to):
        # All Inputs other than LEAVE ENCASHMENT
        emp_id = self.employee_id.id
        sql = """
            SELECT sum(l.amount)
            FROM emp_inputs AS input
                LEFT JOIN emp_input_line AS l
                    ON l.emp_input_id = input.id
                LEFT JOIN emp_leave_encashment AS encash
                    ON l.emp_input_id != encash.emp_input_id
            WHERE
                input.state = 'confirm'
                AND
                input.input_type = %s
                AND
                input.employee_id = %s
                AND
                l.payslip_date BETWEEN %s AND %s
                AND
                l.state = 'due'
                AND
                encash.employee_id = %s AND encash.state = 'confirm'
        """
        self.env.cr.execute(sql, ((input_type, emp_id, date_from, date_to, emp_id)))
        total = self.env.cr.fetchone()

        return total and total[0] or 0

    def get_addition(self):
        allowance_lines = self.payslip_id.line_ids.filtered(lambda line: line.category_id.code == 'ALW')
        emp_inp_total = sum(allowance_lines.mapped('amount'))
        return emp_inp_total

    def get_deduction(self):
        # Emp Input & Loan
        deduction_lines = self.payslip_id.line_ids.filtered(lambda line: line.category_id.code == 'DED')
        emp_ded_tot = sum(deduction_lines.mapped('amount'))
        return emp_ded_tot

    def get_working_salary_days(self):
        data = {}
        if self.payment_type == 'payslip':
            date_from = date_utils.start_of(self.period_date, 'month')
            date_to = date_utils.end_of(self.period_date, 'month')
        else:
            date_from = self.request_date_from
            date_to = self.request_date_to

        date_from = datetime.combine(date_from, time.min)
        date_to = datetime.combine(date_to, time.max)
        emp = self.employee_id
        per_day_salary = emp.contract_id.get_per_day_salary()

        if not date_from.tzinfo:
            date_from = date_from.replace(tzinfo=UTC)
        if not date_to.tzinfo:
            date_to = date_to.replace(tzinfo=UTC)

        worked = emp._get_work_days_data_batch(date_from, date_to, domain=[])[emp.id]['days']
        public_days = emp.with_context(global_only=True)._get_leave_days_data_batch(self.date_from, self.date_to, domain=[])[emp.id]['days']
        leave_days = 0.0
        if not self.holiday_status_id.unpaid:
            leave_days = self.number_of_days

        addition = self.get_addition()
        deduction = self.get_deduction()
        worked_salary = (worked * per_day_salary)

        sick_leave_ded = 0
        if self.holiday_status_id.leave_type == 'sick':
            sick_leave_ded = self.employee_id.get_sick_leave_ded(False, (date_to - date_from).days, emp.contract_id)
            worked_salary = worked_salary + sick_leave_ded

        leave_salary = (leave_days * per_day_salary)
        public_salary = (public_days * per_day_salary)
        total_salary = (worked_salary + leave_salary + public_salary + addition - deduction)

        data = {
            'period_month': date_from.strftime('%B'),
            'working_days': worked,
            'working_salary': round(worked_salary, 2),
            'sick_leave_ded': round(sick_leave_ded, 2),
            'leave_salary': round(leave_salary, 2),
            'leave_day_salary': round(per_day_salary, 2),
            'other_addition': round(addition, 2),
            'other_deduction': round(deduction, 2),
            'total_salary': round(total_salary, 2),
            'public_salary': round(public_salary, 2),
            'payment_type': self.payment_type,
        }

        return data

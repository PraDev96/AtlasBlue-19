# -*- coding:utf-8 -*-

from datetime import datetime, time
from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    leave_validation_type = fields.Selection(selection_add=[('multiple', 'Multiple Approval')])
    approver_ids = fields.One2many('hr.leave.approver', 'leave_type_id', string="Leave Approvers")
    resumer_ids = fields.One2many('hr.leave.resumer', 'leave_type_id', string="Leave Resumers")
    is_resume_date_required = fields.Boolean(string="Is Resume Date Required?")
    allow_previous_leave = fields.Boolean(string="Is Previous Date Leave Allowed ?")
    is_auto_allocate = fields.Boolean(string="Is Auto Allocate?")
    auto_allocation_date = fields.Date(string="Auto Allocation Date")


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    leave_approval_history_ids = fields.One2many('hr.leave.approval.history', 'hr_leave_id', string="Leave Approval History")
    leave_resume_history_ids = fields.One2many('hr.leave.resume.history', 'hr_leave_id', string="Leave Resume History")
    is_show_approve = fields.Boolean(compute='compute_show_approve', string="s Show Approve?")
    date_resume = fields.Datetime("Resume Date")
    leave_reason = fields.Text("Reason")
    allocation_request_id = fields.Many2one('hr.leave.allocation', string="Allocation Request")
    leave_request_id = fields.Many2one('hr.leave', string="Leave Request")
    resume_days = fields.Float("Resume Days", readonly=True)
    is_show_resume = fields.Boolean(compute='compute_show_resume', string="Is Show Resume?")
    is_resume = fields.Boolean(string="Resume")
    is_employee_resume = fields.Boolean(string="Is Employee Resumed?")
    leave_resume_date = fields.Date(string="Leave Resume Date")
    is_resume_date_required = fields.Boolean(string="Is Resume Date Required?")
    att_log_id = fields.Many2one("att.upload.log", string="Attendance Log")

    @api.constrains('request_date_from')
    def _check_request_date_from(self):
        for leave in self:
            if not leave.holiday_status_id.allow_previous_leave and leave.request_date_from < fields.Date.today():
                raise UserError(_('Leave cannot be created in previous date!'))

    @api.constrains('state', 'number_of_days', 'holiday_status_id')
    def _check_holidays(self):
        # Customer Req.
        # No Need Balance Condition, but still needs to Allocate Balance.
        pass

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_leave_dates(self):
        if self.date_from and self.date_to and self.holiday_status_id.leave_type == 'sick':
            self.number_of_days = (self.request_date_to - self.request_date_from).days + 1

    def _get_number_of_days(self, date_from, date_to, employee_id):
        if self.holiday_status_id.leave_type == 'sick':
            days = (date_to - date_from).days + 1
            employee = self.env['hr.employee'].browse(employee_id)
            result = {
                'days': days,
                'hours': days * (employee.contract_id.hours_per_day or 8)
            }
        else:
            if employee_id:
                employee = self.env['hr.employee'].browse(employee_id)
                return employee._get_work_days_data_batch(date_from, date_to)[employee.id]

            comp_resource = self.env.company.resource_calendar_id
            today_hours = comp_resource.get_work_hours_count(datetime.combine(date_from.date(), time.min), datetime.combine(date_from.date(), time.max), False)
            hours = comp_resource.get_work_hours_count(date_from, date_to)
            result = {
                'days': hours / (today_hours or 8),
                'hours': hours
            }

        return result

    @api.constrains('leave_resume_date')
    def _check_resume_date(self):
        for leave in self:
            if leave.leave_resume_date and leave.leave_resume_date < leave.request_date_to:
                raise ValidationError(_('Resume date should be great than leave last date!'))

    def _get_number_leave_days(self, date_from, date_to, employee_id):
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            return employee._get_work_days_data_batch(date_from, date_to, compute_leaves=False)

        today_hours = self.env.company.resource_calendar_id.get_work_hours_count(
            datetime.combine(date_from.date(), time.min), datetime.combine(date_from.date(), time.max), False
        )
        hours = self.env.company.resource_calendar_id.get_work_hours_count(date_from, date_to)

        return {
            'days': hours / (today_hours or 8),
            'hours': hours
        }

    def compute_show_approve(self):
        Employee = self.env['hr.employee']
        for leave in self:
            show_leave = True
            if leave.holiday_status_id.leave_validation_type == 'multiple':
                remain_approvals = leave.leave_approval_history_ids.filtered(lambda x: not x.is_approve)
                if remain_approvals:
                    if len(remain_approvals) == 1:
                        current_remain_approval = remain_approvals
                    else:
                        current_remain_approval = remain_approvals[0]

                    if current_remain_approval:
                        current_user_employee = Employee.search([('user_id', '=', self.env.user.id)], limit=1)
                        if current_remain_approval.approver_type == 'coach' and current_user_employee != leave.employee_id.coach_id:
                            show_leave = False
                        elif current_remain_approval.approver_type == 'manager' and current_user_employee != leave.employee_id.parent_id:
                            show_leave = False
                        elif current_remain_approval.approver_type == 'dept_manager' and current_user_employee != leave.employee_id.department_id.manager_id:
                            show_leave = False
                        elif current_remain_approval.approver_type == 'hr_admin_manager' and not self.env.user.has_group('hr_leave_custom.group_hr_admin_manager'):
                            show_leave = False
                        elif current_remain_approval.approver_type == 'hr_admin_officer' and not self.env.user.has_group('hr_leave_custom.group_hr_admin_officer'):
                            show_leave = False
                        elif current_remain_approval.approver_type == 'hr_admin_admin' and not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                            show_leave = False

            leave.is_show_approve = show_leave

    def compute_show_resume(self):
        Employee = self.env['hr.employee']
        for leave in self:
            show_resume = True
            current_user_employee = Employee.search([('user_id', '=', self.env.user.id)], limit=1)
            if current_user_employee != leave.employee_id and not leave.is_employee_resume:
                show_resume = False

            if leave.holiday_status_id and leave.is_employee_resume:
                remain_approvals = leave.leave_resume_history_ids.filtered(lambda x: not x.is_approve)
                if remain_approvals:
                    if len(remain_approvals) == 1:
                        current_remain_approval = remain_approvals
                    else:
                        current_remain_approval = remain_approvals[0]

                    if current_remain_approval:
                        if current_remain_approval.approver_type == 'coach' and current_user_employee != leave.employee_id.coach_id:
                            show_resume = False
                        elif current_remain_approval.approver_type == 'manager' and current_user_employee != leave.employee_id.parent_id:
                            show_resume = False
                        elif current_remain_approval.approver_type == 'dept_manager' and current_user_employee != leave.employee_id.department_id.manager_id:
                            show_resume = False
                        elif current_remain_approval.approver_type == 'hr_admin_manager' and not self.env.user.has_group('hr_leave_custom.group_hr_admin_manager'):
                            show_resume = False
                        elif current_remain_approval.approver_type == 'hr_admin_officer' and not self.env.user.has_group('hr_leave_custom.group_hr_admin_officer'):
                            show_resume = False
                        elif current_remain_approval.approver_type == 'hr_admin_admin' and not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                            show_resume = False

            leave.is_show_resume = show_resume

    @api.onchange('holiday_status_id')
    def onchange_holiday_status_id(self):
        self.leave_approval_history_ids = False
        self.leave_resume_history_ids = False
        if self.holiday_status_id:
            self.is_resume_date_required = self.holiday_status_id.is_resume_date_required
            if self.holiday_status_id.leave_validation_type == 'multiple':
                approval_list = []
                resume_list = []
                for line in self.holiday_status_id.approver_ids:
                    approval_list.append((0, 0, {
                        'sequence': line.sequence,
                        'approver_type': line.approver_type,
                    }))
                self.leave_approval_history_ids = approval_list

                for line in self.holiday_status_id.resumer_ids:
                    resume_list.append((0, 0, {
                        'sequence': line.sequence,
                        'approver_type': line.approver_type,
                    }))

                self.leave_resume_history_ids = resume_list

    def action_approve(self):
        self.action_emp_input()
        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_('Time off request must be confirmed ("To Approve") in order to approve it.'))

        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        self.filtered(lambda hol: hol.validation_type == 'both').write({'state': 'validate1', 'first_approver_id': current_employee.id})

        for holiday in self.filtered(lambda r: r.validation_type == 'multiple'):
            remain_approvals = holiday.leave_approval_history_ids.filtered(lambda x: not x.is_approve)
            if remain_approvals:
                if len(remain_approvals) == 1:
                    current_remain_approval = remain_approvals
                    current_remain_approval.write({
                        'approved_by_id': self.env.uid,
                        'approved_time': fields.Datetime.now(),
                        'is_approve': True,
                    })
                else:
                    current_remain_approval = remain_approvals[0]
                    current_remain_approval.write({
                        'approved_by_id': self.env.uid,
                        'approved_time': fields.Datetime.now(),
                        'is_approve': True,
                    })
                    return True

        # Post a second message, more verbose than the tracking message
        for holiday in self.filtered(lambda holiday: holiday.employee_id.user_id):
            holiday.message_post(
                body=_('Your %s planned on %s has been accepted' % (holiday.holiday_status_id.display_name, holiday.date_from)),
                partner_ids=holiday.employee_id.user_id.partner_id.ids
            )

        self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        if not self.env.context.get('leave_fast_create'):
            self.activity_update()

        return True

    def action_resume(self):
        action = self.env.ref('hr_leave_custom.action_resume_work_wizard').read()[0]
        action['context'] = self.env.context
        return action

    def action_draft(self):
        res = super(HrLeave, self).action_draft()
        self.leave_approval_history_ids.write({'is_approve': False})
        self.leave_resume_history_ids.write({'is_approve': False})
        self.write({'is_employee_resume': False})
        return res


class HrLeaveApprover(models.Model):
    _name = 'hr.leave.approver'
    _description = "HR Leave Approver"
    _order = 'sequence'

    sequence = fields.Integer(string="Sequence", required=True)
    approver_type = fields.Selection([
        ('coach', 'By Coach'),
        ('manager', 'By Manager'),
        ('dept_manager', 'By Department Manager'),
        ('hr_admin_manager', 'By HR Manager'),
        ('hr_admin_officer', 'By HR Officer'),
        ('hr_admin_admin', 'By HR Admin'),
        ('hr_group', 'By HR Group')],
        string="Approver Type", required=True)
    leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type")


class HrLeaveResumer(models.Model):
    _name = 'hr.leave.resumer'
    _description = "HR Leave Resumer"
    _order = 'sequence'

    sequence = fields.Integer(string="Sequence", required=True)
    approver_type = fields.Selection([
        ('coach', 'By Coach'),
        ('manager', 'By Manager'),
        ('dept_manager', 'By Department Manager'),
        ('hr_admin_manager', 'By HR Manager'),
        ('hr_admin_officer', 'By HR Officer'),
        ('hr_admin_admin', 'By HR Admin'),
        ('hr_group', 'By HR Group')],
        string="Approver Type", required=True)
    leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type")


class HrLeaveApprovalHistory(models.Model):
    _name = 'hr.leave.approval.history'
    _description = "HR Leave Approval History"
    _order = 'sequence'

    sequence = fields.Integer(string="Sequence", required=True)
    approver_type = fields.Selection([
        ('coach', 'By Coach'),
        ('manager', 'By Manager'),
        ('dept_manager', 'By Department Manager'),
        ('hr_admin_manager', 'By HR Manager'),
        ('hr_admin_officer', 'By HR Officer'),
        ('hr_admin_admin', 'By HR Admin'),
        ('hr_group', 'By HR Group')],
        string="Approver Type", required=True)
    is_approve = fields.Boolean(string="Is Approved?")
    approved_by_id = fields.Many2one('res.users', string="Approved By", readonly=True)
    approved_time = fields.Datetime(string="Approved Time", readonly=True)
    hr_leave_id = fields.Many2one('hr.leave', string="Leave")


class HrLeaveResumeHistory(models.Model):
    _name = 'hr.leave.resume.history'
    _description = "HR Leave Resume History"
    _order = 'sequence'

    sequence = fields.Integer(string="Sequence", required=True)
    approver_type = fields.Selection([
        ('coach', 'By Coach'),
        ('manager', 'By Manager'),
        ('dept_manager', 'By Department Manager'),
        ('hr_admin_manager', 'By HR Manager'),
        ('hr_admin_officer', 'By HR Officer'),
        ('hr_admin_admin', 'By HR Admin'),
        ('hr_group', 'By HR Group')],
        string="Approver Type", required=True)
    is_approve = fields.Boolean(string="Is Approved?")
    approved_by_id = fields.Many2one('res.users', string="Approved By", readonly=True)
    approved_time = fields.Datetime(string="Approved Time", readonly=True)
    hr_leave_id = fields.Many2one('hr.leave', string="Leave")


class HrGroup(models.Model):
    _name = 'hr.group'
    _description = "HR Group"

    name = fields.Char(string="Name", required=True)
    emp_approve_ids = fields.Many2many('hr.employee', string="Employees")


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    group_id = fields.Many2one('hr.group', string="Group", groups="hr.group_hr_user")

    def action_view_employee_timeoff_analysis(self):
        self.ensure_one()
        return {
            'name': 'Time Off Analysis',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave.report',
            'view_mode': 'tree,pivot,graph',
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'search_default_year': True,
                'default_employee_id': self.id,
                'search_default_validated': True,
                'search_default_group_type': True,
            },
        }


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    group_id = fields.Many2one('hr.group', string="Group", readonly=True)


class AttendanceUploadLog(models.Model):
    _inherit = 'att.upload.log'

    leave_ids = fields.One2many("hr.leave", "att_log_id", string="Leaves")
    leave_count = fields.Integer(string="Total Uploaded Leaves", compute="_compute_leave_count")

    def _compute_leave_count(self):
        for rec in self:
            rec.leave_count = len(rec.leave_ids.ids)


class LeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    is_auto_generate = fields.Boolean(string="Is Auto Generate?")
    employee_join_date = fields.Date(related="employee_id.date_joining")

    def create_auto_type_leave_allocation(self):
        LeaveType = self.env['hr.leave.type']
        leave_types = LeaveType.search([('is_auto_allocate', '=', True)])
        today = fields.Date.today()
        employees = self.env['hr.employee'].search([])
        for employee in employees:
            for leave_type in leave_types.filtered(lambda l: l.company_id == employee.company_id or not l.company_id):
                if leave_type.auto_allocation_date and datetime.strptime(leave_type.auto_allocation_date.strftime('%m-%Y'), '%m-%Y') > datetime.strptime(
                        today.strftime('%m-%Y'), '%m-%Y'):
                    continue

                if employee.company_id == leave_type.company_id and employee.contract_id and employee.contract_id.leave_allocation > 0.0:
                    self.create({
                        'name': leave_type.name + ' - ' + today.strftime('%B'),
                        'holiday_type': 'employee',
                        'employee_id': employee.id,
                        'holiday_status_id': leave_type.id,
                        'allocation_type': 'regular',
                        'number_of_days': employee.contract_id.leave_allocation,
                        'is_auto_generate': True,
                        'mode_company_id': employee.company_id.id,
                    })

                leave_type.write({'auto_allocation_date': datetime.date().today()})

# -*- coding: utf-8 -*-

from odoo import models, fields

CURRENTLY_WITH = [('emp', 'Employee'), ('org', 'In Office')]


class PassportHistory(models.Model):
    _name = 'passport.history'
    _description = 'Password History'

    receiving_date = fields.Date(string="Receiving Date", required=True)
    returning_date = fields.Date(string="Returning Date")
    reasons = fields.Text(string="Reasons")
    employee_id = fields.Many2one('hr.employee', string="Employee")


class EmployeeBenefits(models.Model):
    _name = 'employee.benefits'
    _description = 'Employee Benefits'

    name = fields.Char(string="Benefits", required=True)
    value = fields.Float(string="Value")
    employee_id = fields.Many2one('hr.employee', string="Employee")


class EmployeeDocument(models.Model):
    _name = 'employee.document'
    _description = "Employee Documents"

    name = fields.Char(string="Filename", required=True)
    file = fields.Binary(string="File Content", required=True)
    article_type_id = fields.Many2one('article.type', string="Attachment Type", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    history_ids = fields.One2many("employee.document.history", "emp_doc_id", string="History")

    date_last_action = fields.Datetime(string="Since", related="history_ids.date_last_action")
    currently_with = fields.Selection(related="history_ids.currently_with")


class EmployeeDocHistory(models.Model):
    _name = 'employee.document.history'
    _description = "Employee Documents History"
    _order = "date_last_action desc"

    emp_doc_id = fields.Many2one("employee.document", string="Employee Document")
    currently_with = fields.Selection(CURRENTLY_WITH, string="With", required=True)
    date_last_action = fields.Datetime(string="Handover Date", default=fields.Datetime.now)
    reason = fields.Text(string="Reason", required=True)


class HrAsset(models.Model):
    _name = 'employee.asset'
    _description = "Employee Assets"

    date_assigned = fields.Datetime(string="Date Assigned", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")


class EmpDiscount(models.Model):
    _name = 'emp.discount'
    _description = "Employee Discount"
    _order = "date_payslip desc"

    name = fields.Char(string="Invoice Reference", required=True, index=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    inv_amount = fields.Float(string="Invoice Amount")
    date_invoice = fields.Date(string="Invoice Date", required=True)
    note = fields.Text(string="Note")
    date_payslip = fields.Date(string="Payslip Date", required=True, help="System will give discount in this Month Payroll.")
    is_discounted = fields.Boolean(string="Considered in Payslip ?")

    _sql_constraints = [('name_unique', 'unique (name)', 'The invoice reference must be unique !')]


class AttendanceUploadLog(models.Model):
    _name = 'att.upload.log'
    _description = "Attendance Upload Log"

    name = fields.Char(string="File Name")
    file = fields.Binary(string="File")
    skipped_count = fields.Integer(string="Skipped Lines")
    skipped_text = fields.Text(string="Skipped Text")
    ignored_count = fields.Integer(string="Ignored Lines")
    ignored_text = fields.Text(string="Ignored Text")
    no_emp_count = fields.Integer(string="Employee Not Found Lines")
    no_emp_text = fields.Text(string="Employee Not Found Text")

# -*- coding: utf-8 -*-

from odoo import models, fields


class AttendanceUploadLog(models.Model):
    _name = 'att.upload.log'
    _description = "Attendance Upload Log"
    _order = "create_date desc"

    name = fields.Char(string="File Name")
    file = fields.Binary(string="File")
    skipped_count = fields.Integer(string="Skipped Lines")
    skipped_text = fields.Text(string="Skipped Text")
    ignored_count = fields.Integer(string="Ignored Lines")
    ignored_text = fields.Text(string="Ignored Text")
    no_emp_count = fields.Integer(string="Employee Not Found Lines")
    no_emp_text = fields.Text(string="Employee Not Found Text")

    attendance_ids = fields.One2many("hr.attendance", "att_log_id", string="Attendances")
    attendance_count = fields.Integer(string="Total Uploaded Attendance", compute="_compute_attendance_count")

    def _compute_attendance_count(self):
        for rec in self:
            rec.attendance_count = len(rec.attendance_ids.ids)

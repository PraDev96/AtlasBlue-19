# -*- coding: utf-8 -*-

import base64
from datetime import datetime
from odoo import models, fields, api


class ProjectChecklist(models.Model):
    _name = 'project.checklist'
    _description = "Project Checklist"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "projects_id"
    _order = 'date desc'

    projects_id = fields.Many2one('project.project', string="Project", tracking=True)
    task_id = fields.Many2one('project.task', string="Task", tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", tracking=True)
    date = fields.Date(string="Date", default=fields.Date.today, tracking=True)
    vacuum_pool = fields.Boolean(string="Vacuum Pool", help="Vacuum Pool-Daily", tracking=True)
    brush_pool = fields.Boolean(string="Brush Pool", help="Brush Pool-Daily", tracking=True)
    clean_tiles = fields.Boolean(string="Clean Tiles", help="Clean Tiles-Daily", tracking=True)
    skim_pool = fields.Boolean(string="Skim Pool", help="Skim Pool-Daily", tracking=True)
    clean_skimmer_overflow = fields.Boolean(string="Clean Skimmer/Overflow", help="Clean Skimmer/Overflow Gutter-Daily", tracking=True)
    clean_deck_area = fields.Boolean(string="Clean deck area", help="Clean deck area-50cm from pool edge", tracking=True)
    back_wash_filter_before = fields.Char(string="filter pressure before backwash", help="Filter pressure before backwash")
    back_wash_filter_after = fields.Char(string="Filter pressure after backwash", help="Filter pressure after backwash", tracking=True)
    clean_pump_strainer = fields.Boolean(string='Clean Pump Strainer', help="Clean Pump Strainer", tracking=True)
    clean_machine_room = fields.Boolean(string="Clean Machine Room", help="Clean Machine Room(Ones a Month)", tracking=True)
    clean_balance_tank = fields.Boolean(string="Clean Balance Tank", help="Clean Balance Tank(Ones a Month)", tracking=True)
    water_temperature = fields.Float(string="Water Temperature", help="Water Temperature in C", tracking=True)
    free_chlorin_level = fields.Float(string="Free Chlorine Level", help="Free Chlorine level(DPD-3)1.5 to 2.0ppm, Chemical Used and amount", tracking=True)
    total_chlorin_level = fields.Float(string="Total Chlorine level", help="Total Chlorine level Max 0.2 above information FCL Chemical Used", tracking=True)
    ph_level = fields.Float(string="PH Level", help="PH Level 7.4-7.6 Chemical Used/Amount", tracking=True)
    total_alkalinity = fields.Float(string="Total Alkalinity", help="Total Alkalinity 80-120ppm Chemical Used/Amount", tracking=True)
    calcium_acid = fields.Float(string="Calcium Acid", help="Calcium Acid 25-50ppm Chemical Used/Amount", tracking=True)
    calcium_hardness = fields.Float(string="Calcium Hardness", help="Calcium Hardness 200-250ppm Chemical Used/Amount", tracking=True)
    active = fields.Boolean(string="Active", default=True, tracking=True)
    signature = fields.Binary(string="Signature")
    signed_on = fields.Datetime(string="Signed On")
    signed_by = fields.Char(string="Signed By")
    mail_sent_done = fields.Boolean("Mail Send")
    cyanuric_acid = fields.Float(string="Cyan-uric Acid", tracking=True)
    powder_chlorine = fields.Float(string="Powder Chlorine", help="Free Chlorine level(DPD-3)1.5 to 2.0ppm, Chemical Used and amount", tracking=True)
    tablet_chlorine = fields.Float(string="Table Chlorine", help="Free Chlorine level(DPD-3)1.5 to 2.0ppm, Chemical Used and amount", tracking=True)
    ph_plus = fields.Float(string="PH+", help="Free Chlorine level(DPD-3)1.5 to 2.0ppm, Chemical Used and amount", tracking=True)
    ph_minus = fields.Float(string="PH-", help="Free Chlorine level(DPD-3)1.5 to 2.0ppm, Chemical Used and amount", tracking=True)

    total_chlorine = fields.Float(string="Total Chlorine", help="Total Chlorine", tracking=True)
    salinity = fields.Float(string="Salinity", help="Salinity", tracking=True)
    tds = fields.Float(string="TDS", help="TDS", tracking=True)

    @api.model
    def create_from_checklist(self, args):
        task_id = args.get('task_id', False)
        user_id = args.get('user_id', False)
        employee_rec = False
        if user_id:
            employee_rec = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)], limit=1)

        if task_id:
            task_rec = self.env['project.task'].sudo().browse(task_id)
            if task_rec and task_rec.project_id.project_type_id.name == 'Service':
                checklist_id = self.env['project.checklist'].sudo().create({
                    'tds': args.get('tds'),
                    'signed_on': datetime.now(),
                    'salinity': args.get('salinity'),
                    'ph_level': args.get('ph_level'),
                    'skim_pool': args.get('skim_pool'),
                    'task_id': task_rec and task_rec.id,
                    'brush_pool': args.get('brush_pool'),
                    'signature': args.get('signature_img'),
                    'vacuum_pool': args.get('vacuum_pool'),
                    'signed_by': args.get('signature_name'),
                    'cyanuric_acid': args.get('cyanuric_acid'),
                    'total_chlorine': args.get('total_chlorine'),
                    'clean_deck_area': args.get('clean_desk_area'),
                    'total_alkalinity': args.get('total_alkalinity'),
                    'calcium_hardness': args.get('calcium_hardness'),
                    'water_temperature': args.get('water_temperature'),
                    'clean_machine_room': args.get('clean_machine_room'),
                    'free_chlorin_level': args.get('free_chlorin_level'),
                    'clean_balance_tank': args.get('clean_balance_tank'),
                    'clean_pump_strainer': args.get('clean_pump_strainer'),
                    'employee_id': employee_rec.id if employee_rec else False,
                    'clean_skimmer_overflow': args.get('clean_skimmer_overflow'),
                    'back_wash_filter_after': args.get('back_wash_filter_after'),
                    'back_wash_filter_before': args.get('back_wash_filter_before'),
                    'projects_id': task_rec and task_rec.project_id and task_rec.project_id.id or False,
                })

                mail = self.mail_sent(checklist_id)
                if mail:
                    checklist_id.write({'mail_sent_done': True})

                if checklist_id.projects_id:
                    data_lst = ['Task : %s' % (checklist_id.task_id.name), 'Employee: %s' % (checklist_id.employee_id.name), 'Date: %s' % (checklist_id.date)]
                    self.env['mail.message'].sudo().create({
                        'res_id': checklist_id.projects_id.id,
                        'model': 'project.project',
                        'body': 'Project Checklist created with details: %s' % ('\n'.join(map(str, data_lst)))
                    })

        return True

    def mail_sent(self, checklist_id):
        email_template = self.env.ref('atlas_checklist.email_template_checklist_report')
        mail_vals = {}
        report = self.env['ir.actions.report'].sudo()._render_qweb_pdf('atlas_checklist.action_report_project_checklist', res_ids=checklist_id.ids)
        filename = 'Project Checklist Automatic Report.pdf'
        attachment_ids = []
        attachment = self.env['ir.attachment'].sudo().create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(report[0]),
            'res_model': 'project.checklist',
            'res_id': checklist_id.id,
            'mimetype': 'application/pdf'
        })
        if attachment:
            attachment_ids.append((4, attachment.id))
        if email_template and attachment_ids:
            mail_vals.update({'attachment_ids': attachment_ids})
            email_template.sudo().send_mail(checklist_id.id, force_send=True, email_values=mail_vals)

        return True

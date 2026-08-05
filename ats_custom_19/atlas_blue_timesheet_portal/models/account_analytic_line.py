# -*- coding: utf-8 -*-

import base64
from datetime import datetime
from odoo import models, fields, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")
    from_portal = fields.Boolean(string="Is from Portal")
    is_signature = fields.Boolean(string="Is Signed")
    user_id = fields.Many2one('res.users', string="User")

    @api.model
    def create_from_portal(self, args):
        user_id = self._uid
        employee_rec = False
        if user_id:
            employee_rec = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)], limit=1)

        task_id = args.get('task_id', False)
        task_rec = self.env['project.task'].sudo().browse(task_id)
        analytic_line_id = args.get('analytic_line_id', False)
        if analytic_line_id:
            analytic_line_rec = self.env['account.analytic.line'].sudo().browse(eval(analytic_line_id))
        else:
            analytic_line_rec = self.env['account.analytic.line'].sudo().create({
                'employee_id': employee_rec.id,
                'project_id': task_rec and task_rec.project_id and task_rec.project_id.id or False,
                'task_id': task_rec and task_rec.id,
                'start_date': datetime.now(),
                'from_portal': True,
                'is_signature': True,
                'user_id': user_id,
            })

        return {
            'analytic_line_rec': analytic_line_rec.id,
            'start_date': fields.Datetime.context_timestamp(analytic_line_rec, analytic_line_rec.start_date),
        }

    @api.model
    def update_from_portal(self, args):
        if args.get("analytic_line_id"):
            analytic_line_rec = self.env['account.analytic.line'].sudo().browse(int(args.get("analytic_line_id")))
            if analytic_line_rec:
                delta = datetime.now() - analytic_line_rec.start_date
                worked_hours = delta.total_seconds() / 3600.0
                analytic_line_rec.write({'end_date': datetime.now(), 'unit_amount': worked_hours})
                return {
                    'analytic_line_rec': analytic_line_rec.id,
                    'end_date': fields.Datetime.context_timestamp(analytic_line_rec, analytic_line_rec.end_date),
                    'unit_amount': '{0:02.0f}:{1:02.0f}'.format(*divmod(worked_hours * 60, 60)),
                }

        return {}

    @api.model
    def submit_from_portal(self, args):
        if args.get("analytic_line_id"):
            analytic_line_rec = self.env['account.analytic.line'].sudo().browse(int(args.get("analytic_line_id")))
            if analytic_line_rec:
                analytic_line_rec.write({'name': args.get('description'), 'is_signature': False})
                self.env['employee.cost'].create({
                    'employee_id': analytic_line_rec.employee_id.id,
                    'hours_spent': analytic_line_rec.unit_amount,
                    'project_id': analytic_line_rec.task_id.project_id.id,
                    'task_id': analytic_line_rec.task_id.id,
                    'description': analytic_line_rec.name,
                })
                return {
                    'description': analytic_line_rec.name
                }

        return False


class ProjectChecklist(models.Model):
    _inherit = 'project.checklist'

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
        report = self.env['ir.actions.report']._render_qweb_pdf('atlas_checklist.action_report_project_checklist', res_ids=checklist_id.id)
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

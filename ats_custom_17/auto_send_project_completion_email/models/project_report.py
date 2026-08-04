# -*- coding: utf-8 -*-


import base64
import xlsxwriter
from io import BytesIO
from odoo import models, fields, _


class SaleOrder(models.Model):
    _inherit = 'project.project'

    filename = fields.Binary()

    def action_excel(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Project Completion')
        sheet.set_column(0, 2, 30)
        sheet.set_column(3, 4, 20)
        sheet.set_column(5, 5, 20)
        sheet.set_column(6, 10, 15)
        currency_format = workbook.add_format({'num_format': '#,###0.000'})
        cell = workbook.add_format({'bold': True})
        # Main Info
        col = 0
        sheet.write(0, col, _("Project Name"), cell)
        col += 1
        sheet.write(0, col, _("Project Code"), cell)
        col += 1
        sheet.write(0, col, _("Project Type"), cell)
        col += 1
        sheet.write(0, col, _("Sale Amount"), cell)
        col += 1
        sheet.write(0, col, _("Percentage Completion"), cell)

        row, col = 0, 0

        for line in self:
            row += 1
            # product = line.product_id
            col = 0
            sheet.write(row, col, line.name or '')
            col += 1
            sheet.write(row, col, line.number or '')
            col += 1
            sheet.write(row, col, line.project_type_id.name or '')
            col += 1
            sheet.write(row, col, line.total_so_amount,currency_format or '')
            col += 1
            sheet.write(row, col, line.total_completion_percent or '')
            col += 1

        workbook.close()
        file_base = base64.b64encode(output.getvalue())
        output.close()
        return file_base

    def _cron_project_complite_mail(self):
        project_users = self.env.ref("auto_send_project_completion_email.group_project_by_email").users
        if not project_users:
            return

        projects = self.search([], order="name")
        # report = self.env.ref('auto_send_project_completion_email.project_report_action')
        # result, format = report._render_qweb_pdf(projects.ids)
        result = projects.action_excel()
        # result = base64.b64encode(result)
        report_name = 'Project Completion Report.%s.xlsx' % str(fields.Datetime.now())
        attachments = [(report_name, result)]

        template = self.env.ref('auto_send_project_completion_email.project_complition_notification_mail_template')
        values = {'attachments': attachments}
        values['email_to'] = ",".join(project_users.mapped("email"))
        values['author_id'] = self.env.user.partner_id.id
        values['recipient_ids'] = project_users.mapped('partner_id.id')
        template.send_mail(False, force_send=True, email_values=values)

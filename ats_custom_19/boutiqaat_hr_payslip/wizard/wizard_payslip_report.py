# -*- coding: utf-8 -*-

import time
import base64
import xlsxwriter
from io import BytesIO
from odoo import models, fields, _

PAYSLIP_STATE = {
    'draft': 'Draft',
    'verify': 'Waiting',
    'done': 'Done',
    'cancel': 'Cancel',
}


class WizardPayslipReport(models.TransientModel):
    _name = 'wizard.payslip.report'
    _description = 'Payslip Wizard'

    from_date = fields.Date(string="From Date", required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    to_date = fields.Date(string="To Date", required=True, default=fields.Date.context_today)
    department_ids = fields.Many2many('hr.department', string="Departments")
    state = fields.Selection([('draft', 'Draft'), ('verify', 'Verify'), ('done', 'Done'), ('verify_done', 'Verify and Done'), ('all', 'Draft, Verify and Done')],
                             string="Payslip State", required=True, default='all')
    export_data = fields.Binary()
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)
    seperator = fields.Selection([(';', ';'), (',', ',')], string="Separator", required=True, default=",")

    def print_excel(self):
        lang_code = self.env.user.lang or 'en_US'
        date_format = self.env['res.lang']._lang_get(lang_code).date_format

        def get_date_format(date):
            return date.strftime(date_format) if date else ''

        user_from_date = get_date_format(self.from_date)
        user_to_date = get_date_format(self.to_date)

        domain = [('date_from', '>=', self.from_date), ('date_from', '<=', self.to_date), ('company_id', '=', self.company_id.id)]
        if self.department_ids:
            domain += [('employee_id.department_id', 'in', self.department_ids.ids)]

        if self.state == 'verify_done':
            domain += [('state', 'in', ['verify', 'done'])]
        elif self.state != 'all':
            domain += [('state', '=', self.state)]

        payslips_heading = [
            'S/N', 'Slip Ref.', 'Employee ID', 'English Name', 'Arabic Name', 'Nationality', 'Civil ID', 'Department', 'Job Title',
            'Joining Date', 'IBAN', 'Working Schedule', 'Monthly Days', 'Monthly Hours', 'Attendance Working Days', 'Attendance Working Hours'
        ]
        payslips_heading_after = ['Payment Method', 'Residency', 'Work Address', 'Status']
        payslip_header = {}

        payslips = self.env['hr.payslip'].search(domain)
        all_lines = payslips.mapped('line_ids.salary_rule_id')
        all_lines_sorted = sorted(all_lines, key=lambda k: k.sequence)

        payslip_total = {}
        for line in all_lines_sorted:
            code = line.code
            if code in ['EMP_INP_ALW', 'EMP_INP_DED']:
                continue

            if not payslip_header.get(code):
                payslip_header[code] = {
                    'title': line.name,
                    'sequence': line.sequence,
                    'code': code,
                }
                payslip_total.setdefault(code, 0)

        # inp_categories = payslips.mapped('emp_input_line_ids.emp_input_id.category_id')
        inp_categories = self.env['emp.input.category'].search([])
        pref_line = payslip_header.get('EMP_INP_ALW') or payslip_header.get('EMP_INP_DED') or payslip_header.get('NET')
        inp_seq = ((pref_line or {}).get('sequence') or 110) - 1

        input_categ_code_list = []
        for categ in inp_categories:
            code = categ.code
            if not payslip_header.get(code):
                input_categ_code_list.append(code)
                payslip_header[code] = {
                    'title': categ.name,
                    'sequence': inp_seq,
                    'code': code,
                }
                payslip_total.setdefault(code, 0)

        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet("%s-%s Salary" % (user_from_date, user_to_date))
        worksheet.set_column(0, 0, 5)
        worksheet.set_column(1, 1, 25)
        worksheet.set_column(2, 2, 25)
        worksheet.set_column(3, 35, 18)

        style_normal_right = workbook.add_format({'align': 'right'})
        style_bold_border = workbook.add_format({'text_wrap': 1, 'valign': 'middle', 'border': True, 'bold': True})
        style_bold_border_center = workbook.add_format({'text_wrap': 1, 'valign': 'top', 'border': True, 'bold': True, 'align': 'center'})
        style_bold_border_right = workbook.add_format({'text_wrap': 1, 'valign': 'top', 'align': 'right', 'border': True, 'bold': True})

        col = 1
        row = 2
        worksheet.write(row, col, _('From Date:'), style_bold_border)
        col += 1
        worksheet.write(row, col, user_from_date, style_bold_border)

        col = 3
        worksheet.write(row, col, _('To Date:'), style_bold_border)
        col += 1
        worksheet.write(row, col, user_to_date, style_bold_border)

        row += 1
        col = 1
        worksheet.write(row, col, _('Company:'), style_bold_border)
        col += 1
        worksheet.write(row, col, self.company_id.name, style_bold_border)

        row += 1
        col = 1
        worksheet.write(row, col, _('Printed On:'), style_bold_border)
        col += 1
        worksheet.write(row, col, get_date_format(fields.Date.today()), style_bold_border)

        # Header
        row += 2
        col = 0
        start_row = row
        table_header_line = payslips_heading
        for heading in payslips_heading:
            worksheet.write(row, col, heading, style_bold_border_center)
            col += 1

        alw_ded_header = []
        for code, header in payslip_header.items():
            worksheet.write(row, col, header['title'], style_bold_border_center)
            table_header_line.append(header['title'])
            alw_ded_header.append(code)
            col += 1

        table_header_line += payslips_heading_after
        for heading in payslips_heading_after:
            worksheet.write(row, col, heading, style_bold_border_center)
            col += 1

        row += 1
        col = 0

        emp_data = {}
        count = 0
        col_total = 0
        for slip in payslips:
            count += 1
            emp = slip.employee_id
            if not emp_data.get(emp.id):
                calendar = emp.resource_calendar_id
                emp_data.update({
                    emp.id: {
                        'identification_id': emp.identification_id,
                        'name': emp.name,
                        'arabic_name': emp.arabic_name,
                        'nationality': emp.country_id.name,
                        'civil_id': emp.civil_id,
                        'department': emp.department_id.name,
                        'job_title': emp.job_id.name,
                        'joining_date': emp.date_joining,
                        'iban': emp.iban_number,
                        'working_schedule': calendar.name,
                        'month_days': slip.contract_id.month_days or 26,
                        'tot_monthly_hours': slip.contract_id.tot_monthly_hours or 208,
                        'pay_through': (emp.pay_through or '').capitalize(),
                        'private_address': emp.private_address,
                        'work_address': emp.work_address,
                        'state': PAYSLIP_STATE.get(slip.state),
                    }
                })

            col = 0
            worksheet.write(row, col, count)
            col += 1
            worksheet.write(row, col, slip.number or '')
            col += 1
            worksheet.write(row, col, emp_data[emp.id]['identification_id'] or '')
            col += 1
            worksheet.write(row, col, emp_data[emp.id]['name'] or '')
            col += 1
            worksheet.write(row, col, emp_data[emp.id]['arabic_name'] or '')
            col += 1
            worksheet.write(row, col, emp_data[emp.id]['nationality'] or '')
            col += 1
            worksheet.write(row, col, emp_data[emp.id]['civil_id'] or '')
            col += 1
            worksheet.write(row, col, emp_data[emp.id]['department'] or '')
            col += 1
            worksheet.write(row, col, emp_data[emp.id]['job_title'] or '')
            col += 1
            worksheet.write(row, col, get_date_format(emp_data[emp.id]['joining_date'] or ''))
            col += 1
            worksheet.write(row, col, emp_data[emp.id]['iban'] or '')
            col += 1
            worksheet.write(row, col, emp_data[emp.id]['working_schedule'] or '')
            col += 1
            worksheet.write(row, col, emp_data[emp.id]['month_days'], style_normal_right)
            col += 1
            worksheet.write(row, col, emp_data[emp.id]['tot_monthly_hours'], style_normal_right)
            col += 1

            worked_lines = slip.worked_days_line_ids.filtered(lambda r: r.code == "WORK100")
            days_qty = sum(worked_lines.mapped('number_of_days'))
            w_days = w_hours = 0
            if slip.struct_id.is_without_attendance:
                w_days = slip.employee_id.contract_id.month_days or 26
                w_hours = slip.employee_id.contract_id.tot_monthly_hours or 208
            else:
                if days_qty:
                    actual_days = emp_data[emp.id]['month_days']
                    w_days = actual_days - (slip.calendar_working_days - days_qty)

                hours_qty = sum(worked_lines.mapped('number_of_hours'))
                if hours_qty:
                    actual_hours = emp_data[emp.id]['tot_monthly_hours']
                    w_hours = actual_hours - (slip.calendar_working_hours - hours_qty)

            worksheet.write(row, col, w_days, style_normal_right)
            col += 1
            worksheet.write(row, col, round(w_hours, 3), style_normal_right)
            col += 1

            col_total = col
            for code in alw_ded_header:
                if code in ['EMP_INP_ALW', 'EMP_INP_DED'] and slip.emp_input_line_ids:
                    continue
                elif code in input_categ_code_list:
                    amount = sum(slip.emp_input_line_ids.filtered(lambda l: l.categ_code == code).mapped('amount'))
                    # for input_line in :
                    amount = round(amount, 3)
                    payslip_total[code] += amount
                    worksheet.write(row, col, amount, style_normal_right)
                    col += 1
                else:
                    amount = slip._get_salary_line_total(code)
                    payslip_total[code] += amount
                    worksheet.write(row, col, amount, style_normal_right)
                    col += 1

            worksheet.write(row, col, emp_data[emp.id]['pay_through'] or '')
            col += 1
            worksheet.write(row, col, emp_data[emp.id]['private_address'] or '')
            col += 1
            worksheet.write(row, col, emp_data[emp.id]['work_address'] or '')
            col += 1
            worksheet.write(row, col, emp_data[emp.id]['state'] or '')
            col += 1
            row += 1

        row += 1
        col = col_total
        for code, header in payslip_header.items():
            worksheet.write(row, col, payslip_total[code], style_bold_border_right)
            col += 1

        table = []
        for header_line in table_header_line:
            col = {'header': header_line}
            table.append(col)

        worksheet.add_table(start_row, 0, row + 1, len(table_header_line) - 1, {
            'total_row': 1,
            'columns': table,
            'style': 'Table Style Light 9',
            'first_column': True,
        })
        workbook.close()
        export_data = base64.b64encode(fp.getvalue())
        fp.close()

        self.write({"export_data": export_data})

        file_name = "%s-To-%s-Payslips.xls" % (self.from_date, self.to_date)
        return {
            'target': 'new',
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s/%s/%s/%s?download=true' % (self._name, self.id, 'export_data', file_name),
        }

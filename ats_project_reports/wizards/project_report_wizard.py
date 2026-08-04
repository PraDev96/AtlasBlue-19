# -*- coding: utf-8 -*-

import io
import re
import base64
import xlsxwriter
from odoo import models, fields, _, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class ProjectReportWizard(models.TransientModel):
    _name = 'project.report.wizard'
    _description = "Project Report Wizard"

    period_type = fields.Selection([
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('quarterly', 'Quarterly Report'),
        ('custom_period', 'Custom Period Report')
    ], string="Period Type", default='daily', required=True)
    date_from = fields.Date(string="From Date", default=fields.Date.context_today)
    date_to = fields.Date(string="To Date", default=fields.Date.context_today)
    exclude_employee_ids = fields.Many2many('hr.employee', string="Exclude Employees")
    excel_file = fields.Binary(string="Excel Report")
    file_name = fields.Char(string="File Name")

    @api.constrains('date_from', 'date_to')
    def _check_project_report_from_to_date(self):
        for report in self:
            if report.period_type == 'daily' and report.date_from > fields.Date.today():
                raise ValidationError(_("Sorry!!! I am not Able to Predict the Future Daily Report!!!.") + "\n" + _("Please Choose the Past or Present Date."))
            if report.period_type == 'custom_period' and report.date_to < report.date_from:
                raise ValidationError(_("The 'To Date' cannot be earlier than the 'From Date'!"))

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['exclude_employee_ids'] = [(4, 99)]

        return defaults

    @api.onchange('period_type')
    def _onchange_period_type(self):
        today = fields.Date.context_today(self)
        if self.period_type == 'daily':
            self.date_from = today
            self.date_to = today
        elif self.period_type == 'weekly':
            weekday = today.weekday()
            days_to_sunday = (weekday + 1) % 7
            start_date = today - timedelta(days=days_to_sunday)
            end_date = start_date + timedelta(days=6)
            self.date_from = start_date
            self.date_to = end_date
        elif self.period_type == 'monthly':
            self.date_from = today.replace(day=1)
            self.date_to = self.date_from + relativedelta(months=1, days=-1)
        elif self.period_type == 'quarterly':
            quarter = (today.month - 1) // 3
            self.date_from = datetime(today.year, 3 * quarter + 1, 1).date()
            self.date_to = self.date_from + relativedelta(months=3, days=-1)
        else:
            self.date_from = False
            self.date_to = False

    def _process_project_number(self, project_name):
        if not project_name:
            return 'Unknown'

        clean_text = str(project_name).strip()
        if not clean_text or clean_text == '0' or clean_text == '0.00':
            return 'Unknown'

        patterns = [
            r'^0*(\d{4,5})\s*[-–—]?\s*.*?\s*\(([^)]+)\)',
            r'^0*(\d{4,5})\s*\(([A-D])\)',
            r'^0*(\d{4,5})\s*[-–—]?\s*.+',
            r'^0*(\d{4,5})$'
        ]
        for pattern in patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                project_no = match.group(1).lstrip('0')
                suffix = ''
                if len(match.groups()) >= 2 and match.group(2):
                    suffix = ' ' + match.group(2).upper()
                return project_no + suffix

        number_match = re.search(r'\b0*(\d{4,5})\b', clean_text)
        if number_match:
            return number_match.group(1).lstrip('0')

        return clean_text

    def _process_stage(self, stage_str):
        if not stage_str:
            return ''
        stage = stage_str.lower().strip()
        stage_map = {
            'embedded piping': 'Embedded Piping',
            'embedded': 'Embedded Piping',
            'piping': 'Embedded Piping',
            'site inspection': 'Embedded Piping',
            'material request': 'Embedded Piping',
            'material delivery': 'Embedded Piping',
            'works before waterproofing': 'Works Before WP',
            'works before water-proofing': 'Works Before WP',
            'works before water proofing': 'Works Before WP',
            'before waterproofing': 'Works Before WP',
            'before water-proofing': 'Works Before WP',
            'before water proofing': 'Works Before WP',
            'works before wp': 'Works Before WP',
            'works before w/p': 'Works Before WP',
            'before wp': 'Works Before WP',
            'before w/p': 'Works Before WP',
            'pool fittings installations': 'Works Before WP',
            'light work': 'Works Before WP',
            'control switch installation': 'Works Before WP',
            'pipe extention': 'Works Before WP',
            'waterproofing': 'Waterproofing',
            'water proofing': 'Waterproofing',
            'water-proofing': 'Waterproofing',
            'w/p': 'Waterproofing',
            'site preparation': 'Waterproofing',
            'tiling': 'Tiling',
            'tile': 'Tiling',
            'tiles': 'Tiling',
            'water removing': 'Tiling',
            'plastering': 'Tiling',
            'tiles delivery': 'Tiling',
            'grouting': 'Tiling',
            'fittings': 'Fittings Installation',
            'fittings installation': 'Fittings Installation',
            'lights': 'Fittings Installation',
            'lighting': 'Fittings Installation',
            'inlets': 'Fittings Installation',
            'control switch': 'Fittings Installation',
            'ladder': 'Fittings Installation',
            'deck box': 'Fittings Installation',
            'eqsi': 'EQSI',
            'equipment': 'EQSI',
            'mechanical': 'EQSI',
            'material installation': 'EQSI',
            'equipment delivery': 'EQSI',
            'electrical installation': 'EQSI',
            'commissioning': 'Commissioning',
            'commission': 'Commissioning',
            'start the system': 'Commissioning',
            'handover': 'Handover',
            'hand over': 'Handover',
            'warranty': 'Warranty',
            'warrenty': 'Warranty',
            'warranty period': 'Warranty',
            'concrete': 'Concrete Works',
            'concrete works': 'Concrete Works',
            'blinding': 'Concrete Works',
            'external waterproofing': 'Concrete Works',
            'reinforcement': 'Concrete Works',
            'floor casting': 'Concrete Works',
            'slab casting': 'Concrete Works',
            'seat works': 'Concrete Works',
        }
        if stage in stage_map:
            return stage_map[stage]

        for keyword, mapped_stage in stage_map.items():
            if keyword in stage:
                return mapped_stage

        return stage_str

    def _get_stage_column(self, stage_text):
        if not stage_text:
            return -1

        stage = stage_text.lower()
        # Mapping from JS getStageColumn
        if any(kw in stage for kw in ['embedded piping', 'piping', 'embedded', 'site inspection', 'material request']): return 10
        if any(kw in stage for kw in
               ['works before', 'before wp', 'works before waterproofing', 'before waterproofing', 'before w/p', 'pool fittings installation', 'light work',
                'control switch installation', 'pipe extension']): return 11
        if any(kw in stage for kw in ['waterproofing', 'water proofing', 'w/p', 'site preparation']): return 12
        if any(kw in stage for kw in ['tiling', 'tile', 'tiles', 'water removing', 'plastering', 'tiles delivery', 'grouting']): return 13
        if any(kw in stage for kw in ['fittings', 'lights', 'acrylic', 'lighting', 'inlets', 'control switch', 'ladder', 'deck box']): return 14
        if any(kw in stage for kw in ['eqsi', 'equipment', 'mechanical', 'equipment delivery', 'electrical installation']): return 15
        if any(kw in stage for kw in ['commissioning', 'commission', 'start the system']): return 16
        if any(kw in stage for kw in ['handover', 'hand over']): return 17
        if any(kw in stage for kw in ['warranty', 'warrenty']): return 18
        if any(kw in stage for kw in ['site inspection', 'inspection', 'site meeting', 'meeting']): return 20

        return -1

    def _get_employee_info(self, employee):
        # Hardcoded PMs, TLs, CEs from the script
        pms = [
            {'fullName': "Gino Edward", 'pmNo': "PM-1", 'shortName': "PM-GE"},
            {'fullName': "Dinesh Chadayan", 'pmNo': "PM-2", 'shortName': "PM-DC"},
            {'fullName': "Dharman Koottungal Balan", 'pmNo': "DW-1", 'shortName': "DW-DK"}
        ]
        tls = [
            {'fullName': "Soju Kunjumole Rajan", 'tlNumber': "T1", 'tlShortName': "TL-SR"},
            {'fullName': "Padam Raj Giri", 'tlNumber': "T2", 'tlShortName': "TL-PA"},
            {'fullName': "Subh Karan Harizan", 'tlNumber': "T3", 'tlShortName': "TL-SH"},
            {'fullName': "Prem Bahadur Devkota", 'tlNumber': "T4", 'tlShortName': "TL-PB"},
            {'fullName': "Selvakannan Selva Nadar", 'tlNumber': "T5", 'tlShortName': "TL-SK"},
            {'fullName': "Sajeehan Raman Cheleri", 'tlNumber': "T6", 'tlShortName': "TL-SA"},
            {'fullName': "Dhanna Ram Bhana Ram", 'tlNumber': "T7", 'tlShortName': "TL-DB"},
            {'fullName': "Binod Kumar Chaudhary", 'tlNumber': "T8", 'tlShortName': "TL-BK"},
            {'fullName': "Prabin Rai", 'tlNumber': "T9", 'tlShortName': "TL-PR"},
            {'fullName': "Raj Kumar Kapar", 'tlNumber': "T10", 'tlShortName': "TL-RJ"},
            {'fullName': "Bir Bahadur Gurung", 'tlShortName': "SU-BB"}
        ]
        ces = [
            {'fullName': "Abusamra Muhammed Muhammed Ibrahim Samra", 'ceNo': "CE-1", 'shortName': "CE-AS"},
            {'fullName': "Paul Amogema", 'ceNo': "CE-2", 'shortName': "CE-PA"}
        ]

        name = employee.name.lower().strip()
        for pm in pms:
            if pm['fullName'].lower().strip() == name:
                return {'info': pm, 'type': 'pm'}

        for tl in tls:
            if tl['fullName'].lower().strip() == name:
                return {'info': tl, 'type': 'tl'}

        for ce in ces:
            if ce['fullName'].lower().strip() == name:
                return {'info': ce, 'type': 'ce'}

        return {'info': None, 'type': 'other'}

    def _calculate_team_number(self, pm_no, tl_short_name):
        if not pm_no or not tl_short_name:
            return 'Unknown'

        match = re.search(r'(\d+)$', pm_no)
        if not match:
            return 'Unknown'

        pm_num = match.group(1)
        prefix = 'PM' if pm_no.startswith('PM') else 'DW' if pm_no.startswith('DW') else 'PM'
        if tl_short_name.startswith('SU-'):
            return f"{prefix}{pm_num}-SU"

        # Mapping TL short name to T number
        tl_map = {
            "TL-SR": "T1", "TL-PA": "T2", "TL-SH": "T3", "TL-PB": "T4", "TL-SK": "T5",
            "TL-SA": "T6", "TL-DB": "T7", "TL-BK": "T8", "TL-PR": "T9", "TL-RJ": "T10"
        }
        t_num = tl_map.get(tl_short_name, 'Unknown').replace('T', '')
        return f"{prefix}{pm_num}-T{t_num}"

    def _get_time_format(self, formats, quantity):
        if not isinstance(quantity, (int, float)):
            return formats['data']

        total_minutes = quantity * 60
        if total_minutes >= 540:
            return formats['time_critical']
        elif total_minutes >= 480:
            return formats['time_high']
        elif 0 <= total_minutes < 5:
            return formats['time_critical']
        elif 5 <= total_minutes <= 10:
            return formats['time_high']
        elif 10 < total_minutes <= 480:
            return formats['time_med']

        return formats['time_data']

    def action_print_excel(self):
        domain = [("department_id", "in", [133, 143]), ("task_id", "not ilike", "Time Off")]
        if self.exclude_employee_ids:
            domain.append(("employee_id", "not in", self.exclude_employee_ids.ids))
        if self.period_type == 'daily':
            domain.append(('date', '=', self.date_from))
        else:
            domain.extend([('date', '<=', self.date_to), ('date', '>=', self.date_from)])

        # TimesheetEntries = self.env['account.analytic.line'].sudo().search(domain, order='date asc')
        TimesheetEntries = self.env['account.analytic.line'].sudo().search(domain)
        if not TimesheetEntries:
            raise ValidationError(_("There is no Timesheet entry for Project Report, for the chosen Date!"))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet_name = "Project Report - " + str(self.date_from.strftime('%d-%m-%Y'))
        sheet = workbook.add_worksheet(sheet_name)

        # Pre-define Formats to avoid loop creation
        formats = {
            'data': workbook.add_format({'border': 1}),
            'title': workbook.add_format({'bold': True, 'font_size': 14}),
            'subtitle': workbook.add_format({'bold': True, 'font_size': 12}),
            'date': workbook.add_format({'border': 1, 'num_format': 'dd-mm-yyyy'}),
            'time_data': workbook.add_format({'border': 1, 'num_format': '[h]:mm'}),
            'light_green': workbook.add_format({'bg_color': '#d6ecd2', 'border': 1}),
            'period': workbook.add_format({'bold': True, 'align': 'left', 'font_size': 12}),
            'time_med': workbook.add_format({'bg_color': '#ffffcc', 'border': 1, 'num_format': '[h]:mm'}),
            'time_high': workbook.add_format({'bg_color': '#ffe6e6', 'border': 1, 'num_format': '[h]:mm'}),
            'time_critical': workbook.add_format({'bg_color': '#ffcccc', 'bold': True, 'border': 1, 'num_format': '[h]:mm'}),
            'ts_header': workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D9D9D9', 'border': 1, 'text_wrap': True}),
        }

        header_colors = [
            '#BFBFBF', '#BFBFBF', '#BFBFBF', '#BFBFBF', '#BFBFBF', '#BFBFBF', '#BFBFBF', '#E2EFDA', '#FFF2CC', '#DDEBF7', '#E4DFEC',
            '#DAEEF3', '#F2DCDB', '#FFFFCC', '#FDEADA', '#D9E1F2', '#EBF1DE', '#F2DCDB', '#BFBFBF', '#BFBFBF', '#BFBFBF', '#BFBFBF',
        ]
        color_formats = {color: workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': color, 'border': 1, 'text_wrap': True
        }) for color in set(header_colors)}

        # JS-style Title section
        date_from_str = self.date_from.strftime('%d/%m/%Y') if self.date_from else ''
        date_to_str = self.date_to.strftime('%d/%m/%Y') if self.date_to else ''

        sheet.write(0, 0, 'MIS-11-DR', formats['title'])
        sheet.write(1, 0, 'DAILY REPORT', formats['subtitle'])
        if self.period_type == 'daily':
            report_period = date_from_str
        else:
            report_period = date_from_str + ' to ' + date_to_str
        sheet.write(2, 0, f"Report Period: {report_period}", formats['period'])

        # Section 1: Timesheet Activity
        row = 4
        # Aggregate entries for summary section
        # We group by Date, Employee, Project, and Stage
        aggregated = {}
        processed_entries = []

        for timesheet in TimesheetEntries:
            # Key for summary aggregation
            stage_name = timesheet.task_id.stage_id.name if timesheet.task_id and timesheet.task_id.stage_id else ''
            key = (timesheet.date, timesheet.employee_id.id, timesheet.project_id.name, stage_name)
            if key not in aggregated:
                aggregated[key] = {
                    'quantity': 0.0,
                    'description': '',
                    'stage': stage_name,
                    'date': timesheet.date,
                    'employee': timesheet.employee_id,
                    'project_name': timesheet.project_id.name,
                    'task': timesheet.task_id.name if timesheet.task_id else '',
                    'task_assignees': ", ".join(timesheet.task_id.user_ids.mapped('name')) if timesheet.task_id else ''
                }
            entry = aggregated[key]
            entry['quantity'] += round(timesheet.unit_amount, 2)
            # Sum unit_amount for the same Project/Stage/Employee/Date
            line_desc = timesheet.name or ''
            if line_desc:
                if entry['description']:
                    if line_desc not in entry['description']:
                        entry['description'] += ' / ' + line_desc
                else:
                    entry['description'] = line_desc

        processed_entries = list(aggregated.values())

        status_headers = [
            'Date', 'Project No.', 'P.M./CE No.', 'P.M. Name', 'Team No.', 'Team Leader', 'Contract Status', 'Design Status', 'Concrete Works',
            'Stage-1 Embedded Piping', 'Stage-2 Works Before WP', 'Water Proofing', 'Tiling Works', 'Fittings Installation', 'Stage-3 EQSI',
            'Commissioning', 'Handover', 'Works during Warranty Period', 'Status', "Client's Comments/ Complaints", 'Checklist No.', 'Remarks'
        ]
        # Adjust row height based on longest header
        status_max_lines = max([(len(h) - 1) // 15 + 1 for h in status_headers])
        sheet.set_row(row, status_max_lines * 35 + 10)  # 15 points per line + padding

        for col_num, (header, color) in enumerate(zip(status_headers, header_colors)):
            # Set explicit width for all summary columns
            width = 10 if col_num == 0 else 8
            sheet.set_column(col_num, col_num, width)
            sheet.write(row, col_num, header, color_formats[color])

        # Grouping and Sorting
        order = ['PM-1', 'PM1-T1', 'PM1-T2', 'PM1-T3', 'PM1-T4', 'PM1-T5', 'PM1-T6', 'PM1-T7', 'PM1-T8', 'PM1-T9', 'PM1-T10', 'PM1-SU', 'CE-1',
                 'PM-2', 'PM2-T1', 'PM2-T2', 'PM2-T3', 'PM2-T4', 'PM2-T5', 'PM2-T6', 'PM2-T7', 'PM2-T8', 'PM2-T9', 'PM2-T10', 'PM2-SU', 'CE-2', 'DW-1']
        grouped = {k: [] for k in order}
        grouped['other'] = []

        for entry in processed_entries:
            emp_info = self._get_employee_info(entry['employee'])
            group_key = 'other'
            if emp_info['type'] == 'pm':
                group_key = emp_info['info']['pmNo']
            elif emp_info['type'] == 'ce':
                group_key = emp_info['info']['ceNo']
            elif emp_info['type'] == 'tl':
                pm_no = 'Unknown'
                for pm_name in ['Gino Edward', 'Dinesh Chadayan', 'Dharman Koottungal Balan']:
                    if pm_name.lower() in entry['task_assignees'].lower():
                        if 'Gino' in pm_name:
                            pm_no = 'PM-1'
                        elif 'Dinesh' in pm_name:
                            pm_no = 'PM-2'
                        elif 'Dharman' in pm_name:
                            pm_no = 'DW-1'
                        break
                group_key = self._calculate_team_number(pm_no, emp_info['info'].get('tlShortName', ''))

            if group_key not in grouped:
                grouped[group_key] = []
            grouped[group_key].append(entry)

        data_row = row + 1
        for key in order + ['other']:
            for entry in grouped[key]:
                emp_info = self._get_employee_info(entry['employee'])
                time_fmt = self._get_time_format(formats, entry['quantity'])

                # Pre-fill all status columns with borders
                for c in range(22):
                    sheet.write(data_row, c, '', formats['data'])

                sheet.write(data_row, 0, entry['date'], formats['date'])
                sheet.write(data_row, 1, self._process_project_number(entry['project_name']), formats['data'])

                if emp_info['type'] == 'pm':
                    sheet.write(data_row, 2, emp_info['info']['pmNo'], formats['data'])
                    sheet.write(data_row, 3, emp_info['info']['shortName'], formats['data'])
                    if emp_info['info']['pmNo'] == 'DW-1':
                        sheet.write(data_row, 7, entry['quantity'] / 24.0, time_fmt)
                        sheet.write(data_row, 6, '', formats['light_green'])
                elif emp_info['type'] == 'ce':
                    sheet.write(data_row, 2, emp_info['info']['ceNo'], formats['data'])
                    sheet.write(data_row, 3, emp_info['info']['shortName'], formats['data'])
                elif emp_info['type'] == 'tl':
                    pm_no = 'Unknown'
                    pm_short = ''
                    for pm_data in [{'name': 'Gino Edward', 'no': 'PM-1', 'short': 'PM-GE'}, {'name': 'Dinesh Chadayan', 'no': 'PM-2', 'short': 'PM-DC'},
                                    {'name': 'Dharman Koottungal Balan', 'no': 'DW-1', 'short': 'DW-DK'}]:
                        if pm_data['name'].lower() in entry['task_assignees'].lower():
                            pm_no = pm_data['no']
                            pm_short = pm_data['short']
                            break
                    sheet.write(data_row, 2, pm_no, formats['data'])
                    sheet.write(data_row, 3, pm_short, formats['data'])
                    sheet.write(data_row, 4, self._calculate_team_number(pm_no, emp_info['info'].get('tlShortName', '')), formats['data'])
                    sheet.write(data_row, 5, emp_info['info'].get('tlShortName', ''), formats['data'])

                # Requirement: Sum of unit_amount for Concrete Works, else 'By Client'
                stage = self._process_stage(entry['stage'] or entry['task'])
                raw_stage = (entry['stage'] or '').lower()
                is_concrete = stage == 'Concrete Works' or 'concrete works' in raw_stage
                if is_concrete:
                    sheet.write(data_row, 8, entry['quantity'] / 24.0, time_fmt)
                    # Highlight preceding columns light green
                    for c in range(6, 8):
                        sheet.write(data_row, c, '', formats['light_green'])
                else:
                    # Explicitly set 'By Client' for non-concrete work rows in column 8
                    sheet.write(data_row, 8, "By Client", formats['data'])

                is_acrylic = 'acrylic' in stage.lower()
                if is_acrylic:
                    sheet.write(data_row, 13, entry['quantity'] / 24.0, time_fmt)
                    for c in range(6, 13):
                        val = 'By Client' if c == 8 else ''
                        sheet.write(data_row, c, val, formats['light_green'])

                if not is_concrete and not is_acrylic:
                    col = self._get_stage_column(stage)
                    if col > 0:
                        sheet.write(data_row, col - 1, entry['quantity'] / 24.0, time_fmt)
                        for c in range(6, col - 1):
                            val = 'By Client' if c == 8 else ''
                            sheet.write(data_row, c, val, formats['light_green'])

                remarks = entry['description'].strip()
                if remarks and not re.match(r'^[/\\\-_]+$', remarks):
                    remarks = remarks.lstrip('/\\-_ ').capitalize()
                    sheet.write(data_row, 21, remarks, formats['data'])

                data_row += 1

        workbook.close()
        output.seek(0)
        self.excel_file = base64.b64encode(output.read())
        self.file_name = f'Project-{self.get_report_file_name()}-Report.xlsx'
        output.close()

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model={self._name}&id={self.id}&field=excel_file&download=true&filename={self.file_name}',
            'target': 'self',
        }

    def get_report_file_name(self):
        if self.period_type == 'daily':
            file_name = "Daily"
        elif self.period_type == 'weekly':
            file_name = "Weekly"
        elif self.period_type == 'monthly':
            file_name = "Monthly"
        elif self.period_type == 'quarterly':
            file_name = "Quarterly"
        else:
            file_name = str(self.date_from.strftime('%d/%m/%Y')) + '-to-' + str(self.date_to.strftime('%d/%m/%Y'))

        return file_name

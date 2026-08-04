# -*- coding: utf-8 -*-

import base64
import xlsxwriter
from io import BytesIO
from odoo import models, fields,  _


class FleetHandoverWizard(models.TransientModel):
    _name = 'fleet.handover.wizard'
    _description = "fleet.handover.wizard"

    start_date = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    end_date = fields.Date(string="To Date", required=True, default=fields.Date.today)
    filename = fields.Binary()
    fleet_vehicle_ids = fields.Many2many('fleet.vehicle', string="Vehicle")

    def get_lang_format(self):
        lang_code = self.env.user.lang or 'en_US'
        return self.env['res.lang']._lang_get(lang_code).date_format

    def get_date_format(self, dt, date_format=False):
        if not date_format:
            date_format = self.get_lang_format()

        return dt.strftime(date_format) if dt else ''

    def get_fleet_handover_data(self):
        domain = [('date', '>=', self.start_date), ('date', '<=', self.end_date)]
        if self.fleet_vehicle_ids.ids:
            domain += [('fleet_vehicle_id', 'in', self.fleet_vehicle_ids.ids)]

        fleet_handover = self.env['fleet.handover'].search(domain)
        handover_data = []
        counter = 1
        for handover in fleet_handover:
            handover_data.append({
                'fleet_vehilce_id': handover.fleet_vehicle_id.display_name,
                'assign_to': handover.custody_receiver_id.display_name or '',
                'date': self.get_date_format(handover.date) or '',
            })
            counter += 1

        return handover_data

    def print_all_pdf(self):
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        # data['form'] = self.read(['employee_id', 'date'])[0]
        handover_data = self.get_fleet_handover_data()
        data['handover_data'] = handover_data
        return self.env.ref('fleet_handover.action_report_vehical_assignation').sudo().report_action(self, data=data)

    def print_excel(self):
        self.ensure_one()
        return self.get_handover_detail()

    def get_handover_detail(self):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)

        style_bold_border = workbook.add_format({'text_wrap': False, 'valign': 'middle', 'bold': True})
        style_title = workbook.add_format({'text_wrap': False, 'valign': 'top', 'bold': True, 'align': 'center'})

        worksheet = workbook.add_worksheet('')
        worksheet.set_column("A:E", 13)

        row = 1
        col = 2
        worksheet.write(row, col, _('Vehicle Assignation'), style_title)

        # start_date = self.start_date.strftime('%Y-%m-%d') + ' 00:00:00'
        # end_date = self.end_date.strftime('%Y-%m-%d') + ' 23:59:59'

        row += 1
        col = 0
        worksheet.write(row, col, _('Start Date:'), style_bold_border)
        col += 1
        worksheet.write(row, col, self.get_date_format(self.start_date), style_bold_border)
        col += 2
        worksheet.write(row, col, _('End Date:'), style_bold_border)
        col += 1
        worksheet.write(row, col, self.get_date_format(self.end_date), style_bold_border)

        row += 2
        handover_datas = self.get_fleet_handover_data()

        header_line = [
            {'name': _('Vehicle Name'), 'larg': 10, 'col': {}},
            {'name': _('Assignation To'), 'larg': 30, 'col': {}},
            {'name': _('Date'), 'larg': 30, 'col': {}},
        ]

        for j, h in enumerate(header_line):
            worksheet.set_column(j, j, h['larg'])

        table = []
        for h in header_line:
            col = {}
            col['header'] = h['name']
            col.update(h['col'])
            table.append(col)

        def add_handover_lines(row, handover):
            col = 0
            worksheet.write(row, col, handover.get('fleet_vehilce_id', ''))
            col += 1
            worksheet.write(row, col, handover.get('assign_to', ''))
            col += 1
            self.get_date_format(self.start_date)
            worksheet.write(row, col, handover.get('date', ''))
            col += 1

        row += 2
        start_row = row
        row += 1

        for handover_data in handover_datas:
            add_handover_lines(row, handover_data)
            row += 1

        worksheet.add_table(start_row - 1, 0, row + 1, len(header_line) - 1, {
            'total_row': 1,
            'columns': table,
            'style': 'Table Style Light 9',
            'first_column': True,
        })

        workbook.close()
        file_base = base64.b64encode(fp.getvalue())
        fp.close()
        self.filename = file_base

        file_name = 'VEHICLE.xlsx'
        return {
            'target': 'new',
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s/%s/%s/%s?download=true'
            % (self._name, self.id, 'filename', file_name),
        }

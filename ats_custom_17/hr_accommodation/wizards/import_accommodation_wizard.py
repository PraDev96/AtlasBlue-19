# -*- coding: utf-8 -*-

import xlrd
import base64
from odoo import models, fields


class ImportAccommodationWizard(models.TransientModel):
    _name = 'import.accommodation.wizard'
    _description = "import.accommodation.wizard"

    file = fields.Binary(string="File")
    filename = fields.Char(string="Filename")

    def import_partner(self):
        self.ensure_one()
        Accommodation = self.env['hr.accommodation']
        Employee = self.env['hr.employee']
        Building = self.env['hr.building']
        # Room = self.env['hr.room']
        Floor = self.env['hr.floor']
        Flat = self.env['hr.flat']
        Bed = self.env['hr.bed']
        Room = self.env['hr.room']
        # Company = self.env['res.company']

        skipped_lines = []
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))

        counter = 0
        for sheet in wb.sheets():
            for r in range(1, sheet.nrows):
                data = sheet.row_values(r)

                print("data::::::::;", data)
                employee_id = data[0]
                employee_name = data[1]
                area = str(data[2]).split('.')[0]
                block = str(data[3]).split('.')[0]
                street = str(data[4]).split('.')[0]

                building = data[5]
                flat = data[6]
                floor = data[7]
                bed = data[8]
                room = data[9]
                # company = data[10]
                building_number = data[10]

                if employee_id:
                    employee = Employee.search([('identification_id', '=', str(employee_id).strip())], limit=1)
                    if not employee:
                        employee = Employee.search([('name', '=', str(employee_name).strip())], limit=1)

                    if not employee:
                        skipped_lines.append(data)

                    if not employee or building == '=#N/A' or building in ('10000', '10000.0', 10000, 10000.0, 0, 0.0):
                        continue

                    # building
                    building_id = Building.search([('name', '=', str(building).strip())], limit=1)
                    if not building_id:
                        building_id = Building.create({
                            'name': str(building).strip(),
                            'number': str(int(building_number)).strip(),
                        })

                    flat = str(flat).split('.')[0]
                    flat_id = Flat.search([('name', '=', flat), ('building_id', '=', building_id.id)], limit=1)
                    if not flat_id:
                        flat_id = Flat.create({
                            'name': flat,
                            'building_id': building_id.id
                        })

                    floor = str(floor).split('.')[0]
                    floor_id = Floor.search([('name', '=', floor), ('building_id', '=', building_id.id), ('flat_id', '=', flat_id.id)], limit=1)
                    if not floor_id:
                        floor_id = Floor.create({
                            'name': floor,
                            'building_id': building_id.id,
                            'flat_id': flat_id.id,
                        })

                    bed = str(bed).split('.')[0]
                    bed_id = Bed.search([('name', '=', bed), ('building_id', '=', building_id.id), ('flat_id', '=', flat_id.id), ('floor_id', '=', floor_id.id)], limit=1)
                    if not bed_id:
                        bed_id = Bed.create({
                            'name': bed,
                            'building_id': building_id.id,
                            'flat_id': flat_id.id,
                            'floor_id': floor_id.id,
                        })

                    room = str(room).split('.')[0]
                    room_id = Room.search([('name', '=', room), ('building_id', '=', building_id.id), ('flat_id', '=', flat_id.id)], limit=1)
                    if not room_id:
                        room_id = Room.create({
                            'name': room,
                            'building_id': building_id.id,
                            'flat_id': flat_id.id,
                        })

                    if building_id and flat_id and floor_id and room_id:
                        vals = {
                            'employee_id': employee.id,
                            'building_id': building_id.id,
                            'flat_id': flat_id.id,
                            'floor_id': floor_id.id,
                            'bed_id': bed_id.id,
                            # 'company_id': company_id.id,
                            'area': area,
                            'block': block,
                            'street': street,
                        }
                        Accommodation.create(vals)

                    counter += 1

        return {'type': 'ir.actions.act_window_close'}

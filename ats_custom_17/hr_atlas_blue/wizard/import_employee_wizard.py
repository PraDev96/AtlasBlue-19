# -*- coding: utf-8 -*-

import xlrd
import base64
import logging
from datetime import datetime
from odoo import models, fields
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)
company_id = 2


class ImportRentalEmployeeWizard(models.TransientModel):
    _name = 'import.rental.employee.wizard'
    _description = "Employee Wizard"

    file = fields.Binary(string="File")
    name = fields.Char(string="File Name")

    def import_data(self):
        self.ensure_one()
        Employee = self.env['hr.employee']
        Job = self.env['hr.job']
        Bank = self.env['res.bank']
        Project = self.env['project.project']
        FleetRestaurant = self.env['fleet.restaurant']
        Partner = self.env['res.partner']
        Contract = self.env['hr.contract']

        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
        for sheet in wb.sheets():
            for r in range(1, sheet.nrows):
                data = sheet.row_values(r)

                name = str(data[2]).strip()
                identification_id = str(data[1]).strip()
                if identification_id:
                    aa = str(identification_id).split('.')
                    identification_id = str(aa[0])

                emp = Employee.search([('identification_id', '=', identification_id), ('name', '=', name)], limit=1)
                # if emp:
                #     continue

                contract_start_date = data[36] or False
                contract_end_date = False

                if not emp or not contract_start_date:
                    continue

                if contract_start_date:
                    # birth_date = datetime.strptime(birth_date, "%d/%m/%Y").strftime('%Y-%m-%d')
                    if isinstance(contract_start_date, float):
                        year, month, day, hour, minute, second = xlrd.xldate_as_tuple(contract_start_date, wb.datemode)
                        contract_start_date = datetime(year, month, day)
                    else:
                        contract_start_date = datetime.strptime(contract_start_date, "%d-%m-%Y").strftime('%Y-%m-%d')

                    year = data[38]
                    if year:
                        contract_end_date = fields.Date.from_string(contract_start_date)
                        contract_end_date += relativedelta(years=int(year))

                resource_calendar_id = 8
                # if data[18] == 26:
                #     resource_calendar_id = 4
                if data[18] == 27:
                    resource_calendar_id = 9
                elif data[18] == 28:
                    resource_calendar_id = 10

                Contract.create({
                    'name': identification_id + ' Contract',
                    'wage': data[17] or 0.0,
                    'resource_calendar_id': resource_calendar_id,
                    'meal_allowance': data[19] or 0.0,
                    'transport_allowance': data[20] or 0.0,
                    'housing_allowance': data[21] or 0.0,
                    'employee_id': emp.id,
                    'date_start': contract_start_date,
                    'date_end': contract_end_date,
                    'structure_type_id': 2,
                    'job_id': emp.job_id.id,
                })

                # arabic_name = data[3]

                # civil_id = data[4]
                # if civil_id:
                #     aa = str(civil_id).split('.')
                #     civil_id = str(aa[0])

                # birth_date = data[5] or False
                # if birth_date:
                #     # birth_date = datetime.strptime(birth_date, "%d/%m/%Y").strftime('%Y-%m-%d')
                #     if isinstance(birth_date, float):
                #         year, month, day, hour, minute, second = xlrd.xldate_as_tuple(birth_date, wb.datemode)
                #         birth_date = datetime(year, month, day)
                #     else:
                #         birth_date = datetime.strptime(birth_date, "%d-%m-%Y").strftime('%Y-%m-%d')

                # bank_id = False
                # bank = (data[6]).strip() or False
                # if bank:
                #     bank_id = Bank.search([('name', '=', bank)], limit=1).id
                #     if not bank_id:
                #         bank_id = Bank.create({
                #             'name': bank
                #         }).id

                # iban = data[7]
                # if iban:
                #     aa = str(iban).split('.')
                #     iban = str(aa[0])

                # project_id = False
                # project = str(data[8]).strip()
                # if project:
                #     project_id = Project.search([('name', '=', project)], limit=1).id
                #     if not project_id:
                #         project = Project.create({
                #             'name': project
                #         })

                # restaurant_number = data[9]

                # restaurant = str(data[10]).strip()

                # location = str(data[11]).strip()

                # restaurant_id = False

                # if restaurant:
                #     restaurant_id = FleetRestaurant.search([
                #         ('name', '=', restaurant)
                #     ], limit=1).id
                #     if not restaurant_id:
                #         FleetRestaurant.create({
                #             'name': restaurant,
                #             'restaurant_id': restaurant_number,
                #             'location': location,
                #         }).id

                # position = data[12]
                # position_id = Job.search([('name', '=', position)], limit=1)
                # if not position_id:
                #     position_id = Job.create({
                #         'name': position
                #     })

                # country = data[13]
                # country_id = self.env['res.country'].search([('name', '=', country)], limit=1).id
                # if not country_id:
                #     country_id = self.env['res.country'].create({
                #         'name': country
                #     }).id

                # sponser = data[15]
                # sponser_id = Partner.search([('name', '=', sponser)], limit=1).id
                # if not sponser_id:
                #     sponser_id = Partner.create({
                #         'name': sponser
                #     }).id

                # company = data[16] or False
                # company_id = False
                # if company:
                #     company_id = self.env['res.company'].search([('name', '=', company)], limit=1).id or False

                # passport_id = data[22]

                # passport_issue_date = data[23] or False
                # if passport_issue_date:
                #     if isinstance(passport_issue_date, float):
                #         year, month, day, hour, minute, second = xlrd.xldate_as_tuple(passport_issue_date, wb.datemode)
                #         passport_issue_date = datetime(year, month, day)
                #     else:
                #         passport_issue_date = datetime.strptime(passport_issue_date, "%d-%m-%Y").strftime('%Y-%m-%d')

                # passport_expiry_date = data[23] or False
                # if passport_expiry_date:
                #     if isinstance(passport_expiry_date, float):
                #         year, month, day, hour, minute, second = xlrd.xldate_as_tuple(passport_expiry_date, wb.datemode)
                #         passport_expiry_date = datetime(year, month, day)
                #     else:
                #         passport_expiry_date = datetime.strptime(passport_expiry_date, "%d-%m-%Y").strftime('%Y-%m-%d')

                # kuwait_entry_date = data[26] or False
                # if kuwait_entry_date:
                #     if isinstance(kuwait_entry_date, float):
                #         year, month, day, hour, minute, second = xlrd.xldate_as_tuple(kuwait_entry_date, wb.datemode)
                #         kuwait_entry_date = datetime(year, month, day)
                #     else:
                #         kuwait_entry_date = datetime.strptime(kuwait_entry_date, "%d-%m-%Y").strftime('%Y-%m-%d')

                # joining_date = data[27] or False
                # if joining_date:
                #     if isinstance(joining_date, float):
                #         year, month, day, hour, minute, second = xlrd.xldate_as_tuple(joining_date, wb.datemode)
                #         joining_date = datetime(year, month, day)
                #     else:
                #         joining_date = datetime.strptime(joining_date, "%d-%m-%Y").strftime('%Y-%m-%d')

                # workpermit_expiry_date = data[28] or False
                # if workpermit_expiry_date:
                #     if isinstance(workpermit_expiry_date, float):
                #         year, month, day, hour, minute, second = xlrd.xldate_as_tuple(workpermit_expiry_date, wb.datemode)
                #         workpermit_expiry_date = datetime(year, month, day)
                #     else:
                #         workpermit_expiry_date = datetime.strptime(workpermit_expiry_date, "%d-%m-%Y").strftime('%Y-%m-%d')

                # license_expiry_date = data[29] or False
                # if license_expiry_date:
                #     if isinstance(license_expiry_date, float):
                #         year, month, day, hour, minute, second = xlrd.xldate_as_tuple(license_expiry_date, wb.datemode)
                #         license_expiry_date = datetime(year, month, day)
                #     else:
                #         license_expiry_date = datetime.strptime(license_expiry_date, "%d-%m-%Y").strftime('%Y-%m-%d')

                # fuel_card_number = data[30] or ''
                # if fuel_card_number:
                #     aa = str(fuel_card_number).split('.')
                #     fuel_card_number = str(aa[0])

                # phone_number = data[31] or ''
                # if phone_number:
                #     aa = str(phone_number).split('.')
                #     phone_number = str(aa[0])

                # workpermit_number = data[32] or ''
                # if workpermit_number:
                #     aa = str(workpermit_number).split('.')
                #     workpermit_number = str(aa[0])

                # accomodation = data[33] or ''

                # flat_room = data[34] or ''

                # health_expiry_date = data[35] or False

                # print ("health_expiry_date:::::::::::::", health_expiry_date)
                # if health_expiry_date:
                #     if isinstance(health_expiry_date, float):
                #         year, month, day, hour, minute, second = xlrd.xldate_as_tuple(health_expiry_date, wb.datemode)
                #         health_expiry_date = datetime(year, month, day)
                #     else:
                #         health_expiry_date = datetime.strptime(health_expiry_date, "%d/%m/%Y").strftime('%Y-%m-%d')

                # if name:
                #     vals = {
                #         'identification_id': identification_id,
                #         'name': str(name).strip(),
                #         'arabic_name': str(arabic_name).strip(),
                #         'civil_id': civil_id,
                #         'birthday': birth_date,
                #         'bank_id': bank_id,
                #         'iban_number': iban,
                #         'project_id': project_id,
                #         'restaurant_id': restaurant_id,
                #         'job_id': position_id.id,
                #         'country_id': country_id,
                #         'sponsorship_id': sponser_id,
                #         'company_id': company_id,
                #         'passport_id': passport_id,
                #         'passport_start_date': passport_issue_date,
                #         'passport_end_date': passport_expiry_date,
                #         'kuwait_entry_date': kuwait_entry_date,
                #         'date_joining': joining_date,
                #         'work_permit_expiry': workpermit_expiry_date,
                #         'license_expiry_date': license_expiry_date,
                #         'fuel_card_number': fuel_card_number,
                #         'work_phone': phone_number,
                #         'permit_no': workpermit_number,
                #         'accommodation': accomodation,
                #         'flat_room': flat_room,
                #         'health_card_expiry_date': health_expiry_date,
                #     }

                    # from pprint import pprint
                    # print (vals)
                    # Employee.create(vals)

        return {'type': 'ir.actions.act_window_close'}

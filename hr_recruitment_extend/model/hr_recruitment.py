# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models, fields, _, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    partner_ids = fields.Many2many('res.partner', string="Partners")


class Applicant(models.Model):
    _inherit = 'hr.applicant'

    passport_start_date = fields.Date(string="Issue Date")
    passport_end_date = fields.Date(string="Expiry Date")
    passport_id = fields.Char(string="Passport No")

    vaccination_type_id = fields.Many2one('vaccination.type', string="Vaccination Type")
    vaccination_first_dose_date = fields.Date(string="Vaccination First Dose Date")
    vaccination_second_dose_date = fields.Date(string="Vaccination Second Dose Date")
    vaccintion_first_batch_number = fields.Char(string="Vaccination First Batch Number")
    vaccination_second_batch_number = fields.Char(string="Vaccination Second Batch Number")
    sponsorship_id = fields.Many2one('res.partner', string="Sponsorship")
    interviewed_by = fields.Many2one('hr.employee', string="Interview By")
    arabic_name = fields.Char(string="Applicant's Arabic Name")
    backout_reason = fields.Text(string="Back-Out Reason")
    rejection_reason = fields.Text(string="Rejection Reason")
    food_allowance = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Food Allowance")
    accomodation_allowance = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Accommodation Allowance")
    nationality_id = fields.Many2one('res.country', string="Nationality")
    civil_code = fields.Char(string="Civil No")

    @api.model_create_multi
    def create(self, vals_list):
        record = super(Applicant, self).create(vals_list)
        follow_ids = self.env.company.partner_ids.ids
        if follow_ids:
            record.message_subscribe(partner_ids=follow_ids)

        return record

    def create_employee_from_applicant(self):
        """ Create a hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.display_name
            else:
                if not applicant.partner_name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))

                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'type': 'private',
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile,
                })
                address_id = new_partner_id.address_get(['contact'])['contact']

            if applicant.partner_name or contact_name:
                employee = self.env['hr.employee'].create({
                    'name': applicant.partner_name or contact_name,
                    'job_id': applicant.job_id.id or False,
                    'job_title': applicant.job_id.name,
                    'address_home_id': address_id,
                    'department_id': applicant.department_id.id or False,
                    'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
                    'work_email': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False,
                    'work_phone': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.phone or False,
                    'passport_id': applicant.passport_id,
                    'passport_start_date': applicant.passport_start_date,
                    'passport_end_date': applicant.passport_end_date,
                    'civil_id': applicant.civil_code
                })
                applicant.write({'emp_id': employee.id})
                if applicant.job_id:
                    applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                    applicant.job_id.message_post(
                        body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                        subtype_xmlid="hr_recruitment.mt_job_applicant_hired"
                    )

                applicant.message_post_with_view(
                    'hr_recruitment.applicant_hired_template', values={'applicant': applicant},
                    subtype_id=self.env.ref("hr_recruitment.mt_applicant_hired").id
                )

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        dict_act_window['context'] = {'form_view_initial_mode': 'edit'}
        dict_act_window['res_id'] = employee.id

        return dict_act_window


class VaccinationType(models.Model):
    _name = 'vaccination.type'
    _description = "Vaccination Type"

    name = fields.Char(string="Name", required=True)

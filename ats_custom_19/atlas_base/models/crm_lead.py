# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models, fields, _, api


class CrmLead(models.Model):
    _inherit = "crm.lead"

    project_name = fields.Char(tracking=True, string="Project Name")
    crm_no = fields.Char(tracking=True, string="CRM Ref", readonly=True, default=lambda self: ('New'))
    opportunity_type = fields.Selection([
        ('project', 'Project'),
        ('service', 'Service'),
        ('maintenance', 'Maintenance'),
        ('renovation', 'Renovation'),
        ('retail_sale', 'Retail Sale')], string="Opportunity Type", tracking=True)
    lead_time_id = fields.Many2one('lead.time', required=True, tracking=True)
    facility_type_ids = fields.Many2many('facility.type', required=True, tracking=True)
    commission = fields.Float(tracking=True, string="Commission")
    commission_to = fields.Many2one('res.partner', tracking=True)
    service_duration = fields.Integer(tracking=True, string="Service Duration")
    no_of_day_type = fields.Selection([('day', 'Day'), ('month', 'Month'), ('year', 'Years')], tracking=True)
    quote_ref = fields.Char(string="Quote Reference", tracking=True)
    facility_ids = fields.One2many('facility.facility', 'crm_lead_id', string="Facility", tracking=True)
    lost_other_reason = fields.Text("Other Lost Reason", tracking=True)
    project_type_detail_id = fields.Many2one('project.type.detail', tracking=True, string="Project Type Detail", required=True)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.user_has_groups('atlas_base.group_manage_lead_opportunity'):
            if not self.env.context.get('from_helpdesk_ticket'):
                raise UserError(_("You have no access to create lead/opportunity. You can create the same from helpdesk ticket."))

        for vals in vals_list:
            vals['crm_no'] = self.env['ir.sequence'].next_by_code('crm.sequence') or ('New')

        return super(CrmLead, self).create(vals_list)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_latitude = self.partner_id.partner_latitude
            self.partner_longitude = self.partner_id.partner_longitude

    def action_new_quotation(self):
        action = super(CrmLead, self).action_new_quotation()
        if action.get('context'):
            action['context'].update({
                'default_note': self.env['opportunity.type.terms'].get_opportunity_type_terms(self.opportunity_type),
                'default_opportunity_type': self.opportunity_type,
                'default_project_type_detail_id': self.project_type_detail_id.id,
            })

        return action

    @api.depends('order_ids.state', 'order_ids.currency_id', 'order_ids.amount_untaxed', 'order_ids.date_order', 'order_ids.company_id')
    def _compute_sale_data(self):
        super(CrmLead, self)._compute_sale_data()
        for lead in self:
            quotation_cnt = 0
            for order in lead.order_ids:
                if order.state in ('draft', 'sent', 'cancel'):
                    quotation_cnt += 1

            lead.quotation_count = quotation_cnt

    def action_view_sale_quotation(self):
        action = super(CrmLead, self).action_view_sale_quotation()
        action['domain'] = [('opportunity_id', '=', self.id), ('state', 'in', ['draft', 'sent', 'cancel'])]

        return action


class CrmLeadLost(models.TransientModel):
    _inherit = "crm.lead.lost"

    other_reason = fields.Char(string="Other Reason")

    def action_lost_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        return leads.action_set_lost(lost_reason_id=self.lost_reason_id.id, lost_other_reason=self.other_reason)


class CrmDays(models.Model):
    _name = "week.days"
    _description = 'Week Days'
    _rec_name = "day"

    day = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')], string="Week Day", required=True)
    display_name = fields.Char(string="Display Name", compute="_compute_display_name")

    @api.depends('day')
    def _compute_display_name(self):
        for rec in self:
            display_name = ''
            if rec.day and rec.day == 'monday':
                rec.display_name = 'Monday'
            elif rec.day and rec.day == 'tuesday':
                rec.display_name = 'Tuesday'
            elif rec.day and rec.day == 'wednesday':
                rec.display_name = 'Wednesday'
            elif rec.day and rec.day == 'thursday':
                rec.display_name = 'Thursday'
            elif rec.day and rec.day == 'friday':
                rec.display_name = 'Friday'
            elif rec.day and rec.day == 'saturday':
                rec.display_name = 'Saturday'
            else:
                rec.display_name = 'Sunday'

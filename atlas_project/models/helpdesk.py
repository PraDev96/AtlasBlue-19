# -*- coding: utf-8 -*-

from datetime import date
from markupsafe import Markup
from odoo.exceptions import UserError
from odoo import models, fields, _, api


class Stage(models.Model):
    _inherit = "helpdesk.stage"

    code = fields.Char(string="Code")


class Team(models.Model):
    _inherit = "helpdesk.team"

    enable_lead = fields.Boolean(string="Enable Lead Creation")


class Ticket(models.Model):
    _name = 'helpdesk.ticket'
    _inherit = ["helpdesk.ticket", "utm.mixin"]

    enable_lead = fields.Boolean(related="team_id.enable_lead", tracking=True)
    stage_position = fields.Boolean(related="stage_id.fold", string="Stage Position", tracking=True)
    lead_id = fields.Many2one("crm.lead", string="Lead", tracking=True)
    lead_ids = fields.One2many("crm.lead", 'ticket_id', string="Leads", tracking=True)
    lead_count = fields.Integer(string="Lead #", compute="_compute_lead_count", tracking=True)
    phone = fields.Char(string="Phone", tracking=True)
    description = fields.Text(required=True, tracking=True)
    call_other_reason = fields.Text(string="Other Reason", tracking=True)
    call_reason_ids = fields.Many2many('call.reason', string="Call Reasons", tracking=True)
    call_receive_id = fields.Many2one('call.receive', string="Call Received On", tracking=True)
    comment = fields.Text(string="Comment", tracking=True)
    end_date = fields.Date(string="Ticket Date", default=fields.Date.today, tracking=True)
    tag_ids = fields.Many2many(string="Departments", tracking=True)
    date_done = fields.Datetime(string="Closed On", readonly=True, tracking=True)
    dt_ticket = fields.Date(string="Created date", default=fields.Date.today, required=True, tracking=True)
    ticket_duration = fields.Integer(string="Ticket Duration (Days)", compute='_compute_difference', tracking=True)

    def _compute_difference(self):
        for rec in self:
            diff = 0
            if rec.dt_ticket:
                close_dt = rec.date_done and rec.date_done.date() or date.today()
                diff = (close_dt - rec.dt_ticket).days
            rec.ticket_duration = diff

    def send_mail_to_assignee(self, vals):
        if vals.get('user_id') or vals.get('team_id'):
            for ticket in self:
                body = Markup("Updates from Helpdesk.<br /><br /><strong>Ticket:</strong> %s<br /><strong>Assigned To:</strong> %s<br /><strong>Team :</strong> %s") % (
                    ticket.name, ticket.user_id.name or '', ticket.team_id.name or '')

                partner_ids = []
                if ticket.user_id and ticket.user_id.partner_id:
                    partner_ids.append(ticket.user_id.partner_id.id)

                ticket.message_post(body=body, partner_ids=list(set(partner_ids)))

    @api.model_create_multi
    def create(self, vals_list):
        record = super(Ticket, self).create(vals_list)
        for vals in vals_list:
            record.send_mail_to_assignee(vals)

        return record

    def write(self, val):
        if val.get('stage_id'):
            if self.env['helpdesk.stage'].sudo().browse(val['stage_id']).fold:
                val.update({'date_done': fields.Datetime.now()})

        self.send_mail_to_assignee(val)
        return super(Ticket, self).write(val)

    def unlink(self):
        if not self.user_has_groups('atlas_base.group_delete_helpdesk_ticket'):
            raise UserError(_('You cannot Delete the Helpdesk Ticket!!! Please Contact Administrator.'))

        return super(Ticket, self).unlink()

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            self.phone = self.partner_id.phone or self.partner_id.mobile
            self.partner_email = self.partner_id.email

    def _compute_lead_count(self):
        for rec in self:
            rec.lead_count = len(rec.lead_ids.ids)

    def get_default_context(self):
        return {
            'default_company_id': self.company_id.id,
            'default_ticket_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_user_id': self.user_id.id,
            'default_email_from': self.partner_email,
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_source_id': self.source_id.id,
            'default_description': self.description,
        }

    def action_create_lead(self):
        ctx = self.env.context.copy()
        ctx.update(self.get_default_context())
        ctx.update({'from_helpdesk_ticket': True})
        return {
            'name': _('Ticket to Lead'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm.lead',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'view_id': self.env.ref('crm.crm_lead_view_form', False).id,
            'context': ctx
        }

    def action_view_lead(self):
        action = self.env.ref('crm.crm_lead_action_pipeline').sudo().read()[0]
        ctx = self.env.context.copy()
        ctx.update(self.get_default_context())
        action.update({
            'domain': [('id', 'in', self.lead_ids.ids)],
            'context': ctx
        })

        return action

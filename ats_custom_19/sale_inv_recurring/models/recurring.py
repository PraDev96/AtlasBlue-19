# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class RecurringInvoice(models.Model):
    _name = 'sale.recurring.invoice'
    _description = "sale.recurring.invoice"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Ref", readonly=True, tracking=True)
    ref_invoice_id = fields.Many2one("account.move", string="Invoice Ref", tracking=True)
    enable_recurring_inv = fields.Boolean(string="Enable Recurrent Invoice", tracking=True)
    inv_start_date = fields.Date(string="Invoice Start Date", tracking=True)
    interval_unit = fields.Selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months'), ('years', 'Years')], default="days", tracking=True)
    interval_nbr = fields.Integer(string="Recurring Invoice Interval", tracking=True)
    recurrent_inv_nbr = fields.Integer(string="Recurring Invoice tobe Created", tracking=True)
    recurrent_inv_ids = fields.One2many("account.move", "recurrent_ref_id", string="Recurrent Invoices", tracking=True)
    recurrent_user_id = fields.Many2one("res.users", string="Recurrence Confirmed By", tracking=True, readonly=True)
    recurrent_confirmed_date = fields.Datetime(string="Recurrence Confirmed On", tracking=True, readonly=True)
    state = fields.Selection([
        ("draft", "Draft"), ("running", "Running"), ("done", "Completed"), ("cancel", "Cancelled")], default="draft",
        string="Recurrent Status", tracking=True, readonly=True)

    line_ids = fields.One2many("recurring.invoice.line", "recurrent_id", string="Lines")
    instant_create = fields.Boolean(string="Create Instantly", default=True)
    should_auto_post = fields.Boolean(string="Auto Post Recurrent Invoice")

    def action_confirm_inv_recurrence(self):
        if self.ref_invoice_id.state != 'posted':
            raise ValidationError(_('Your reference Invoice must be posted.'))

        if self.interval_nbr < 1:
            raise ValidationError(_("Recurrence duration cannot be less than 1"))

        lines = []
        dt = self.inv_start_date
        day = dt.day
        for i in range(0, self.recurrent_inv_nbr):
            lines.append((0, 0, {
                'ref_invoice_id': self.ref_invoice_id.id,
                'date_invoice': dt
            }))
            interval = {self.interval_unit: self.interval_nbr}
            if self.interval_unit not in ['days', 'weeks']:
                interval.update({'day': day})

            dt = dt + relativedelta(**interval)

        self.write({
            'line_ids': lines,
            'state': 'running',
            'recurrent_user_id': self.env.uid,
            'recurrent_confirmed_date': fields.Datetime.now()
        })

        if self.instant_create:
            lines = self.line_ids.filtered(lambda l: not l.invoice_id)
            lines.create_next_invoice()

    def action_cancel(self):
        lines = self.line_ids.filtered(lambda l: l.state == 'draft')
        if lines:
            lines.unlink()

        self.ref_invoice_id.write({'recurrent_ref_id': False})
        self.write({'state': 'cancel'})

    def action_reset(self):
        self.write({'state': 'draft', 'recurrent_user_id': False, 'recurrent_confirmed_date': False})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.recurrent')

        record = super(RecurringInvoice, self).create(vals_list)
        record.ref_invoice_id.write({'recurrent_ref_id': record.id})
        return record

    @api.model
    def cron_sale_recurring_invoice(self):
        dt = fields.Date.today()
        recurrent_lines = self.env['recurring.invoice.line'].search([
            ('state', '=', 'draft'), ('date_invoice', '<=', dt), '|', ('invoice_id', '=', False), ('invoice_id.state', '=', 'cancel'),
        ])
        recurrent_lines.create_next_invoice()
        # for rec in recurrent_lines:
        #     new_invoice = rec.ref_invoice_id.copy({'invoice_date': rec.date_invoice})
        #     for line in rec.ref_invoice_id.invoice_line_ids.filtered('sale_line_ids'):
        #         new_line = new_invoice.invoice_line_ids.filtered(lambda l: l.product_id.id == line.product_id.id)
        #         if new_line:
        #             new_line.write({'sale_line_ids': [(4, sol_id) for sol_id in line.sale_line_ids.ids]})

        #     if rec.recurrent_id.should_auto_post:
        #         new_invoice.action_post()
        #     rec.write({'invoice_id': new_invoice.id})


class RecurringInvoiceLine(models.Model):
    _name = 'recurring.invoice.line'
    _description = "recurring.invoice.line"
    _order = "date_invoice"
    _rec_name = "date_invoice"

    ref_invoice_id = fields.Many2one("account.move", string="Invoice Ref")
    date_invoice = fields.Date(string="Invoice Date")
    invoice_id = fields.Many2one("account.move", string="Invoice")
    state = fields.Selection([('draft', 'Tobe Done'), ('done', 'Done')], default='draft')
    recurrent_id = fields.Many2one("sale.recurring.invoice", string="Recurrent From")

    def write(self, vals):
        if vals.get('invoice_id'):
            vals['state'] = 'done'

        res = super().write(vals)
        if vals.get('state') == 'done':
            for rec in self:
                recurrent = rec.recurrent_id
                lines = recurrent.line_ids
                if lines and len(lines.ids) == len(lines.filtered(lambda l: l.state == 'done')):
                    rec.recurrent_id.write({'state': 'done'})

        return res

    def create_next_invoice(self):
        for rec in self:
            new_invoice = rec.ref_invoice_id.copy({'invoice_date': rec.date_invoice})
            for line in rec.ref_invoice_id.invoice_line_ids.filtered('sale_line_ids'):
                new_line = new_invoice.invoice_line_ids.filtered(lambda l: l.product_id.id == line.product_id.id)
                if new_line:
                    new_line.write({'sale_line_ids': [(4, sol_id) for sol_id in line.sale_line_ids.ids]})

            if rec.recurrent_id.should_auto_post:
                new_invoice.action_post()

            rec.write({'invoice_id': new_invoice.id})

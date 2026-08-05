# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model_create_multi
    def create(self, vals_list):
        """
            This is to restrict the timeoff time more than 8.5 hours
        """
        for vals in vals_list:
            if vals.get('unit_amount') and vals.get('unit_amount') > 8.5:
                vals['unit_amount'] = 8.5

        return super(AccountAnalyticLine, self).create(vals_list)

    def write(self, vals):
        """
            This is to restrict the timeoff time more than 8.5 hours
        """
        if 'unit_amount' in vals and vals.get('unit_amount') > 8.5:
            vals['unit_amount'] = 8.5

        return super().write(vals)

    @api.model
    def cron_end_long_timesheets(self):
        """ End all running timesheets exceeding 8.5 hours duration created today. """
        now = fields.Datetime.now()
        today = now.date()

        # Find running timesheets created today
        running_timesheets = self.search([('is_timer_running', '=', True), ('start_time', '!=', False)])

        for ts in running_timesheets:
            if ts.start_time.date() == today:
                duration = (now - ts.start_time).total_seconds() / 3600.0  # hours
                if duration > 8.5:
                    ts.write({
                        'unit_amount': 8.5,  # Cap duration to 8.5 hours
                        'is_timer_running': False,  # Mark timer as stopped
                    })
                    # Optional: Add an internal note or chatter message
                    ts.message_post(
                        body=f"⏰ Timesheet automatically ended at {now.strftime('%H:%M')} "
                             f"after exceeding 8.5 hours (started at {ts.start_time})."
                    )

    @api.model
    def cron_close_open_timesheets_today(self):
        """At 22:00 server time, close timesheets started today but still running."""
        # Today (date only, in server timezone)
        today = fields.Date.context_today(self)

        # Domain assumptions:
        # - date == today  -> started today
        # - 'is_timer_running' or similar flag indicates running entries
        #   Adjust field name according to your DB (e.g. 'unit_amount' == 0 and timer_active = True).
        running_lines = self.search([
            ("date", "=", today),
            ("is_timesheet", "=", True),  # standard flag in timesheets
            ("unit_amount", "=", 0.0),  # no duration yet, still running
        ])

        # Force end at exactly 22:00 server time
        end_dt = fields.Datetime.now().replace(hour=22, minute=0, second=0, microsecond=0)

        for line in running_lines:
            # If you store start datetime, use it to compute duration; otherwise set a minimal duration
            start_dt = line.create_date  # or a dedicated start field if you have one
            if start_dt and start_dt.date() == today:
                duration_hours = (end_dt - start_dt).total_seconds() / 3600.0
                if duration_hours < 0:
                    # safety: if create_date is after end_dt, skip
                    continue
                line.write({
                    "unit_amount": duration_hours,
                    # if you have an explicit "end" datetime field, set it here
                    # "end_datetime": end_dt,
                })

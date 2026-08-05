# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_timesheet_daily_limit = fields.Boolean(
        string="Enable Daily Timesheet Limit",
        config_parameter='ats_hr_timesheet_limit.use_timesheet_daily_limit',
        default=False, help="Check this to Enforce a Maximum Daily Limit for Timesheet Entries."
    )
    timesheet_daily_limit = fields.Float(
        string="Maximum Daily Timesheet Limit (Hours)",
        config_parameter='ats_hr_timesheet_limit.timesheet_daily_limit',
        default=8, help="Maximum Hours a user can log in a Single Day."
    )

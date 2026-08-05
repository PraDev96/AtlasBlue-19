# -*- coding: utf-8 -*-

from datetime import datetime
from odoo.tools import format_date
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    overtime_unit_amount = fields.Float(string="Overtime Hours Spent", readonly=True, help="To Notice the Overtime Hours for Portal Users")
    is_overtime_added = fields.Boolean(string="Is Overtime Added", readonly=True)
    overtime_approved_amount = fields.Float(string="Approved Overtime Hours", readonly=True, help="Overtime Hours Approved by Manager")
    overtime_approved_manager_id = fields.Many2one('res.users', string="Overtime Approved By", readonly=True, help="Overtime Hours Approved Manager User")

    def _float_to_time(self, hours):
        """ Convert float hours to HH:mm string format. """
        minutes = round(abs(hours) * 60)
        return '{:02d}:{:02d}'.format(*divmod(minutes, 60))

    def _get_daily_limit_info(self, date, user_id, current_id=None):
        if self.env.user.has_group('ats_hr_timesheet_limit.group_bypass_timesheet_limit'):
            return {'limit': 0.0, 'existing': 0.0, 'remaining': 999.0}

        use_limit = self.env['ir.config_parameter'].sudo().get_param('ats_hr_timesheet_limit.use_timesheet_daily_limit')
        if not use_limit:
            return {'limit': 0.0, 'existing': 0.0, 'remaining': 999.0}

        limit = float(self.env['ir.config_parameter'].sudo().get_param('ats_hr_timesheet_limit.timesheet_daily_limit', default=0.0))
        if limit <= 0.0:
            return {'limit': 0.0, 'existing': 0.0, 'remaining': 999.0}

        domain = [('date', '=', date), ('user_id', '=', user_id), ('project_id.project_type_id.name', 'not in', ('Service', 'Maintenance'))]
        if current_id:
            domain.append(('id', '!=', current_id))

        result = self.sudo()._read_group(domain, [], ['unit_amount:sum'])
        existing_hours = result[0][0] if result and result[0][0] else 0.0
        return {
            'limit': limit,
            'existing': existing_hours,
            'remaining': max(0.0, limit - existing_hours)
        }

    def _check_daily_limit(self, date, unit_amount, user_id, current_id=None):
        if self.env.context.get('skip_timesheet_limit_check'):
            return unit_amount, 0.0

        info = self._get_daily_limit_info(date, user_id, current_id)
        if info['limit'] <= 0.0:
            return unit_amount, 0.0

        formatted_date = format_date(self.env, date)
        if info['remaining'] <= 0.0 and unit_amount >= 0.0 and self.task_id:
            if self.env.context.get('auto_adjust_to_limit'):
                return 0.0, unit_amount

            raise ValidationError(_(
                "You have already Reached the Daily Limit of %(limit)s for %(date)s. \n"
                "You cannot add more Timesheet Entries for this Date.",
                limit=self._float_to_time(info['limit']), date=formatted_date
            ))

        if (info['existing'] + unit_amount) > info['limit'] and self.task_id:
            if self.env.context.get('auto_adjust_to_limit'):
                extra = (info['existing'] + unit_amount) - info['limit']
                return info['remaining'], extra

            raise ValidationError(_(
                "You cannot add more than the Daily Limit of %(limit)s for %(date)s. \n"
                "Already Logged: %(existing)s. \n"
                "Remaining Possible Hours for this Date: %(remaining)s.",
                limit=self._float_to_time(info['limit']),
                existing=self._float_to_time(info['existing']),
                remaining=self._float_to_time(info['remaining']),
                date=formatted_date
            ))

        return unit_amount, 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Check limit even for 0 hours if it's a new entry (start of timing)
            date = vals.get('date') or fields.Date.today()
            user_id = vals.get('user_id') or self.env.uid
            unit_amount = vals.get('unit_amount', 0.0)
            adjusted_amount, extra_amount = self._check_daily_limit(date, unit_amount, user_id)
            if self.env.context.get('auto_adjust_to_limit'):
                vals['unit_amount'] = adjusted_amount
                vals['overtime_unit_amount'] = extra_amount

        return super(AccountAnalyticLine, self).create(vals_list)

    def write(self, vals):
        if ('unit_amount' in vals or 'date' in vals or 'user_id' in vals) and not self.env.context.get('skip_timesheet_limit_check'):
            if self.env.context.get('auto_adjust_to_limit'):
                for rec in self:
                    unit_amount = vals.get('unit_amount', rec.unit_amount)
                    date = vals.get('date', rec.date)
                    user_id = vals.get('user_id', rec.user_id.id)
                    adjusted_amount, extra_amount = rec._check_daily_limit(date, unit_amount, user_id, current_id=rec.id)
                    super(AccountAnalyticLine, rec).write({
                        'unit_amount': adjusted_amount,
                        'overtime_unit_amount': extra_amount,
                    })
                # Remove from vals to prevent double write
                vals = {k: v for k, v in vals.items() if k not in ('unit_amount', 'overtime_unit_amount')}
                if not vals:
                    return True
            else:
                for rec in self:
                    unit_amount = vals.get('unit_amount', rec.unit_amount)
                    date = vals.get('date', rec.date)
                    user_id = vals.get('user_id', rec.user_id.id)
                    rec._check_daily_limit(date, unit_amount, user_id, current_id=rec.id)

        return super(AccountAnalyticLine, self).write(vals)

    @api.onchange('unit_amount', 'date', 'user_id')
    def _onchange_unit_amount_limit(self):
        if self.unit_amount >= 0:
            date = self.date or fields.Date.today()
            user_id = self.user_id.id or self.env.uid
            info = self._get_daily_limit_info(date, user_id, current_id=self._origin.id if hasattr(self, '_origin') else False)
            if info['limit'] > 0:
                formatted_date = format_date(self.env, date)
                if info['remaining'] <= 0.0 and self.task_id:
                    return {
                        'warning': {
                            'title': _("Daily Limit Reached"),
                            'message': _(
                                "You have already Reached the Daily Limit of %(limit)s for %(date)s. \n"
                                "You cannot add more Timesheet Entries for this Date.",
                                limit=self._float_to_time(info['limit']), date=formatted_date
                            )
                        }
                    }
                if (info['existing'] + self.unit_amount) > info['limit'] and self.task_id:
                    return {
                        'warning': {
                            'title': _("Daily Limit Warning"),
                            'message': _(
                                "You are about to Exceed the Daily Limit of %(limit)s for %(date)s. \n"
                                "Already Logged: %(existing)s. \n"
                                "Remaining Possible Hours for this Date: %(remaining)s.",
                                limit=self._float_to_time(info['limit']),
                                existing=self._float_to_time(info['existing']),
                                remaining=self._float_to_time(info['remaining']),
                                date=formatted_date
                            )
                        }
                    }

    @api.model
    def check_limit_exceeded(self, args):
        analytic_line_id = args.get('analytic_line_id')
        # Check if already reached limit before even starting (for start button)
        if not analytic_line_id:
            today = fields.Date.today()
            info = self._get_daily_limit_info(today, self.env.uid)
            if info['limit'] > 0 and info['remaining'] <= 0.0:
                return {
                    'already_reached': True,
                    'date': format_date(self.env, today),
                    'limit': self._float_to_time(info['limit']),
                }

            return {'already_reached': False}

        line = self.sudo().browse(int(analytic_line_id))
        if not line:
            return {'exceeded': False}

        # Calculate what would be the unit_amount if ended now
        delta = datetime.utcnow() - line.start_date
        worked_hours = delta.total_seconds() / 3600.0
        date = line.date or fields.Date.today()
        info = self._get_daily_limit_info(date, line.user_id.id or self.env.uid, current_id=line.id)
        if info['limit'] > 0 and (info['existing'] + worked_hours) > info['limit']:
            extra = (info['existing'] + worked_hours) - info['limit']
            return {
                'exceeded': True,
                'date': format_date(self.env, date),
                'limit': self._float_to_time(info['limit']),
                'existing': self._float_to_time(info['existing']),
                'worked_hours': self._float_to_time(worked_hours),
                'overtime_unit_amount': self._float_to_time(extra),
                'remaining': self._float_to_time(info['remaining']),
            }

        return {'exceeded': False}

    @api.model
    def create_from_portal(self, args):
        # Apply limit check
        today = fields.Date.today()
        info = self._get_daily_limit_info(today, self.env.uid)
        if info['limit'] > 0 and info['remaining'] <= 0.0 and self.task_id:
            raise ValidationError(_(
                "You have already Reached the Daily Limit of %(limit)s for %(date)s. \n"
                "You cannot add more Timesheet Entries for this Date.",
                limit=self._float_to_time(info['limit']), date=format_date(self.env, today)
            ))
        return super(AccountAnalyticLine, self).create_from_portal(args)

    def action_update_overtime(self):
        self.ensure_one()
        return {
            'target': 'new',
            'view_mode': 'form',
            'name': _("Update / Confirm Overtime Hours"),
            'type': 'ir.actions.act_window',
            'res_model': 'timesheet.overtime.confirm.wizard',
            'context': {
                'default_analytic_line_id': self.id,
                'default_overtime_hours': self.overtime_unit_amount,
            }
        }

    @api.model
    def update_from_portal(self, args):
        if args.get('confirm_limit'):
            res = super(AccountAnalyticLine, self.with_context(auto_adjust_to_limit=True)).update_from_portal(args)
            if res and res.get('analytic_line_rec'):
                line = self.sudo().browse(res['analytic_line_rec'])
                res['overtime_unit_amount'] = line.overtime_unit_amount
                # Ensure the split is correctly shown in portal by overriding returned unit_amount
                res['unit_amount'] = self._float_to_time(line.unit_amount)
            return res

        return super(AccountAnalyticLine, self).update_from_portal(args)

# -*- coding: utf-8 -*-

from odoo import fields, _
from odoo.tools import get_lang
from odoo.addons.project.models.project_project import Project as ProjectBase


def write(self, vals):
    if vals.get('access_token'):
        self.ensure_one()  # We are not supposed to add a single access token to multiple project
        if self.privacy_visibility != 'portal':
            vals['access_token'] = ''

    # Here we modify the project's stage according to the selected company (selecting the first
    # stage in sequence that is linked to the company).
    company_id = vals.get('company_id')
    if self.env.user.has_group('project.group_project_stages') and company_id:
        projects_already_with_company = self.filtered(lambda p: p.company_id.id == company_id)
        if projects_already_with_company:
            projects_already_with_company.write({key: value for key, value in vals.items() if key != 'company_id'})
            self -= projects_already_with_company
        if company_id not in (None, *self.company_id.ids) and self.stage_id.company_id:
            ProjectStage = self.env['project.project.stage']
            vals["stage_id"] = ProjectStage.search([('company_id', 'in', (company_id, False))], order=f"sequence asc, {ProjectStage._order}", ).id

    # directly compute is_favorite to dodge allow to write access right
    if 'is_favorite' in vals:
        vals.pop('is_favorite')
        self._fields['is_favorite'].determine_inverse(self)

    if 'last_update_status' in vals and vals['last_update_status'] != 'to_define':
        for project in self:
            # This does not benefit from multi create, this is to allow the default description from being built.
            # This does seem ok since last_update_status should only be updated on one record at once.
            self.env['project.update'].with_context(default_project_id=project.id).create({
                'name': _('Status Update - ') + fields.Date.today().strftime(get_lang(self.env).date_format), 'status': vals.get('last_update_status'),
            })
        vals.pop('last_update_status')
    if vals.get('privacy_visibility'):
        self._change_privacy_visibility(vals['privacy_visibility'])

    # date_start = vals.get('date_start', True)
    # date_end = vals.get('date', True)
    # if not date_start or not date_end:
    #     vals['date_start'] = False
    #     vals['date'] = False
    # else:
    """
        The above commented statements to achieve to store the planned date itself like independently.
    """
    no_current_date_begin = not all(project.date_start for project in self if project.date_start)
    no_current_date_end = not all(project.date for project in self if project.date)
    date_start_update = 'date_start' in vals
    date_end_update = 'date' in vals
    if (date_start_update and no_current_date_end and not date_end_update):
        del vals['date_start']
    elif (date_end_update and no_current_date_begin and not date_start_update):
        del vals['date']

    res = super(ProjectBase, self).write(vals) if vals else True

    if 'allow_task_dependencies' in vals and not vals.get('allow_task_dependencies'):
        self.env['project.task'].search([('project_id', 'in', self.ids), ('state', '=', '04_waiting_normal')]).write({'state': '01_in_progress'})

    if 'active' in vals:
        # archiving/unarchiving a project does it on its tasks, too
        self.with_context(active_test=False).mapped('tasks').write({'active': vals['active']})

    if 'name' in vals and self.analytic_account_id:
        projects_read_group = self.env['project.project']._read_group(
            [('analytic_account_id', 'in', self.analytic_account_id.ids)], ['analytic_account_id'], having=[('__count', '=', 1)],
        )
        analytic_account_to_update = self.env['account.analytic.account'].browse([analytic_account.id for [analytic_account] in projects_read_group])
        analytic_account_to_update.write({'name': self.name})

    return res


ProjectBase.write = write

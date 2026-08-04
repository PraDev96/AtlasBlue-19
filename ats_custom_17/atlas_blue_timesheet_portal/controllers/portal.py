# -*- coding: utf-8 -*-

from odoo.http import request
from odoo import http, fields, _
from odoo.tools import date_utils
from collections import OrderedDict
from datetime import date, timedelta
from odoo.osv.expression import OR, AND
from dateutil.relativedelta import relativedelta
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.project.controllers.portal import ProjectCustomerPortal as PCP


class ProjectTeamCustomerPortal(PCP):

    def _project_get_page_view_values(self, project, access_token, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='content', groupby=None, **kwargs):
        values = super()._project_get_page_view_values(project, access_token, page=page, date_begin=date_begin, date_end=date_end, sortby=sortby, search=search, search_in=search_in, groupby=groupby, **kwargs)
        employee_cost_line_rec = request.env['employee.cost'].sudo().search(
            [('project_id', '=', project.id), ('from_portal', '=', True), ('is_signature', '=', True), ('user_id', '=', request.env.user.id)], limit=1)
        start_date = False
        end_date = False
        hours_spent = False
        if employee_cost_line_rec.start_date:
            start_date = fields.Datetime.context_timestamp(employee_cost_line_rec, employee_cost_line_rec.start_date)

        if employee_cost_line_rec.end_date:
            end_date = fields.Datetime.context_timestamp(employee_cost_line_rec, employee_cost_line_rec.end_date)

        if employee_cost_line_rec.hours_spent:
            delta = employee_cost_line_rec.end_date - employee_cost_line_rec.start_date
            worked_hours = delta.total_seconds() / 3600.0
            hours_spent = '{0:02.0f}:{1:02.0f}'.format(*divmod(worked_hours * 60, 60))

        values.update({
            'exist_cost_rec': employee_cost_line_rec,
            'employee_cost_line_start_date': start_date,
            'employee_cost_line_end_date': end_date,
            'account_analytic_rec_hours_spent': hours_spent,
        })
        return values

    def _task_get_page_view_values(self, task, access_token, **kwargs):
        values = super()._task_get_page_view_values(task, access_token, **kwargs)
        account_analytic_rec = request.env['account.analytic.line'].sudo().search(
            [('task_id', '=', task.id), ('from_portal', '=', True), ('is_signature', '=', True), ('user_id', '=', request.env.user.id)], limit=1)
        start_date = False
        end_date = False
        unit_amount = False
        if account_analytic_rec.start_date:
            start_date = fields.Datetime.context_timestamp(account_analytic_rec, account_analytic_rec.start_date)

        if account_analytic_rec.end_date:
            end_date = fields.Datetime.context_timestamp(account_analytic_rec, account_analytic_rec.end_date)

        if account_analytic_rec.unit_amount and account_analytic_rec.end_date and account_analytic_rec.start_date:
            delta = account_analytic_rec.end_date - account_analytic_rec.start_date
            worked_hours = delta.total_seconds() / 3600.0
            unit_amount = '{0:02.0f}:{1:02.0f}'.format(*divmod(worked_hours * 60, 60))

        values.update({
            'exist_rec': account_analytic_rec,
            'account_analytic_rec_start_date': start_date,
            'account_analytic_rec_end_date': end_date,
            'account_analytic_rec_unit_amount': unit_amount,
        })
        return values

    @http.route(['/my/projects', '/my/projects/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_projects(self, page=1, date_begin=None, date_end=None, filterby=None, sortby=None, search=None, search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        Project = request.env['project.project']
        domain = self._prepare_project_domain()

        searchbar_sortings = self._prepare_searchbar_sortings()
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
        }
        crm_teams = request.env['crm.team'].sudo().search([])
        for crm_team in crm_teams:
            searchbar_filters.update({
                'team_' + str(crm_team.id): {'label': crm_team.name, 'domain': [('team_id', '=', crm_team.id)]}
            })

        # default filter by value
        crm_team_id = request.env['crm.team'].sudo().search([('team_members_ids', 'in', request.env.user.employee_id.id)], limit=1)
        default_team_id = 'team_' + str(crm_team_id.id)
        if not filterby:
            filterby = default_team_id
            if searchbar_filters.get(filterby, searchbar_filters.get('team_id')):
                domain += searchbar_filters.get(filterby, searchbar_filters.get('team_id'))['domain']

        if searchbar_filters.get('date_start'):
            domain += searchbar_filters.get(filterby, searchbar_filters.get('date_start'))['domain']

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])

            domain += search_domain

        # projects count
        project_count = Project.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/projects",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=project_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        projects = Project.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_projects_history'] = projects.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'projects': projects,
            'page_name': 'project',
            'default_url': '/my/projects',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })

        return request.render("project.portal_my_projects", values)

    def _task_get_groupby_mapping(self):
        return {
            'project': 'project_id',
            'stage': 'stage_id',
            'customer': 'partner_id',
            'milestone': 'milestone_id',
            'priority': 'priority',
            'status': 'state',
            'date_start': 'date_start',
            'team_id': 'team_id',
        }

    def _task_get_search_domain(self, search_in, search):
        """
            Replaced for adding the date_start.
        """
        search_domain = []
        if search_in in ('content', 'all'):
            search_domain.append([('name', 'ilike', search)])
            search_domain.append([('description', 'ilike', search)])
        if search_in in ('customer', 'all'):
            search_domain.append([('partner_id', 'ilike', search)])

        # newly added
        if search_in in ('date_start', 'all'):
            search_domain.append([('date_start', '=', search)])

        if search_in in ('message', 'all'):
            search_domain.append([('message_ids.body', 'ilike', search)])
        if search_in in ('stage', 'all'):
            search_domain.append([('stage_id', 'ilike', search)])
        if search_in in ('project', 'all'):
            search_domain.append([('project_id', 'ilike', search)])
        if search_in in ('ref', 'all'):
            search_domain.append([('id', 'ilike', search)])
        if search_in in ('milestone', 'all'):
            search_domain.append([('milestone_id', 'ilike', search)])
        if search_in in ('users', 'all'):
            user_ids = request.env['res.users'].sudo().search([('name', 'ilike', search)])
            search_domain.append([('user_ids', 'in', user_ids.ids)])
        if search_in in ('priority', 'all'):
            search_domain.append([('priority', 'ilike', search == 'normal' and '0' or '1')])
        if search_in in ('status', 'all'):
            state_dict = dict(map(reversed, request.env['project.task']._fields['state']._description_selection(request.env)))
            search_domain.append([('state', 'ilike', state_dict.get(search, search))])

        return OR(search_domain)

    def _task_get_searchbar_groupby(self, milestones_allowed, project=False):
        """
            Replaced for adding date_start.
        """
        values = {
            'none': {'input': 'none', 'label': _('None'), 'order': 1},
            'date_start': {'input': 'date_start', 'label': _('Date'), 'order': 2},
            'stage': {'input': 'stage', 'label': _('Stage'), 'order': 4},
            'status': {'input': 'status', 'label': _('Status'), 'order': 5},
            'priority': {'input': 'priority', 'label': _('Priority'), 'order': 7},
            'customer': {'input': 'customer', 'label': _('Customer'), 'order': 10},
        }
        if self._display_project_groupby(project):
            values['project'] = {'input': 'project', 'label': _('Project'), 'order': 2}
        if milestones_allowed:
            values['milestone'] = {'input': 'milestone', 'label': _('Milestone'), 'order': 6}

        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_my_tasks_searchbar_filters(self, project_domain=None, task_domain=None):
        """
            Replaced for adding new things.
            Removed the project groupby and task.
        """
        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        today_domain = ['|', '&', ('date_start', '=', today), ('task_end_date', '=', False), '&', ('date_start', '<=', today), ('task_end_date', '>=', today)]

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('project_id', '!=', False)], 'sequence': 1},
            'yesterday': {'label': _('Yesterday'), 'domain': [('date_start', '=', date.today() + timedelta(days=-1))], 'sequence': 2},
            'date_start': {'label': _('Today'), 'domain': today_domain, 'order': 3},
            'tomorrow': {'label': _('Tomorrow'), 'domain': [('date_start', '=', date.today() + timedelta(days=1))], 'sequence': 4},
            'day_after_tomorrow': {'label': _('Day After Tomorrow'), 'domain': [('date_start', '=', date.today() + timedelta(days=2))], 'sequence': 5},
            'week': {'label': _('This week'), 'domain': [('date_start', '>=', date_utils.start_of(today, "week")), ('date_start', '<=', date_utils.end_of(today, 'week'))], 'sequence': 6},
            'month': {
                'label': _('This month'), 'domain': [('date_start', '>=', date_utils.start_of(today, 'month')), ('date_start', '<=', date_utils.end_of(today, 'month'))]
            },
            'year': {'label': _('This year'), 'domain': [('date_start', '>=', date_utils.start_of(today, 'year')), ('date_start', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'), 'domain': [('date_start', '>=', quarter_start), ('date_end', '<=', quarter_end)]},
            'last_week': {
                'label': _('Last week'), 'domain': [('date_start', '>=', date_utils.start_of(last_week, "week")), ('date_start', '<=', date_utils.end_of(last_week, 'week'))]
            },
            'last_month': {
                'label': _('Last month'),
                'domain': [('date_start', '>=', date_utils.start_of(last_month, 'month')), ('date_start', '<=', date_utils.end_of(last_month, 'month'))]
            },
            'last_year': {
                'label': _('Last year'), 'domain': [('date_start', '>=', date_utils.start_of(last_year, 'year')), ('date_start', '<=', date_utils.end_of(last_year, 'year'))]
            },
        }

        return searchbar_filters

    @http.route(['/my/tasks', '/my/tasks/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_tasks(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby=None, **kw):
        """
            Replaced for making the default filter is today
        """
        searchbar_filters = self._get_my_tasks_searchbar_filters()

        if not filterby:
            # changed the filterby 'data_start' instead 'all'
            filterby = 'date_start'

        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']

        values = self._prepare_tasks_values(page, date_begin, date_end, sortby, search, search_in, groupby, domain=domain)

        # pager
        pager_vals = values['pager']
        pager_vals['url_args'].update(filterby=filterby)
        pager = portal_pager(**pager_vals)

        values.update({
            'grouped_tasks': values['grouped_tasks'](pager['offset']),
            'pager': pager,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })

        return request.render("project.portal_my_tasks", values)

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from operator import itemgetter

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values['project_com_count'] = request.env['project_com.project_com'].search_count([])
        values['task_count'] = request.env['project_com.task'].search_count([])
        return values

    # ------------------------------------------------------------
    # My Project
    # ------------------------------------------------------------
    def _project_com_get_page_view_values(self, project_com, access_token, **kwargs):
        values = {
            'page_name': 'project_com',
            'project_com': project_com,
        }
        return self._get_page_view_values(project_com, access_token, values, 'my_project_coms_history', False, **kwargs)

    @http.route(['/my/project_coms', '/my/project_coms/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_project_coms(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Project = request.env['project_com.project_com']
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('project_com.project_com', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # project_coms count
        project_com_count = Project.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/project_coms",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=project_com_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        project_coms = Project.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_project_coms_history'] = project_coms.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'project_coms': project_coms,
            'page_name': 'project_com',
            'archive_groups': archive_groups,
            'default_url': '/my/project_coms',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("project_com.portal_my_project_coms", values)

    @http.route(['/my/project_com/<int:project_com_id>'], type='http', auth="public", website=True)
    def portal_my_project_com(self, project_com_id=None, access_token=None, **kw):
        try:
            project_com_sudo = self._document_check_access('project_com.project_com', project_com_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._project_com_get_page_view_values(project_com_sudo, access_token, **kw)
        return request.render("project_com.portal_my_project_com", values)

    # ------------------------------------------------------------
    # My Task
    # ------------------------------------------------------------
    def _task_get_page_view_values(self, task, access_token, **kwargs):
        values = {
            'page_name': 'task',
            'task': task,
            'user': request.env.user
        }
        return self._get_page_view_values(task, access_token, values, 'my_tasks_history', False, **kwargs)

    @http.route(['/my/tasks', '/my/tasks/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_tasks(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby='project_com', **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Title'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'stage': {'input': 'stage', 'label': _('Search in Stages')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'project_com': {'input': 'project_com', 'label': _('Project')},
        }

        # extends filterby criteria with project_com the customer has access to
        project_coms = request.env['project_com.project_com'].search([])
        for project_com in project_coms:
            searchbar_filters.update({
                str(project_com.id): {'label': project_com.name, 'domain': [('project_com_id', '=', project_com.id)]}
            })

        # extends filterby criteria with project_com (criteria name is the project_com id)
        # Note: portal users can't view project_coms they don't follow
        project_com_groups = request.env['project_com.task'].read_group([('project_com_id', 'not in', project_coms.ids)],
                                                                ['project_com_id'], ['project_com_id'])
        for group in project_com_groups:
            proj_id = group['project_com_id'][0] if group['project_com_id'] else False
            proj_name = group['project_com_id'][1] if group['project_com_id'] else _('Others')
            searchbar_filters.update({
                str(proj_id): {'label': proj_name, 'domain': [('project_com_id', '=', proj_id)]}
            })

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('project_com.task', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            if search_in in ('stage', 'all'):
                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])
            domain += search_domain

        # task count
        task_count = request.env['project_com.task'].search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tasks",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=task_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        if groupby == 'project_com':
            order = "project_com_id, %s" % order  # force sort on project_com first to group by project_com in view
        tasks = request.env['project_com.task'].search(domain, order=order, limit=self._items_per_page, offset=(page - 1) * self._items_per_page)
        request.session['my_tasks_history'] = tasks.ids[:100]
        if groupby == 'project_com':
            grouped_tasks = [request.env['project_com.task'].concat(*g) for k, g in groupbyelem(tasks, itemgetter('project_com_id'))]
        else:
            grouped_tasks = [tasks]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_tasks': grouped_tasks,
            'page_name': 'task',
            'archive_groups': archive_groups,
            'default_url': '/my/tasks',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("project_com.portal_my_tasks", values)

    @http.route(['/my/task/<int:task_id>'], type='http', auth="public", website=True)
    def portal_my_task(self, task_id, access_token=None, **kw):
        try:
            task_sudo = self._document_check_access('project_com.task', task_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._task_get_page_view_values(task_sudo, access_token, **kw)
        return request.render("project_com.portal_my_task", values)

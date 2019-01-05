# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.tools.translate import _


class WebsiteBackend(http.Controller):

    @http.route('/tuto_odoo/fetch_dashboard_data', type="json", auth='user')
    def fetch_dashboard_data(self, user_id):
        current_second = request.env['model.second']
        if user_id:
            current_second = current_second.search([('user_id','=',user_id)], limit=1)
        # from ipdb import set_trace; set_trace()
        result_data = {
            'is_configurated': current_second.is_configurated,
            'ga_key': current_second.ga_key,
            'ga_client_id': current_second.ga_client_id,
            'ga_client_secret': current_second.ga_client_secret,
            'domain': current_second.domain,
        }
        return result_data

    @http.route('/tuto_odoo/dashboard/set_ga_data', type='json', auth='user')
    def website_set_ga_data(self, ga_key, ga_client_id, ga_client_secret, domain, user_id):
        current_second = request.env['model.second']
        if user_id:
            if not ga_key or not ga_client_id or not ga_client_secret or not domain:
                return {
                    'error': {
                        'title': _('Incorrect Key / Client ID / Secret / Domain'),
                        'message': _('Please set it again...'),
                    }
                }
            current_second = current_second.search([('user_id','=',user_id)], limit=1)
            if current_second:
                current_second.write({
                    'ga_key': ga_key,
                    'ga_client_id': ga_client_id,
                    'ga_client_secret': ga_client_secret,
                    'domain': domain,
                })
            else:
                current_second.create({
                    'ga_key': ga_key,
                    'ga_client_id': ga_client_id,
                    'ga_client_secret': ga_client_secret,
                    'domain': domain,
                    'user_id': user_id,
                })
        return True
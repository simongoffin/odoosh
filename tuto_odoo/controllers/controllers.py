# -*- coding: utf-8 -*-
from odoo import http

# class FollowMe(http.Controller):
#     @http.route('/follow_me/follow_me/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/follow_me/follow_me/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('follow_me.listing', {
#             'root': '/follow_me/follow_me',
#             'objects': http.request.env['follow_me.follow_me'].search([]),
#         })

#     @http.route('/follow_me/follow_me/objects/<model("follow_me.follow_me"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('follow_me.object', {
#             'object': obj
#         })
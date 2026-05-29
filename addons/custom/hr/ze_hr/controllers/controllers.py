# -*- coding: utf-8 -*-
# from odoo import http


# class ZeHr(http.Controller):
#     @http.route('/ze_hr/ze_hr', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ze_hr/ze_hr/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ze_hr.listing', {
#             'root': '/ze_hr/ze_hr',
#             'objects': http.request.env['ze_hr.ze_hr'].search([]),
#         })

#     @http.route('/ze_hr/ze_hr/objects/<model("ze_hr.ze_hr"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ze_hr.object', {
#             'object': obj
#         })


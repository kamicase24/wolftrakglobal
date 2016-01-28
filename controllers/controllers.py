# -*- coding: utf-8 -*-
from openerp import http

# class Wolftrakglobal(http.Controller):
#     @http.route('/wolftrakglobal/wolftrakglobal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wolftrakglobal/wolftrakglobal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wolftrakglobal.listing', {
#             'root': '/wolftrakglobal/wolftrakglobal',
#             'objects': http.request.env['wolftrakglobal.wolftrakglobal'].search([]),
#         })

#     @http.route('/wolftrakglobal/wolftrakglobal/objects/<model("wolftrakglobal.wolftrakglobal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wolftrakglobal.object', {
#             'object': obj
#         })
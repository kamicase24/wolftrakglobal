# -*- coding: utf-8 -*-
from odoo import http

class Example(http.Controller):
    @http.route('/example', type='http', auth='public', website=True)
    def render_example_page(self):
        return http.request.render('wolftrakglobal.example_page', {})

    @http.route('/example/detail', type='http', auth='public', website=True)
    def navigate_to_detail_page(self):
        return http.request.render('wolftrakglobal.detail_page', {})
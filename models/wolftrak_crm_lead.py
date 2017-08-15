# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
_logger = logging.getLogger(__name__)


class LeadWolftrak(models.Model):
    _inherit = "crm.lead"

    def update_fields(self):

        _logger.info(self.partner_id.street)
        _logger.info(self.street)
        _logger.info(self.partner_id.street2)
        _logger.info(self.street2)
        _logger.info(self.partner_id.city)


        if self.partner_id.email:
            self.email_from = self.partner_id.email
        if self.partner_id.phone:
            self.phone = self.partner_id.phone
        if self.partner_id.street:
            self.street = self.partner_id.street
        if self.partner_id.street2:
            self.street2 = self.partner_id.street2
        if self.partner_id.city:
            self.city = self.partner_id.city
        if self.partner_id.state_id:
            self.state_id = self.partner_id.state_id
        if self.partner_id.zip:
            self.zip = self.partner_id.zip
        if self.partner_id.country_id:
            self.country_id = self.partner_id.country_id

    @api.onchange('partner_id')
    def confirm_rnc(self):
        if self.partner_id:
            if self.partner_id.doc_ident:
                self.confirm_note = """<p style='color: blue'> %s </p>""" % self.partner_id.doc_ident
            else:
                self.confirm_note = """<p style='color: red'>El cliente no posee RNC</p>"""

    country_id = fields.Many2one('res.country', string='Country', default=62)
    confirm_note = fields.Html(string='RNC')

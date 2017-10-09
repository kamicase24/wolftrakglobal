# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)


class WolftrakPurchase(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def _set_custom_currency(self):
        _logger.info("CUSTOM CURRENCY")
        _logger.info(self.currency_id.name)
        if self.currency_id.name == 'DOP':
            self.currency_id = 3

    def currency_exchange(self):
        self.env['wolftrak.tools'].currency_exchange(self)

    ex_rate = fields.Float(string='Tasa de Cambio', digits=(1, 4),
                           default=lambda self: self.env['wolftrak.tools'].default_ex_rate_2())

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.fiscal_position_id = False
            self.payment_term_id = False
            self.currency_id = False
        else:
            self.fiscal_position_id = self.env['account.fiscal.position'].with_context(company_id=self.company_id.id).get_fiscal_position(self.partner_id.id)
            self.payment_term_id = self.partner_id.property_supplier_payment_term_id.id
            if self.currency_id.name == 'DOP' or not self.currency_id:
                self.currency_id = 3
        return {}

# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError
_logger = logging.getLogger(__name__)


class ProductWolftrak(models.Model):
    _inherit = "product.template"

    @api.multi
    def _compute_currency_id(self):

        for template in self:
            template.currency_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)

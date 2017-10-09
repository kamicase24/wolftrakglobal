import logging
from odoo import api, fields, models, _
from bs4 import BeautifulSoup
import requests
_logger = logging.getLogger(__name__)


class WolftrakSaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    def currency_exchange(self):
        self.env['wolftrak.tools'].currency_exchange(self)

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, readonly=True,
                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                   help="Pricelist for current sales order.", default=2)
    ex_rate = fields.Float(string='Tasa de Cambio del dia', digits=(1, 4),
                           default=lambda self: self.env['wolftrak.tools'].default_ex_rate_2())

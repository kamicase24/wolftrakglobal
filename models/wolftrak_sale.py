import logging
from odoo import api, fields, models, _
from bs4 import BeautifulSoup
import requests
_logger = logging.getLogger(__name__)


class WolftrakSaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    def default_ex_rate(self):
        page = requests.get('http://promerica.com.do/')
        soup = BeautifulSoup(page.content, 'lxml')
        body = soup.body
        result = body.marquee.string
        venta = result[result.find('V'):]
        rate = float(venta[venta.find('$')+1:venta.find('$')+6])
        user = self.env.user
        if user.company_id.name == 'MYTRAK TECHNOLOGY SRL':
            return rate
        else:
            return 0.0

    def default_ex_rate_2(self):
        page = requests.get('https://www.banreservas.com/calculators/divisas')
        soup = BeautifulSoup(page.content, 'lxml')
        body = soup.body
        rate = body.find_all('span')[1].string
        user = self.env.user
        if user.company_id.name == 'MYTRAK TECHNOLOGY SRL':
            return rate
        else:
            return 0.0

    def currency_exchange(self):
        line_ids = self.order_line
        if self.currency_id.name == 'USD':
            _logger.info('Dolares 3')
            _logger.info('Dolares(SO) 2')
            for line in line_ids:
                _logger.info('inicial')
                _logger.info(line.price_unit)
                line.price_unit = line.price_unit * self.ex_rate
                self.pricelist_id = 1
        elif self.currency_id.name == 'DOP':
            _logger.info('Pesos Dominicanos 74')
            _logger.info('Pesos Dominicanos(SO) 1')
            for line in line_ids:
                line.price_unit = line.price_unit / self.ex_rate
                self.pricelist_id = 2

    @api.onchange('order_line')
    def _currency_exchange_online(self):
        if self.order_line:
            for line in self.order_line:
                if line.currency_id.name == 'USD':
                    line.price_unit = line.price_unit * self.ex_rate
                    self.pricelist_id = 1
                    line.currency_id = 74

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order.", default=2)
    ex_rate = fields.Float(string='Tasa de Cambio del dia', digits=(1, 4), default=default_ex_rate_2)

from odoo import api, fields, models, _
from bs4 import BeautifulSoup
import requests

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
        if user.company_id.name == 'Mytraktech':
            return rate
        else:
            return 0.0

    def default_ex_rate_2(self):
        page = requests.get('https://www.banreservas.com/calculators/divisas')
        soup = BeautifulSoup(page.content, 'lxml')
        body = soup.body
        rate = body.find_all('span')[1].string
        user = self.env.user
        if user.company_id.name == 'Mytraktech':
            return rate
        else:
            return 0.0

    ex_rate = fields.Float(string='Tasa de Cambio del dia', digits=(1,4), default=default_ex_rate_2)
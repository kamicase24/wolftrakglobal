# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
from bs4 import BeautifulSoup
import requests

class WolftrakCurrencyRate(models.Model):
	_name = "res.currency.rate"
	_inherit = "res.currency.rate"

	def default_ex_rate(self):
		page = requests.get('http://promerica.com.do/')
		soup = BeautifulSoup(page.content, 'lxml')
		body = soup.body
		result = body.marquee.string
		venta = result[result.find('V'):]
		rate = float(venta[venta.find('$') + 1:venta.find('$') + 6])
		user = self.env.user
		if user.company_id.name == 'Mytraktech':
			return rate
		else:
			return 0.0

	rate = fields.Float(default=default_ex_rate)
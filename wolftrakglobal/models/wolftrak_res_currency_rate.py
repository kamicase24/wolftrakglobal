# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
from bs4 import BeautifulSoup
import requests

class WolftrakCurrencyRate(models.Model):
	_name = "res.currency.rate"
	_inherit = "res.currency.rate"

	def default_ex_rate(self):
		# page = requests.get('http://promerica.com.do/?d=1014')
		# soup = BeautifulSoup(page.content, 'lxml')
		# form = soup.body
		# result = form.find_all(href='http://www.promerica.com.do/?p=1014')
		# link = result[0]
		# str_final = link.string
		# venta = str_final[str_final.find('V'):].encode('utf-8')
		# rate = float(venta[venta.find('$') + 1:venta.find('$') + 6])
		# user = self.env.user
		# if user.company_id.name == 'Mytraktech':
		# 	return rate
		# else:
		return 0.0

	rate = fields.Float(default=default_ex_rate)
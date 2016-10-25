# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
import time
import math

from openerp import api, fields as fields2
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_round, float_is_zero, float_compare
import json

from bs4 import BeautifulSoup
from lxml import etree
from io import StringIO, BytesIO
import string
import requests
import lxml

page = requests.get('http://www.promerica.com.do/?p=1014')
content = page.content
soup = BeautifulSoup(content, 'lxml')
form_1 = soup.body

result_2 = form_1.find_all(href='http://www.promerica.com.do/?p=1014')

link_2 = result_2[1]

str_final = link_2['title'].encode('utf-8')

compra = str_final[str_final.find('V'):]
venta = str_final[str_final.find('C'):str_final.find('/')-1]
solo_venta = venta[venta.find('$')+1:]
solo_compra = compra[compra.find('$')+1:]
float_venta = float(venta[venta.find('$')+1:])
float_compra = float(compra[compra.find('$')+1:])

class res_currency_rate(osv.osv):
	_name = "res.currency.rate"
	_inherit = "res.currency.rate"

	_defaults = {
	'rate' : float_venta
	}
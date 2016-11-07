from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

from bs4 import BeautifulSoup
from lxml import etree
from io import StringIO, BytesIO
import string
import requests
import lxml

def taza_de_cambio(aja):
	eje = aja
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
	float_compra = float(venta[venta.find('$')+1:])
	float_venta = float(compra[compra.find('$')+1:])
	return float_venta
	
class wolftraksale(models.Model):
	_name = "sale.order"
	_inherit = "sale.order"

	tasa_cambio = fields.Float(string='Tasa de Cambio del dia', digits=(1,4), default=taza_de_cambio)
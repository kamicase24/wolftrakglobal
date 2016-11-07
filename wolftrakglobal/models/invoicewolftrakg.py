# -*- coding: utf-8 -*-
import requests, json
import sys, os
from bs4 import BeautifulSoup
from openerp import models, fields #importa los objetos models y fields de el Core de Odoo
from openerp.osv import orm
from openerp import models, fields, api

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
	float_venta = float(venta[venta.find('$')+1:])
	float_compra = float(compra[compra.find('$')+1:])
	return float_venta

main_base = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_NAME = 'ncf.json'
CONFIG_FILE = os.path.join(main_base, CONFIG_FILE_NAME)

def load_config(json_file):
	with open(json_file, 'r') as file:
		config_data = json.load(file)
		return config_data

def get_ncf_record(ncf,rnc, config_data = None):
	if not config_data:
		config_data = load_config(CONFIG_FILE)
	req_headers = config_data['request_headers']
	req_cookies = config_data['request_cookies']
	req_params = config_data['request_parameters']
	uri = ''.join([config_data['url'], config_data['web_resource']])

	req_params['txtNCF'] = ncf
	req_params['txtRNC'] = rnc

	result = requests.get(uri, params = req_params, headers = req_headers)
	if result.status_code == requests.codes.ok:
		soup = BeautifulSoup(result.content)
		if soup.find('span', attrs={'id': 'lblContribuyente'}):
			data_rows1 = soup.find('span', attrs={'id': 'lblContribuyente'})
			data_rows2 = soup.find('span', attrs={'id': 'lblTipoComprobante'})
			span = []
			span.append(data_rows1.string)
			span.append(data_rows2.string)
			return span
		else:
			print soup.find('span', attrs={'id': 'lblErrorWebService'}).string

class wolftraknew(orm.Model): #declara un nuevo modelo. Deriva de models.Model
	#define el atributo _nombre, identificador que sera usado por Odoo para referises a este modelo 
	_name = 'account.invoice'
	_inherit = 'account.invoice'

	ncf = fields.Char(string="Numero de Comprobante Fiscal")

	tax_hold = fields.Monetary(string="ITBIS Retenido")

	type_ci = fields.Char(string="Tipo de Id")

	isr = fields.Selection([('0.3','30%'),
							('0.27','27%')], string="Impuesto Sobre la Renta")

	isr_hold = fields.Float(string="Total retenido")

	isr_date = fields.Date(string="Fecha de la Retencion")

	type_buy = fields.Selection([('01','01 - Gastos de personal'),
								('02','02 - Gastos por trabajos suministros y servicios'),
								('03','03 - Arrendamientos'),
								('04','04 - Gastos de activos fijo'),
								('05','05 - Gastos de representación'),
								('06','06 - Otras deducciones admitisdas'),
								('07','07 - Gastos financieros'),
								('08','08 - Gastos Extraordinarios'),
								('09','09 - Compras y Gastos que formarann parte del costo de venta'),
								('10','10 - Adquisiciones de activos'),
								('11','11 - Gastos de Seguros')], string="Tipo de Bienes o Servicios comprados")

	type_nul = fields.Selection([('01','01 Deterioro de Factura Pre-Imresa'),
								('02','02 Errores de Impresión (factura Pre-Impresa)'),
								('03','03 Impresión Defectuosa'),
								('04','04 Duplicidad de Factura'),
								('05','05 Correción de la Información'),
								('06','06 Cambio de Productos'),
								('07','07 Devolución de Productos'),
								('08','08 Omisión de Productos'),
								('09','09 Errores de Secuencias de NCF')], string="Tipo de Anulación")

	type_comp = fields.Char(string="Tipo de Comprobante", readonly=True, compute='ncf_validation')

	ncf_result = fields.Char(string="Resultado", readonly=True, compute='ncf_validation')

	taza_cambio = fields.Float(string='Tasa de Cambio', digits=(1,4), default=taza_de_cambio)

	@api.onchange('isr')
	def isr_holding(self):

		self.isr_hold = self.amount_total * float(self.isr)

	@api.onchange('amount_tax')
	def tax_holding(self):

		p_id = self.partner_id.id
		partner = self.env['res.partner'].search([('id', '=', p_id)])
		rnc = partner.ci
		if type(rnc) != bool:
			if len(rnc) == 11: 
				# Es una persona natural
				self.tax_hold += self.amount_tax*1.0
				self.type_ci = 2
			else:
				self.tax_hold += 0.0
				self.type_ci = 1

	@api.depends('ncf')
	def ncf_validation(self):
		supplier_rnc = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
		values = get_ncf_record(self.ncf,supplier_rnc.ci)
		if values != None:
			self.type_comp = values[1]
			self.ncf_result = "El Número de Comprobante Fiscal digitado es válido."
		else:
			self.ncf_result = "El Número de Comprobante Fiscal ingresado no es correcto o no corresponde a este RNC"

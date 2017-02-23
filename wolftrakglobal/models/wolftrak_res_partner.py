# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
import requests, json
import sys, os
from bs4 import BeautifulSoup
from rnc_wolftrak import Rnc

main_base = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_NAME = "config.json"      
CONFIG_FILE = os.path.join(main_base, CONFIG_FILE_NAME)

def load_config(json_file):
	with open(json_file, 'r') as file:    
		config_data = json.load(file)            
	return config_data
  
def get_rnc_record(rnc, config_data = None):

	if not config_data:
		config_data = load_config(CONFIG_FILE)  
	req_headers = config_data['request_headers'] 
	# req_cookies = config_data.get('request_cookies')
	req_params = config_data['request_parameters']    
	uri = ''.join([config_data['url'], config_data['web_resource']])  

	req_params['txtRncCed'] = rnc
	result = requests.get(uri, params = req_params, headers=req_headers)  
	if result.status_code == requests.codes.ok:
		soup = BeautifulSoup(result.content)             
		data_rows  = soup.find('tr', attrs={'class': 'GridItemStyle'})
		try:
			tds = data_rows.findChildren('td')   
			rnc_vals = [str(td.text.strip()) for td in tds]
			# rnc = Rnc(rnc_vals)
			return rnc_vals
		except :
			pass

class WolftrakPartner(models.Model):
	_name = "res.partner"
	_inherit = "res.partner"

	doc_ident = fields.Char(string='Documento de Identificación')
	dgii_state = fields.Char(string='Estado')
	pay_reg = fields.Char(string='Regimen de Pago')

	def _get_partner_invoices(self):
		invoices = self.env['account.invoice']
		par_inv = invoices.search([])
		return par_inv

	def _get_invoices(self):
		invoices = self.env['account.invoice']
		par_inv = invoices.search([])
		for partner in self:
			partner.partner_inv += par_inv.search([('partner_id','=',partner.id)])

	partner_inv = fields.Many2many('account.invoice', default=_get_partner_invoices, compute=_get_invoices)

	@api.onchange('doc_ident')
	def user_validation(self):
		db_doc_ident = self.search([('doc_ident', '=', self.doc_ident)])
		if db_doc_ident and self.doc_ident:
			self.doc_ident = ''
			self.name = ''
			self.dgii_state = ''

		try:
			rnc_record = get_rnc_record(self.doc_ident)
			self.name = rnc_record[1]
			self.dgii_state = rnc_record[5]
			self.pay_reg = rnc_record[4]
		except :
			pass
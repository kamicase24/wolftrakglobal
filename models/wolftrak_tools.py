# -*- coding: utf-8 -*-
import re
import time
import json
import logging
import unicodedata
import sys, os
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from bs4 import BeautifulSoup
import requests
import datetime
from datetime import date
import calendar
_logger = logging.getLogger(__name__)
main_base = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_NAME = "config.json"
CONFIG_FILE = os.path.join(main_base, CONFIG_FILE_NAME)

CONFIG_FILE_NAME_2 = 'ncf.json'
CONFIG_FILE_2 = os.path.join(main_base, CONFIG_FILE_NAME_2)


class WolftrakTools(models.Model):
    _name = 'wolftrak.tools'

    @api.multi
    def load_config(self, json_file):
        with open(json_file, 'r') as file:
            config_data = json.load(file)
        return config_data

    def get_rnc_record(self, rnc, config_data=None):
        if not config_data:
            config_data = self.load_config(CONFIG_FILE)
        req_headers = config_data['request_headers']
        # req_cookies = config_data.get('request_cookies')
        req_params = config_data['request_parameters']
        uri = ''.join([config_data['url'], config_data['web_resource']])

        req_params['txtRncCed'] = rnc
        result = requests.get(uri, params=req_params, headers=req_headers)
        if result.status_code == requests.codes.ok:
            soup = BeautifulSoup(result.content)
            data_rows = soup.find('tr', attrs={'class': 'GridItemStyle'})
            try:
                tds = data_rows.findChildren('td')
                rnc_vals = [str(td.text.strip()) for td in tds]
                # rnc = Rnc(rnc_vals)
                return rnc_vals
            except:
                pass

    def get_ncf_record(self, ncf, rnc, config_data=None):
        if not config_data:
            config_data = self.load_config(CONFIG_FILE_2)
        req_headers = config_data['request_headers']
        # req_cookies = config_data['request_cookies']
        req_params = config_data['request_parameters']
        uri = ''.join([config_data['url'], config_data['web_resource']])
        req_params['txtNCF'] = ncf
        req_params['txtRNC'] = rnc
        result = requests.get(uri, params=req_params, headers=req_headers)
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

    def default_ex_rate(self):
        if not self.ex_rate:
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
        if user.company_id.name == 'MYTRAK TECHNOLOGY SRL':
            return rate
        else:
            return 0.0

    def currency_exchange(self, record):
        _logger.info(record)
        _logger.info(record._name)
        line_ids = False
        if record._name == 'purchase.order' or record._name == 'sale.order':
            line_ids = record.order_line
        elif record._name == 'account.invoice':
            line_ids = record.invoice_line_ids

        if record.currency_id.name == 'USD':
            _logger.info('Dolares 3')
            _logger.info(record.currency_id.id)
            _logger.info(record.currency_id.name)
            for line in line_ids:
                _logger.info('inicial')
                _logger.info(line.price_unit)
                line.price_unit = line.price_unit * record.ex_rate
                record.currency_id = 74
                if record._name == 'sale.order':
                    record.pricelist_id = 1

            if record._name == 'account.invoice':
                for line_tax in record.tax_line_ids:
                    tax = record.env['account.tax'].search([('id', '=', line_tax.tax_id.id)])
                    _logger.info(tax.amount)
                    _logger.info(line_tax.base)
                    line_tax.amount = (line_tax.base * tax.amount) / 100
                record.amount_tax = sum(line_tax.amount for line_tax in record.tax_line_ids)

        elif record.currency_id.name == 'DOP':
            _logger.info('Pesos Dominicanos 74')
            _logger.info(record.currency_id.id)
            _logger.info(record.currency_id.name)
            for line in line_ids:
                line.price_unit = line.price_unit / record.ex_rate
                record.currency_id = 3
                if record._name == 'sale.order':
                    record.pricelist_id = 2

            if record._name == 'account.invoice':
                for line_tax in record.tax_line_ids:
                    tax = record.env['account.tax'].search([('id', '=', line_tax.tax_id.id)])
                    _logger.info(tax.amount)
                    _logger.info(line_tax.base)
                    line_tax.amount = (line_tax.base * tax.amount) / 100
                record.amount_tax = sum(line_tax.amount for line_tax in record.tax_line_ids)
        return True


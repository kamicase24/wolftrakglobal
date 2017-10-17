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


class WolftrakTools(models.Model):
    _name = 'wolftrak.tools'

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


# -*- coding: utf-8 -*-
import time
import json
import logging
import sys, os
from odoo import api, fields, models, _
from bs4 import BeautifulSoup
import requests
from datetime import date
import calendar
_logger = logging.getLogger(__name__)

main_base = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_NAME = 'ncf.json'
CONFIG_FILE = os.path.join(main_base, CONFIG_FILE_NAME)


def load_config(json_file):
    with open(json_file, 'r') as wfile:
        config_data = json.load(wfile)
        return config_data

def get_ncf_record(ncf, rnc, config_data=None):
    if not config_data:
        config_data = load_config(CONFIG_FILE)
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


class WolftrakInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

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
        if user.company_id.name == 'MYTRAK TECHNOLOGY SRL':
            return rate
        else:
            return 0.0

    def default_draft_number(self):
        invoices = self.env['account.invoice'].search([], limit=1, order='draft_number desc')
        last_id = invoices and max(invoices)
        date_str = str(date.today().year)+str(date.today().month)
        if not last_id.draft_number:
            return 'OP/'+date_str+'/0001'
        else:
            number = int(''.join(last_id.draft_number[9:]))+1
            return 'OP/'+date_str+'/'+str(number).zfill(last_id.draft_number[9:].count('0')+1)

    def currency_exchange(self):
        line_ids = self.invoice_line_ids
        if self.currency_id.name == 'USD':
            _logger.info('Dolares 3')
            _logger.info(self.currency_id.id)
            _logger.info(self.currency_id.name)
            for line in line_ids:
                _logger.info('inicial')
                _logger.info(line.price_unit)
                line.price_unit = line.price_unit * self.ex_rate
                self.currency_id = 74
            for line_tax in self.tax_line_ids:
                tax = self.env['account.tax'].search([('id', '=', line_tax.tax_id.id)])
                _logger.info(tax.amount)
                _logger.info(line_tax.base)
                line_tax.amount = (line_tax.base * tax.amount) / 100
            self.amount_tax = sum(line_tax.amount for line_tax in self.tax_line_ids)

        elif self.currency_id.name == 'DOP':
            _logger.info('Pesos Dominicanos 74')
            _logger.info(self.currency_id.id)
            _logger.info(self.currency_id.name)
            for line in line_ids:
                line.price_unit = line.price_unit / self.ex_rate
                self.currency_id = 3
            for line_tax in self.tax_line_ids:
                tax = self.env['account.tax'].search([('id', '=', line_tax.tax_id.id)])
                _logger.info(tax.amount)
                _logger.info(line_tax.base)
                line_tax.amount = (line_tax.base * tax.amount) / 100
            self.amount_tax = sum(line_tax.amount for line_tax in self.tax_line_ids)

    @api.multi
    def invoice_validate(self):
        self.date_invoice = time.strftime('%Y-%m-%d')
        return self.write({'state': 'open'})


    draft_number = fields.Char(readonly=False, default=default_draft_number)

    ncf = fields.Char(string="Número de Comprobante Fiscal")

    type_comp = fields.Char(string="Tipo de Comprobante", readonly=True, compute='ncf_validation')

    ncf_result = fields.Char(string="Resultado", readonly=True, compute='ncf_validation')

    tax_hold = fields.Monetary(string="ITBIS Retenido")

    type_ci = fields.Char(string="Tipo de Identificación")

    isr = fields.Selection([('0.3', '30%'),
                            ('0.27', '27%')], string="Impuesto Sobre la Renta")

    isr_hold = fields.Float(string="Total retenido")

    isr_date = fields.Date(string="Fecha de la Retencion")

    type_buy = fields.Selection([('01', '01 - Gastos de personal'),
                                ('02', '02 - Gastos por trabajos suministros y servicios'),
                                ('03', '03 - Arrendamientos'),
                                ('04', '04 - Gastos de activos fijo'),
                                ('05', '05 - Gastos de representación'),
                                ('06', '06 - Otras deducciones admitidas'),
                                ('07', '07 - Gastos financieros'),
                                ('08', '08 - Gastos Extraordinarios'),
                                ('09', '09 - Compras y Gastos que formaran parte del costo de venta'),
                                ('10', '10 - Adquisiciones de activos'),
                                ('11', '11 - Gastos de Seguros')], string="Tipo de Bienes o Servicios comprados")

    type_nul = fields.Selection([('01', '01 Deterioro de Factura Pre-Imresa'),
                                ('02', '02 Errores de Impresión (factura Pre-Impresa)'),
                                ('03', '03 Impresión Defectuosa'),
                                ('04', '04 Duplicidad de Factura'),
                                ('05', '05 Correción de la Información'),
                                ('06', '06 Cambio de Productos'),
                                ('07', '07 Devolución de Productos'),
                                ('08', '08 Omisión de Productos'),
                                ('09', '09 Errores de Secuencias de NCF')], string="Tipo de Anulación")

    ex_rate = fields.Float(string='Tasa de Cambio', digits=(1, 4), default=default_ex_rate_2)

    comment = fields.Text(string='Additional Information', readonly=False, states={'draft': [('readonly', False)]})

    @api.onchange('date_invoice')
    def _compute_draft_number(self):
        invoices = self.env['account.invoice'].search([], limit=1, order='draft_number desc')
        last_id = invoices and max(invoices)
        date_str = str(date.today().year)+str(date.today().month)
        if not last_id.draft_number:
            self.draft_number = 'OP/'+date_str+'/1'
        else:
            inv_chain = self.env['account.invoice'].search([], order='id asc')
            i = 0
            for inv in inv_chain:
                number = int(inv.draft_number[9:])
                if number > i:
                    i = number
            _logger.info("contador: "+str(i))
            self.draft_number = "OP/"+date_str+"/"+str(i+1)
            _logger.info(self.draft_number)
            # if self.draft_number != last_id.draft_number:
            #     _logger.info(last_id.draft_number)
            #     number = int(''.join(last_id.draft_number[9:]))+1
            #     _logger.info(number)
            #     self.draft_number = 'OP/'+date_str+'/'+str(number)
            #     _logger.info(self.draft_number)

    @api.onchange('isr')
    def isr_holding(self):
        self.isr_hold = self.amount_total * float(self.isr)

    @api.onchange('amount_tax')
    def tax_holding(self):
        p_id = self.partner_id.id
        partner = self.env['res.partner'].search([('id', '=', p_id)])
        rnc = partner.doc_ident
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
        values_in_inv = get_ncf_record(self.ncf, supplier_rnc.doc_ident)
        values_out_inv = get_ncf_record(self.ncf, '131104371')
        if self.type == 'out_invoice':
            # if values_out_inv != None:
            if values_out_inv is not None:
                self.type_comp = values_out_inv[1]
                self.ncf_result = "El Número de Comprobante Fiscal digitado es válido."
            else:
                self.ncf_result = "El Número de Comprobante Fiscal ingresado no es correcto o no corresponde a este RNC"
        else:
            # if values_in_inv != None:
            if values_in_inv is not None:
                self.type_comp = values_in_inv[1]
                self.ncf_result = "El Número de Comprobante Fiscal digitado es válido."
            else:
                self.ncf_result = "El Número de Comprobante Fiscal ingresado no es correcto o no corresponde a este RNC"


class WolftrakInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    description = fields.Char(string='Detalle', default="Mes: " + calendar.month_name[date.today().month])


class WolftrakMove(models.Model):
    _inherit = "account.move"

    partner_id = fields.Many2one('res.partner', compute='_compute_partner_id', string="Partner", store=True)

    ncf = fields.Char(string="Número de Comprobante Fiscal")

    type_comp = fields.Char(string="Tipo de Comprobante", readonly=True, compute='ncf_validation')

    ncf_result = fields.Char(string="Resultado", readonly=True, compute='ncf_validation')

    type_buy = fields.Selection([('01', '01 - Gastos de personal'),
                                ('02', '02 - Gastos por trabajos suministros y servicios'),
                                ('03', '03 - Arrendamientos'),
                                ('04', '04 - Gastos de activos fijo'),
                                ('05', '05 - Gastos de representación'),
                                ('06', '06 - Otras deducciones admitidas'),
                                ('07', '07 - Gastos financieros'),
                                ('08', '08 - Gastos Extraordinarios'),
                                ('09', '09 - Compras y Gastos que formaran parte del costo de venta'),
                                ('10', '10 - Adquisiciones de activos'),
                                ('11', '11 - Gastos de Seguros')], string="Tipo de Bienes o Servicios comprados")

    rent_hold = fields.Float(string="Retención de Renta", default=0.00)

    tax_hold = fields.Float(string="ITBIS Retenido", default=0.00)

    @api.depends('ncf')
    def ncf_validation(self):
        supplier_rnc = self.partner_id
        values_in_inv = get_ncf_record(self.ncf, supplier_rnc.doc_ident)
        # if values_in_inv != None:
        if values_in_inv is not None:
            self.type_comp = values_in_inv[1]
            self.ncf_result = "El Número de Comprobante Fiscal digitado es válido."
        else:
            self.ncf_result = "El Número de Comprobante Fiscal ingresado no es correcto o no corresponde a este RNC"

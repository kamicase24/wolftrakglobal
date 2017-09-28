# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import requests, json
import sys, os
from bs4 import BeautifulSoup
_logger = logging.getLogger(__name__)
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

    @api.multi
    def _total_device(self):
        invoices = self.env['account.invoice']

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self:
            all_partners_and_children[partner] = self.search([('id', 'child_of', partner.id)]).ids
            all_partner_ids += all_partners_and_children[partner]

        for partner, child_ids in all_partners_and_children.items():
            gps_devices = self.env['gps.device'].search([('partner_id', '=', partner.id)])
            _logger.info(len(gps_devices))
            partner.total_device = len(gps_devices)
        return False

    def _default_user_id(self):
        return self.env.uid

    doc_ident = fields.Char(string='Documento de Identificación')
    dgii_state = fields.Char(string='Estado')
    pay_reg = fields.Char(string='Regimen de Pago')
    doc_ident_type = fields.Integer(string='Tipo de Documento')
    user_id = fields.Many2one('res.users', string='Comercial', default=_default_user_id)
    total_device = fields.Integer(string='Dispositivos', help='Total de dispositivos vendidos a este cliente', compute=_total_device)
    start_date = fields.Date(string='Fecha de Inicio', help='Fecha en que inicio el contrato el cliente.')

    def _get_partner_invoices(self):
        invoices = self.env['account.invoice']
        par_inv = invoices.search([])
        return par_inv

    def _get_invoices(self):
        invoices = self.env['account.invoice']
        par_inv = invoices.search([])
        for partner in self:
            partner.partner_inv += par_inv.search([('partner_id', '=', partner.id)])

    partner_inv = fields.Many2many('account.invoice', default=_get_partner_invoices, compute=_get_invoices)

    @api.onchange('doc_ident', 'phone')
    def user_validation(self):

        if self.doc_ident:
            if len(self.doc_ident) == 11:
                self.doc_ident_type = 2
            elif len(self.doc_ident) == 9:
                self.doc_ident_type = 1

        db_doc_ident = self.search([('doc_ident', '=', self.doc_ident)])
        if db_doc_ident and self.doc_ident:
            self.doc_ident = ''
            raise ValidationError(_('Este Cliente ya se encuentra registrado'))
        db_user_client = self.search([('phone', '=', self.phone)])
        if db_user_client and self.phone:
            self.phone = ''
            raise ValidationError(_('Este Cliente ya se encuentra registrado'))
        try:
            rnc_record = get_rnc_record(self.doc_ident)
            self.name = rnc_record[1]
            self.dgii_state = rnc_record[5]
            self.pay_reg = rnc_record[4]
        except:
            pass

    def device_history(self):
        invoices = self.env['account.invoice']
        partner_invoices = invoices.search([('partner_id', '=', self.id)])
        for invoice in partner_invoices:
            for line in invoice.invoice_line_ids:
                _logger.info(line.name)

        _logger.info("Dispositivos: ")
        _logger.info(partner_invoices)

        action = self.env.ref('wolftrakglobal.action_partner_device_lines')
        result = action.read()[0]
        # result['domain'] = [('partner_id', 'in', self.ids), ('product_id', 'in', [2, 4])]
        result['domain'] = [('partner_id', 'in', self.ids)]
        return result

    @api.multi
    @api.depends('country_id')
    def _compute_product_pricelist(self):
        for p in self:
            if not isinstance(p.id, models.NewId):  # if not onchange
                p.property_product_pricelist = self.env['product.pricelist'].search([('id', '=', 2)])
                # p.property_product_pricelist = self.env['product.pricelist']._get_partner_pricelist(p.id)

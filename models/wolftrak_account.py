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

# def load_config(json_file):
#     with open(json_file, 'r') as wfile:
#         config_data = json.load(wfile)
#         return config_data
#
#
# def get_ncf_record(ncf, rnc, config_data=None):
#     if not config_data:
#         config_data = load_config(CONFIG_FILE)
#     req_headers = config_data['request_headers']
#     # req_cookies = config_data['request_cookies']
#     req_params = config_data['request_parameters']
#     uri = ''.join([config_data['url'], config_data['web_resource']])
#     req_params['txtNCF'] = ncf
#     req_params['txtRNC'] = rnc
#     result = requests.get(uri, params=req_params, headers=req_headers)
#     if result.status_code == requests.codes.ok:
#         soup = BeautifulSoup(result.content)
#         if soup.find('span', attrs={'id': 'lblContribuyente'}):
#             data_rows1 = soup.find('span', attrs={'id': 'lblContribuyente'})
#             data_rows2 = soup.find('span', attrs={'id': 'lblTipoComprobante'})
#             span = []
#             span.append(data_rows1.string)
#             span.append(data_rows2.string)
#             return span
#         else:
#             print soup.find('span', attrs={'id': 'lblErrorWebService'}).string


class WolftrakInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    def default_draft_number(self):
        invoices = self.env['account.invoice'].search([], limit=1, order='id desc')
        last_id = invoices and max(invoices)
        date_str = str(date.today().year)+str(date.today().month)
        if not last_id.draft_number:
            return 'OP/'+date_str+'/0001'
        else:
            number = int(re.findall(r'\d+', last_id.draft_number[9:])[0])+1
            return 'OP/'+date_str+'/'+str(number).zfill(last_id.draft_number[9:].count('0')+1)

    @api.onchange('partner_id')
    def _set_custom_currency(self):
        if self.currency_id.name == 'DOP' and self.partner_shipping_id:
            self.currency_id = 3

    def currency_exchange(self):
        self.env['wolftrak.tools'].currency_exchange(self)

    def move_rename(self, type):
        new_move = self.env['account.move'].search([('id', '=', self.move_id.id)])
        if type == 'payorder':
            sql = "update account_move set name = '%s' where id = %s" % (self.draft_number, new_move.id)
            self.env.cr.execute(sql)
        if type == 'open':
            sql = "update account_move set name = '%s' where id = %s" % (self.number, new_move.id)
            self.env.cr.execute(sql)

    def pay_order(self):
        to_open_invoices = self.filtered(lambda inv: inv.state != 'payorder')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft', 'open']):
            raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        to_open_invoices.move_rename('payorder')
        return to_open_invoices.invoice_validate_payorder()

    def action_invoice_open2(self):
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open2')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft', 'payorder']):
            raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
        if not self.state == 'payorder':
            to_open_invoices.action_date_assign()
            to_open_invoices.action_move_create()
        to_open_invoices.move_rename('open')
        return to_open_invoices.invoice_validate_no_tax()

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft', 'payorder']):
            raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
        if not self.state == 'payorder':
            to_open_invoices.action_date_assign()
            to_open_invoices.action_move_create()
        to_open_invoices.move_rename('open')
        return to_open_invoices.invoice_validate()

    @api.multi
    def invoice_validate(self):
        if self.currency_id.name == 'DOP':
            self.date_invoice = time.strftime('%Y-%m-%d')
            return self.write({'state': 'open'})
        else:
            raise ValidationError(_("La factura no puede pasar al siguiente estado mientras que su moneda no sea DOP"))

    def invoice_validate_no_tax(self):
        if self.currency_id.name == 'DOP':
            for invoice in self:
                if invoice.type in ('in_invoice', 'in_refund') and invoice.reference:
                    if self.search([('type', '=', invoice.type),
                                    ('reference', '=', invoice.reference),
                                    ('company_id', '=', invoice.company_id.id),
                                    ('commercial_partner_id', '=', invoice.commercial_partner_id.id),
                                    ('id', '!=', invoice.id)]):
                        raise UserError(_("Duplicated vendor reference detected. "
                                          "You probably encoded twice the same vendor bill/refund."))
            self.date_invoice = time.strftime('%Y-%m-%d')
            return self.write({'state': 'open2'})

        else:
            raise ValidationError(_("La factura no puede pasar al siguiente estado mientras que su moneda no sea DOP"))

    @api.multi
    def invoice_validate_payorder(self):
        if self.currency_id.name == 'DOP':
            for invoice in self:
                if invoice.type in ('in_invoice', 'in_refund') and invoice.reference:
                    if self.search([('type', '=', invoice.type),
                                    ('reference', '=', invoice.reference),
                                    ('company_id', '=', invoice.company_id.id),
                                    ('commercial_partner_id', '=', invoice.commercial_partner_id.id),
                                    ('id', '!=', invoice.id)]):
                        raise UserError(_("Duplicated vendor reference detected. "
                                          "You probably encoded twice the same vendor bill/refund."))
            return self.write({'state': 'payorder'})
        else:
            raise ValidationError(_("La factura no puede pasar al siguiente estado mientras que su moneda no sea DOP"))

    def default_ex_rate(self):
        if not self.partner_id and not self.ex_rate:
            return self.env['wolftrak.tools'].default_ex_rate_2()


    @api.multi
    def action_payorder_cancel(self):
        if self.filtered(lambda inv: inv.state not in ['proforma2', 'draft', 'open', 'payorder']):
            raise UserError(_("Invoice must be in draft,Pro-forma or open state in order to be cancelled."))
        return self.action_cancel()

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
    state = fields.Selection([('draft', 'Draft'), ('payorder', 'Orden de Pago'),
                              ('proforma', 'Pro-forma'), ('proforma2', 'Pro-forma'),
                              ('open', 'Open'), ('open2', 'Abierto (Sin credito Fiscal)'),
                              ('paid', 'Paid'), ('cancel', 'Cancelled')],
                             string='Status', index=True, readonly=True, default='draft',
                             track_visibility='onchange', copy=False)
    ex_rate = fields.Float(string='Tasa de Cambio', digits=(1, 4),
                           default=lambda self: self.default_ex_rate())

    comment = fields.Text(string='Additional Information', readonly=False, states={'draft': [('readonly', False)]})

    date_invoice = fields.Date(string='Invoice Date', readonly=True,
        states={'draft': [('readonly', False)], 'payorder': [('readonly', False)]},
        index=True, help="Keep empty to use the current date", copy=False)

    date_due = fields.Date(string='Due Date', readonly=True, states={'draft': [('readonly', False)]}, required=True,
                           index=True, copy=False, help="If you use payment terms, the due date will be computed "
                           "automatically at the generation of accounting entries. The payment term may compute "
                           "several due dates, for example 50% now and 50% in one month, but if you want to force a "
                           "due date, make sure that the payment term is not set on the invoice. If you keep the "
                           "payment term and the due date empty, it means direct payment.")

    ncf_date = fields.Date(string='Fecha del Comprobante Fiscal', state={'paid': [('readonly', True)]})

    install_date = fields.Date(string='Fecha de Instalación', state={'paid': [('readony', True)]})

    @api.onchange('month')
    def _compute_draft_number(self):
        invoices = self.env['account.invoice'].search([], limit=1, order='id desc')
        last_id = invoices and max(invoices)
        date_str = str(date.today().year)+str(date.today().month)
        if not last_id.draft_number:
            self.draft_number = 'OP/'+date_str+'/1'
        else:
            inv_chain = self.env['account.invoice'].search([], order='id asc')
            i = 0
            for inv in inv_chain:
                number = int(inv.draft_number[9:])
                _logger.info(number)
                if number > i:
                    i = number
            self.draft_number = "OP/"+date_str+"/"+str(i+1)

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
        values_in_inv = self.env['wolftrak.tools'].get_ncf_record(self.ncf, supplier_rnc.doc_ident)
        values_out_inv = self.env['wolftrak.tools'].get_ncf_record(self.ncf, '131104371')
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

    @api.onchange('ncf')
    def ncf_db_validation(self):
        if self.search([('ncf', '=', self.ncf)]) and self.ncf:
            self.ncf = ''
            raise ValidationError(_("EL Número de Comprobante Fiscal ya se encuentra registrado en el Sistema\n "
                                    "Verifique nuevamente la información antes de proceder."))
        self.update_ncf_fields()

    def update_ncf_fields(self):
        if not self.ncf_date and self.ncf:
            self.ncf_date = fields.Datetime.now()
        if self.move_id and self.state not in ['draft', 'cancel']:
            self.move_id.write({
                'ncf': self.ncf,
                'ncf_date': self.ncf_date
            })


class WolftrakInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    now = datetime.datetime.now()
    description = fields.Char(string='Detalle',
                              default="Mes: " + calendar.month_name[date.today().month] + " " + str(now.year))


class WolftrakMove(models.Model):
    _inherit = "account.move"

    partner_id = fields.Many2one('res.partner', compute='_compute_partner_id', string="Partner", store=True)

    ncf = fields.Char(string="Número de Comprobante Fiscal")

    type_comp = fields.Char(string="Tipo de Comprobante", readonly=True, compute='ncf_validation')
    ncf_date = fields.Date(string="Fecha de Comprobante Fiscal")
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
        values_in_inv = self.env['wolftrak.tools'].get_ncf_record(self.ncf, supplier_rnc.doc_ident)
        # if values_in_inv != None:
        if values_in_inv is not None:
            self.type_comp = values_in_inv[1]
            self.ncf_result = "El Número de Comprobante Fiscal digitado es válido."
        else:
            self.ncf_result = "El Número de Comprobante Fiscal ingresado no es correcto o no corresponde a este RNC"

    @api.onchange('ncf')
    def ncf_date_update(self):
        inv_id = self.env['account.invoice'].search([('ncf', '=', self.ncf)])
        if len(inv_id) == 1:
            if inv_id.ncf_date:
                self.ncf_date = inv_id.ncf_date
            else:
                raise ValidationError(_('La factura poseedora de esté NCF no posee fecha de NCF, '
                                        'por favor verifique antes de continuar'))

    def sync_ncf_fields(self):
        inv_id = self.env['account.invoice'].search([('number', '=', self.name)])
        self.ncf_date = inv_id.ncf_date
        self.ncf = inv_id.ncf


class WolftrakPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def post(self):

        for rec in self:
            if rec.state != 'draft':
                raise UserError(
                    _("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)

            validation = False
            for inv in rec.invoice_ids:
                state = unicodedata.normalize('NFKD', inv.state).encode('ascii', 'ignore')
                if state != 'open' or state != 'open2':
                    validation = False
                else:
                    validation = True

            if validation:
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
            for inv in rec.invoice_ids:
                inv.write({'state': 'paid'})

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
                sequence_code)

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(
                    lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'posted', 'move_name': move.name})


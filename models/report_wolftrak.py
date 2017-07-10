import base64
import time
import logging
import urllib
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api
_logger = logging.getLogger(__name__)

class WolftrakReport607(models.Model):
    _name = 'wolftrakglobal.report607'

    @api.onchange('invoices')
    def total_calculated(self):
        total_inv = 0.0
        total_tax = 0.0
        for value in self.invoices:
            total_inv += value.amount_untaxed
            total_tax += value.amount_tax

        str_total_inv = str('%.2f'%total_inv)
        str_total_tax = str('%.2f'%total_tax)
        self.total_inv = ''.zfill(13)[len(str_total_inv[:str_total_inv.index('.')]):]+str_total_inv
        self.total_tax = ''.zfill(9)+str_total_tax

        regs = str(len(self.invoices))
        self.number_reg = ''.zfill(12)[len(regs):]+regs

    @api.onchange('to_607','invoices')
    def _set_period(self):
        month = str(self.to_607[5:7])
        year = str(self.to_607[:4])
        self.period = year + month

    @api.depends('from_607')
    def _set_from(self):
        year = str(self.from_607[:4])
        month = str(self.from_607[5:7])
        day = str(self.from_607[8:10])
        self.from_str = year + month + day

    @api.depends('to_607')
    def _set_to(self):
        year = str(self.to_607[:4])
        month = str(self.to_607[5:7])
        day = str(self.to_607[8:10])
        self.to_str = year + month + day

    from_607 = fields.Date('Desde', default=time.strftime('%Y-%m-01'))
    from_str = fields.Char(compute=_set_from)
    to_607 = fields.Date('Hasta', default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    to_str = fields.Char(compute=_set_to)
    total_inv = fields.Char(string='Total Calculado')
    total_tax = fields.Char(string='ITBIS Calculado')
    invoices = fields.Many2many('account.invoice', string='Facturas', domain=[('type', '=', 'out_invoice'),('state', '!=', 'draft')])
    period = fields.Char(string='Periodo')
    number_reg = fields.Char('Cantidad de registros')

    def to_wizard(self):

        view_ref = self.env['ir.model.data'].get_object_reference('wolftrakglobal', 'wizard_report607_view')
        view_id = view_ref[1] if view_ref else False

        if 'id' in self.env.context['params']:
            record_id = self.env.context['params']['id']
        else:
            record_id = self.id
        return {
            'name': 'Report 607',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.report607',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'report_id': record_id}
        }

class WizardReport607(models.Model):
    _name = 'wizard.report607'

    def _default_report(self):
        return self.env['wolftrakglobal.report607'].search([('id','=',self.env.context['report_id'])])

    reports = fields.Many2one('wolftrakglobal.report607', default=_default_report)

    def _default_report_result(self):

        rpt = self.env['wolftrakglobal.report607'].search([('id','=',self.env.context['report_id'])])
        line1 = "607  131104371"+str(rpt.period)+str(rpt.number_reg)+str(rpt.total_inv)+"\n"
        for inv in rpt.invoices:
            line2 = "  "+str(inv.partner_id.doc_ident)+str(inv.partner_id.doc_ident_type)+str(inv.ncf)
            date = str(inv.date)
            year = date[:date.index('-')]
            rest = date[date.index('-')+1:]
            date_result = year+rest[:rest.index('-')]+rest[rest.index('-')+1:]
            str_amount_tax = str('%.2f'%inv.amount_tax)
            str_amount_untaxed = str('%.2f'%inv.amount_untaxed)
            line2 += "                   "+str(date_result)
            line2 += "".zfill(9)[len(str_amount_tax[:str_amount_tax.index('.')]):]+str_amount_tax
            line2 += "".zfill(9)[len(str_amount_untaxed[:str_amount_untaxed.index('.')]):]+str_amount_untaxed+"\n"
            line1 += line2
        return line1

    report_result = fields.Text(string="Reporte", default=_default_report_result)

class WolftrakReport606(models.Model):
    _name = 'wolftrakglobal.report606'

    @api.onchange('to_606','moves')
    def _set_period(self):
        month = str(self.to_606[5:7])
        year = str(self.to_606[:4])
        self.period = year+month

    @api.depends('from_606','to_606')
    @api.onchange('from_606','to_606')
    def _set_dates(self):
        from_year = str(self.from_606[:4])
        from_month = str(self.from_606[5:7])
        from_day = str(self.from_606[8:10])
        self.form_str = from_year + from_month + from_day

        to_year = str(self.to_606[:4])
        to_month = str(self.to_606[5:7])
        to_day = str(self.to_606[8:10])
        self.to_str = to_year + to_month + to_day

    @api.onchange('moves')
    def total_calculated(self):
        total_inv = 0.0
        total_tax = 0.0
        total_tax_hold = 0.0
        for value in self.moves:
            for ln in value.line_ids:
                if ln.account_id.id == 82:
                    _logger.info(ln.debit)
                    tax = ln.debit
                    break
                else:
                    tax = 0.0
            total_tax += tax
            total_inv += value.amount - tax
            total_tax_hold += value.tax_hold

        str_total_inv = str('%.2f'%total_inv)
        str_total_tax = str('%.2f'%total_tax)
        str_total_tax_hold = str('%.2f'%total_tax_hold)
        self.total_inv = ''.zfill(13)[len(str_total_inv[:str_total_inv.index('.')]):]+str_total_inv
        self.total_tax = ''.zfill(9)[len(str_total_tax[:str_total_tax.index('.')]):]+str_total_tax
        self.total_tax_hold = ''.zfill(9)[len(str_total_tax_hold[:str_total_tax_hold.index('.')]):]+str_total_tax_hold
        regs = str(len(self.moves))
        self.number_reg = ''.zfill(12)[len(regs):]+regs

    # @api.onchange('tax_hold')
    # def _real_tax_hold(self):
    #     str_tax_hold = str('%.2f'%self.tax_hold)
    #     self.total_tax_hold = ''.zfill(9)[len(str_tax_hold[:str_tax_hold.index('.')]):]+str_tax_hold

    def _default_moves(self):
        return self.env['account.move'].search([('journal_id','=',2)])


    from_606 = fields.Date('Desde', default=time.strftime('%Y-%m-01'))
    from_str = fields.Char(compute=_set_dates)
    to_606 = fields.Date('Hasta', default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    to_str = fields.Char(compute=_set_dates)
    period = fields.Char(string='Periodo')
    number_reg = fields.Char('Cantidad de registros')
    total_tax_hold = fields.Char('ITBIS Retenido')
    total_tax = fields.Char('ITBIS Calculado')
    total_inv = fields.Char('Total Calculado')
    moves = fields.Many2many('account.move', string='Asientos', domain=[('journal_id','=',2)])

    def to_wizard(self):

        view_ref = self.env['ir.model.data'].get_object_reference('wolftrakglobal', 'wizard_report606_view')
        view_id = view_ref[1] if view_ref else False

        if 'id' in self.env.context['params']:
           record_id = self.env.context['params']['id']
        else:
            record_id = self.id
        return {
            'name' : 'Report 606',
            'view_type' : 'form',
            'view_mode' : 'form',
            'res_model' : 'wizard.report606',
            'view_id' : view_id,
            'type' : 'ir.actions.act_window',
            'target' : 'new',
            'context' : {'report_id' : record_id}
        }

class WizardReport606(models.Model):
    _name = 'wizard.report606'

    def _default_report(self):
        return self.env['wolftrakglobal.report606'].search([('id','=',self.env.context['report_id'])])

    def _default_report_result(self):
        _logger.info(self.env['wolftrakglobal.report606'].search([('id','=',self.env.context['report_id'])]))
        rpt = self.env['wolftrakglobal.report606'].search([('id','=',self.env.context['report_id'])])

        var1 = "606  131104371"+str(rpt.period)+str(rpt.number_reg)+str(rpt.total_inv)+str(rpt.total_tax_hold)+"\n"
        for move in rpt.moves:
            var1 += str(move.partner_id.doc_ident)+"  "+str(move.partner_id.doc_ident_type)+str(move.type_buy)+str(move.ncf)+"                   "
            date = str(move.date)
            year = date[:date.index('-')]
            rest = date[date.index('-')+1:]
            date_result = year+rest[:rest.index('-')]+rest[rest.index('-')+1:]

            tax = 0.0
            amount = 0.0
            for ln in move.line_ids:
                if ln.account_id.id == 82:
                    _logger.info(ln.debit)
                    tax += ln.debit
                    amount += 0.0
                    # break
                else:
                    amount += ln.debit
                    tax += 0.0

            str_tax = str('%.2f'%tax)
            str_tax_hold = str('%.2f'%move.tax_hold)
            str_amount = str('%.2f'%amount)
            str_rent_hold = str('%.2f'%move.rent_hold)
            var1 += date_result+date_result+''.zfill(9)[len(str_tax[:str_tax.index('.')]):]+str_tax # itbis factura y fechas
            var1 += ''.zfill(9)[len(str_tax_hold[:str_tax_hold.index('.')]):]+str_tax_hold # itbis retenido
            var1 += ''.zfill(9)[len(str_amount[:str_amount.index('.')]):]+str_amount # monto factura
            var1 += ''.zfill(9)[len(str_rent_hold[:str_rent_hold.index('.')]):]+str_rent_hold+'\n' # retencion renta

            # file = open("C:\Users\Jesus Rojas/test2.txt","r+")
            # file.write(var1)
            # # file.close()
            # _logger.info(file)
            # _logger.info(file.read())
            # self.binary_report = base64.encodestring(file)
        return var1

    reports = fields.Many2one('wolftrakglobal.report606', default=_default_report)
    report_result = fields.Text(string="Reporte", default=_default_report_result)
    binary_report = fields.Binary('Descargar')
    binary_string = fields.Char('Descargar')


    @api.multi
    def download_file(self):
        content_write = open("C:\Users\openpgsvc\DGII_F_606_131104371_yearmonth.txt", "w")
        content_write.write(self.report_result)
        content_write.close()
        content_read = open("C:\Users\openpgsvc\DGII_F_606_131104371_yearmonth.txt", "r")
        _logger.info(self.report_result)
        self.write({
            'binary_string': 'file.txt',
            'binary_report': base64.encodestring(content_read.read())
        })
        return {'type':'ir.actions.do_nothing'}

# result = self._default_report_result()
#
# return {
#     'type':'ir.action.act_url',
#     'url':'/web/binary/download_document?model=wizard.report.606&field=binary_report&id=%s&filename=test1.txt'%(self.id),
# }

# return self.write({'file_name':'test1.txt','binary_report':base64.encodestring(result)})

# self.write({'data': base64.encodestring(result)})
# this = self.browse()[0]
# _logger.info(this)
# _logger.info(self.inv.context)
# return {
#     'type' : 'ir.actions.act_window',
#     'res_model' : 'wizard.report606',
#     'view_mode' : 'form',
#     'view_type' : 'form',
#     'res_id' : this.id,
#     'views' : [(False,'form')],
#     'target' : 'new'
# }

# file = open("DGII_F_606_131104371_yearmonth.txt","w")
# file.write(result)
# file.close
# opener = urllib.URLopener
# opener.retrieve("http://localhost:8069/web/


class WolftrakPartnersWizard(models.TransientModel):
    _name = 'wizard.partner.report'

    def _default_lines(self):
        return self.env['partner.report'].search([])

    partner_report = fields.Many2many('partner.report', default=_default_lines)
    date_to = fields.Date(string='Desde')
    date_from = fields.Date(string='Hasta')

    def update_lines(self):

        sql = """delete from partner_report"""
        self.env.cr.execute(sql)

        invoices = self.env['account.invoice'].search([('date_invoice','>=',self.date_to),('date_invoice','<=',self.date_from)])

        partner_name = []
        amount_inv = []
        last_partner = False
        for inv in invoices:
            actual_partner = inv.partner_id.name
            if last_partner:
                partner_name.append(inv.partner_id.name)
            else:
                partner_name.append(last_partner)
                last_partner = actual_partner
        partner_names = dict.fromkeys(partner_name).keys()

        _logger.info(partner_names)

        partner_complete = []
        last_partner = False
        for name in partner_names:
            for inv in invoices:
                if inv.partner_id.name == name:
                    inv_lines = []
                    for line in inv.invoice_line_ids:
                        # inv_lines.append(line.price_unit,line.quantity,line.name)
                        inv_lines.append(line.price_unit)
                        inv_lines.append(line.quantity)
                        inv_lines.append(line.name)
                    partner_complete.append({inv.partner_id.name:[inv.amount_total,inv_lines,]})

        last_partner = False
        partner_dic = {}

        for partner in partner_complete:
            actual_partner = partner.keys()[0]
            if last_partner:
                if actual_partner != last_partner:
                    # _logger.info(partner[actual_partner][0])
                    partner_dic[actual_partner] = [partner[actual_partner][0]]
                    last_partner = actual_partner
                else:
                    partner_dic[actual_partner][0] = + partner[last_partner][0]

                    last_partner = actual_partner
            else:
                partner_dic[actual_partner] = [partner[actual_partner][0]]
                last_partner = actual_partner
                # _logger.info(partner_dic)

        sql = """insert into partner_report (partner_id, amount, devices, date_invoice) values
         (1,
         99,
         2,
         '02-05-2016')"""
        self.env.cr.execute(sql)

        view_ref = self.env['ir.model.data'].get_object_reference('wolftrakglobal', 'wizard_partner_report_form')
        view_id = view_ref[1] if view_ref else False

        return {
            'name' : 'Reporte Clientes Fijos',
            'view_type' : 'form',
            'view_mode' : 'form',
            'res_model' : 'wizard.partner.report',
            'view_id' : view_id,
            'type' : 'ir.actions.act_window',
            'target' : 'new'
        }

class WolftrakPartnersReport(models.Model):
    _name = 'partner.report'

    partner_id = fields.Char(string='Cliente')
    amount = fields.Float(string='Monto')
    devices = fields.Integer(string='Dispositivos')
    date_invoice = fields.Date(string='Fecha de la Factura')
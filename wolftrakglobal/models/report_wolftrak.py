import time
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api

class wolftrakglobal_report(models.Model):
    _name = 'wolftrakglobal.report607'

    @api.onchange('invoices')
    def total_calculated(self):
        total_inv = 0.0
        digit_inv = '0000000000000'
        total_tax = 0.0
        digit_reg = '000000000000'
        for value in self.invoices:
            total_inv += value.amount_untaxed
            total_tax += value.amount_tax

        str_total_inv = str('%.2f'%total_inv)
        self.total_inv = digit_inv[len(str_total_inv[:str_total_inv.index('.')]):]+str_total_inv
        self.total_tax = str('%.2f'%total_tax)

        regs = str(len(self.invoices))
        self.number_reg = digit_reg[len(regs):]+regs

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
    invoices = fields.Many2many('account.invoice', string='Facturas', domain=[('type', '=', 'out_invoice'),('state', '=', 'paid')])
    period = fields.Char(string='Periodo')
    number_reg = fields.Char('Cantidad de registros')


class wolftrakglobal_report_606(models.Model):
    _name = 'wolftrakglobal.report606'

    def _default_payment(self):
        return self.env['account.payment'].search(([])) # retorna una lista (importate)

    @api.onchange('to_606','invoices')
    def _set_period(self):
        month = str(self.to_606[5:7])
        year = str(self.to_606[:4])
        self.period = year+month

    @api.depends('from_606')
    def _set_from(self):
        year = str(self.from_606[:4])
        month = str(self.from_606[5:7])
        day = str(self.from_606[8:10])
        self.form_str = year + month + day

    @api.depends('to_606')
    def _set_to(self):
        year = str(self.to_606[:4])
        month = str(self.to_606[5:7])
        day = str(self.to_606[8:10])
        self.to_str = year+month+day

    @api.onchange('invoices')
    def total_calculated(self):
        total_inv = 0.0
        total_tax = 0.0
        total_tax_hold = 0.0
        digit_reg = '000000000000'
        for value in self.invoices:
            total_inv += value.amount_untaxed
            total_tax += value.amount_tax
            total_tax_hold += value.tax_hold

        self.total_inv = digit_reg+str('%.2f'%total_inv)
        self.total_tax = str('%.2f'%total_tax)
        self.total_tax_hold = str('%.2f'%total_tax_hold)

        regs = str(len(self.invoices))
        self.number_reg = digit_reg[len(regs):]+regs

    invoices = fields.Many2many('account.invoice', domain=[('type','=','in_invoice'),('state','=','paid')])

    payments = fields.Many2many('account.payment', default=_default_payment)
    date_payments = fields.Selection([('default','Default'),('x','y'),('z','aa')], string="Fecha Pagos")
    from_606 = fields.Date('Desde', default=time.strftime('%Y-%m-01'))
    from_str = fields.Char(compute=_set_from)
    to_606 = fields.Date('Hasta', default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    to_str = fields.Char(compute=_set_to)
    period = fields.Char(compute=_set_period, string='Periodo')
    number_reg = fields.Char('Cantidad de registros')
    total_tax_hold = fields.Char('ITBIS Retenido')
    total_tax = fields.Char('ITBIS Calculado')
    total_inv = fields.Char('Total Calculado')



# class wolftrakglobal_report_608(osv.osv):
# 	_name = 'wolftrakglobal.report608'
#
# 	_columns = {
# 		'invoices'	: fields.many2many('account.invoice', domain=[('type','=','out_refund'),('company_id','=',3)], string="Facturas"),
# 		'desde_608' : fields.date('Desde:'),
# 		'desde_str'	: fields.char(compute='_toma_desde'),
# 		'hasta_608' : fields.date('Hasta:'),
# 		'hasta_str'	: fields.char(compute='_toma_hasta'),
# 		'periodo'	: fields.char(compute='_toma_periodo', readonly=True, string='Periodo'),
# 		'cant_reg'	: fields.integer('Cantidad de registros')
# 	}
# 	_defaults = {
# 		'desde_608': lambda *a: time.strftime('%Y-%m-01'),
# 		'hasta_608': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
# 	}
#
# 	@api.onchange('invoices')
# 	def _toma_registro(self):
# 		for value in self.invoices:
# 			self.cant_reg = len(self.invoices)
#
# 	@api.depends('hasta_608')
# 	def _toma_periodo(self):
#
# 		month = str(self.hasta_608[5:7])
# 		year = str(self.hasta_608[:4])
# 		self.periodo = year+month
#
# 	@api.depends('desde_608')
# 	def _toma_desde(self):
#
# 		year = str(self.desde_608[:4])
# 		month = str(self.desde_608[5:7])
# 		day = str(self.desde_608[8:10])
# 		self.desde_str = year+month+day
#
# 	@api.depends('hasta_608')
# 	def _toma_hasta(self):
#
# 		year = str(self.hasta_608[:4])
# 		month = str(self.hasta_608[5:7])
# 		day = str(self.hasta_608[8:10])
# 		self.hasta_str = year+month+day


# class wolftrak_report_609(osv.osv):
# 	_name = 'wolftrakglobal.report609'
#
# 	_columns = {
# 		'invoices' : fields.many2many('account.invoice', domain=[('type','=','in_invoice'),('company_id','=',3)]),
# 		'desde_609' : fields.date('Desde:'),
# 		'desde_str'	: fields.char(compute='_toma_desde'),
# 		'hasta_609' : fields.date('Hasta:'),
# 		'hasta_str'	: fields.char(compute='_toma_hasta'),
# 		'periodo'	: fields.char(compute='_toma_periodo', readonly=True, string='Periodo'),
# 		'cant_reg'	: fields.integer('Cantidad de registros'),
# 		'total_inv'	: fields.float('Total monto facturado'),
# 		'total_isr' : fields.float('Total ISR Retenido')
# 	}
# 	_defaults = {
# 		'desde_609': lambda *a: time.strftime('%Y-%m-01'),
# 		'hasta_609': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
# 	}
#
# 	@api.onchange('invoices')
# 	def _toma_registro(self):
# 		for value in self.invoices:
# 			self.cant_reg = len(self.invoices)
#
# 	@api.depends('hasta_609')
# 	def _toma_periodo(self):
#
# 		month = str(self.hasta_609[5:7])
# 		year = str(self.hasta_609[:4])
# 		self.periodo = year+month
#
# 	@api.depends('desde_609')
# 	def _toma_desde(self):
#
# 		year = str(self.desde_609[:4])
# 		month = str(self.desde_609[5:7])
# 		day = str(self.desde_609[8:10])
# 		self.desde_str = year+month+day
#
# 	@api.depends('hasta_609')
# 	def _toma_hasta(self):
#
# 		year = str(self.hasta_609[:4])
# 		month = str(self.hasta_609[5:7])
# 		day = str(self.hasta_609[8:10])
# 		self.hasta_str = year+month+day
#
# 	@api.onchange('invoices')
# 	def total_calculado(self):
# 		self.total_inv = 0.0
# 		self.total_isr = 0.0
# 		for value in self.invoices:
# 			self.total_inv += value.amount_total
# 			self.total_isr += value.isr_hold
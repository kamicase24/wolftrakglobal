import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import models, fields, api
from openerp.osv import fields, osv
from openerp.osv import orm
from openerp.tools.translate import _


class wolftrakglobal_report(osv.osv):
	_name = 'wolftrakglobal.report607'

	_columns = {
		'desde_607' : fields.date('Desde:'),
		'desde_str'	: fields.char(compute='_toma_desde'),
		'hasta_607' : fields.date('Hasta:'),
		'hasta_str'	: fields.char(compute='_toma_hasta'),
		'total_cld'	: fields.float('Total Calculado: '),
		'total_tax'	: fields.float('ITBIS Calculado: '),
		'reporte'	: fields.many2many('account.invoice', 'name', 'amount_untaxed', 'amount_tax', string='Entradas: ', domain=[('type', '=', 'out_invoice'),('state', '!=', 'draft')]),
		'periodo'	: fields.char(compute='_toma_periodo', string='Periodo', readonly=True),
		'cant_reg'	: fields.integer('Cantidad de registros')
	}
	_defaults = {
		'desde_607': lambda *a: time.strftime('%Y-%m-01'),
		'hasta_607': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
	}

	@api.onchange('reporte')
	def total_calculado(self):
		self.total_cld = 0.0
		self.total_tax = 0.0
		for value in self.reporte:
			self.total_cld += value.amount_untaxed
			self.total_tax += value.amount_tax
		self.cant_reg = len(self.reporte)

	@api.depends('hasta_607')
	def _toma_periodo(self):

		month = str(self.hasta_607[5:7])
		year = str(self.hasta_607[:4])
		self.periodo = year+month

	@api.depends('desde_607')
	def _toma_desde(self):

		year = str(self.desde_607[:4])
		month = str(self.desde_607[5:7])
		day = str(self.desde_607[8:10])
		self.desde_str = year+month+day

	@api.depends('hasta_607')
	def _toma_hasta(self):

		year = str(self.hasta_607[:4])
		month = str(self.hasta_607[5:7])
		day = str(self.hasta_607[8:10])
		self.hasta_str = year+month+day

class wolftrakglobal_report_606(osv.osv):
	_name = 'wolftrakglobal.report606'

	def _toma_default_pagos(self, cr, uid, context=None):
		return self.pool.get('account.payment').search(cr, uid, []) # retorna una lista (importate)

	_columns = {
		'invoices'  	: fields.many2many('account.invoice', domain=[('type', '=', 'in_invoice'),('state', '!=', 'draft')]),
		'payments'		: fields.many2many('account.payment'),
		'dt_payments'	: fields.selection([('default','Default'),('x','y'),('z','aa')], string="Fecha Pagos"),
		'desde_606' 	: fields.date('Desde:'),
		'desde_str'		: fields.char(compute='_toma_desde'),
		'hasta_606' 	: fields.date('Hasta:'),
		'hasta_str'		: fields.char(compute='_toma_hasta'),
		'periodo'		: fields.char(compute='_toma_periodo', string='Periodo', readonly=True),
		'cant_reg'		: fields.integer('Cantidad de registros'),
		'total_rtn'		: fields.float('ITBIS Retenido: '),
		'total_cld'		: fields.float('Total Calculado: '),
		'total_tax'		: fields.float('ITBIS Calculado: ')
	}
	_defaults = {
		'desde_606': lambda *a: time.strftime('%Y-%m-01'),
		'hasta_606': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
		'payments'  : _toma_default_pagos
	}

	@api.depends('hasta_606')
	def _toma_periodo(self):

		month = str(self.hasta_606[5:7])
		year = str(self.hasta_606[:4])
		self.periodo = year+month

	@api.depends('desde_606')
	def _toma_desde(self):

		year = str(self.desde_606[:4])
		month = str(self.desde_606[5:7])
		day = str(self.desde_606[8:10])
		self.desde_str = year+month+day

	@api.depends('hasta_606')
	def _toma_hasta(self):

		year = str(self.hasta_606[:4])
		month = str(self.hasta_606[5:7])
		day = str(self.hasta_606[8:10])
		self.hasta_str = year+month+day

	@api.onchange('invoices')
	def total_calculado(self):
		self.total_cld = 0.0
		self.total_tax = 0.0
		self.total_rtn = 0.0
		for value in self.invoices:
			self.total_cld += value.amount_untaxed
			self.total_tax += value.amount_tax
			self.total_rtn += float(value.tax_hold)
			self.cant_reg = len(self.invoices)


class wolftrakglobal_report_608(osv.osv):
	_name = 'wolftrakglobal.report608'

	_columns = {
		'invoices'	: fields.many2many('account.invoice', domain=[('type','=','out_refund')], string="Facturas"),
		'desde_608' : fields.date('Desde:'),
		'desde_str'	: fields.char(compute='_toma_desde'),
		'hasta_608' : fields.date('Hasta:'),
		'hasta_str'	: fields.char(compute='_toma_hasta'),
		'periodo'	: fields.char(compute='_toma_periodo', readonly=True, string='Periodo'),
		'cant_reg'	: fields.integer('Cantidad de registros')
	}
	_defaults = {
		'desde_608': lambda *a: time.strftime('%Y-%m-01'),
		'hasta_608': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
	}

	@api.onchange('invoices')
	def _toma_registro(self):
		for value in self.invoices:
			self.cant_reg = len(self.invoices)

	@api.depends('hasta_608')
	def _toma_periodo(self):

		month = str(self.hasta_608[5:7])
		year = str(self.hasta_608[:4])
		self.periodo = year+month

	@api.depends('hasta_608')
	def _toma_periodo(self):

		month = str(self.hasta_608[5:7])
		year = str(self.hasta_608[:4])
		self.periodo = year+month

	@api.depends('desde_608')
	def _toma_desde(self):

		year = str(self.desde_608[:4])
		month = str(self.desde_608[5:7])
		day = str(self.desde_608[8:10])
		self.desde_str = year+month+day

	@api.depends('hasta_608')
	def _toma_hasta(self):

		year = str(self.hasta_608[:4])
		month = str(self.hasta_608[5:7])
		day = str(self.hasta_608[8:10])
		self.hasta_str = year+month+day


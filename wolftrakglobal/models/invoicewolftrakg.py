# -*- coding: utf-8 -*-
from openerp import models, fields #importa los objetos models y fields de el Core de Odoo
from openerp.osv import orm
from openerp import models, fields, api

class wolftraknew(orm.Model): #declara un nuevo modelo. Deriva de models.Model
	#define el atributo _nombre, identificador que sera usado por Odoo para referises a este modelo 
	_name = 'account.invoice'
	_inherit = 'account.invoice'

	ncf = fields.Char(string="Numero de Comprobante Fiscal")
	tax_hold = fields.Monetary(string="ITBIS Retenido")
	type_ci = fields.Char(string="Tipo de Id")
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
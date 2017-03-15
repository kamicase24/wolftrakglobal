# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil import relativedelta
from odoo import api, fields, models, tools

class WolftrakPayrollReport(models.Model):
    _name = 'hr.payroll.report'
    _description = 'Payroll biweekly report'

    @api.depends('date_from','date_to')
    def _get_payslips(self):
        payslips = self.env['hr.payslip']
        self.payslip_id = payslips.search([('date_from','=',self.date_from),('date_to','=',self.date_to)])

    @api.depends('date_from','date_to','payslip_id')
    def _get_employees(self):
        employess = self.env['hr.employee']
        payslip = self.payslip_id
        for ps in payslip:
            self.employee_id += employess.search([('id','=',ps.employee_id.id)])

    @api.depends('date_from','date_to','payslip_id')
    def _get_payslip_lines(self):
        all_ps_lines = self.env['hr.payslip.line']
        payslips = self.payslip_id
        for ps in payslips:
            self.payslip_lines += all_ps_lines.search([('slip_id','=',ps.id)])

    @api.depends('date_from','date_to')
    def _set_name(self):
        self.name = ""+str(self.date_from)+"/"+str(self.date_to)

    name = fields.Char(string="Quincena", readonly=True, compute=_set_name)
    date_from = fields.Date(string="Desde", default=time.strftime('%Y-%m-01'))
    date_to = fields.Date(string="Hasta", default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])

    employee_id = fields.Many2many('hr.employee', string='Empleado', compute=_get_employees)
    payslip_id = fields.Many2many('hr.payslip', string='Nómina', compute=_get_payslips)
    payslip_lines = fields.Many2many('hr.payslip.line', string='Lineas de Nómina', compute=_get_payslip_lines)

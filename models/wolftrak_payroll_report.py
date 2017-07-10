# -*- coding: utf-8 -*-
import time
import logging
from datetime import datetime

from dateutil import relativedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
_logger = logging.getLogger(__name__)

class WolftrakPayrollReport(models.Model):
    _name = 'hr.payroll.report'
    _description = 'Payroll biweekly report'

    def _default_employees(self):
        return self.env['hr.employee'].search([('id','!=',1)])

    date_from = fields.Date(string="Desde", default=time.strftime('%Y-%m-01'))
    date_to = fields.Date(string="Hasta", default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    name = fields.Char(string="Quincena", readonly=True)
    employee_id = fields.Many2many('hr.employee', string='Empleados', domain=[('id','!=',1)], default=_default_employees)
    payslip_id = fields.Many2many('hr.payslip', string='Nómina')
    payslip_lines = fields.Many2many('hr.payslip.line', string='Lineas de Nómina')

    def load_payslip(self):
        _logger.info('load_payslips')
        _logger.info(type(self.date_from))
        _logger.info(self.date_from)
        paylips = self.env['hr.payslip'].search([('date_from','=',self.date_from),('date_to','=',self.date_to)])
        if len(paylips) > 0: self.payslip_id = paylips
        else: raise UserError(_("Las fechas seleccionadas no coinciden con ninguna Nómina"))

    def _set_report(self):

        sql = 'delete from hr_payroll_report_list'
        self.env.cr.execute(sql)

        for emp in self.employee_id:
            ps_id = ''
            for ps in self.payslip_id:
                if ps.employee_id.id == emp.id:
                    ps_id = ps.id
                    _logger.info(ps_id)
            sql = '''INSERT INTO hr_payroll_report_list
                  (emp_name,
                  emp_ident_doc,
                  emp_charge,
                  basic_wage,
                  daily_wage,
                  hour_value,
                  worked_days,
                  worked_days_total,
                  no_worked_days,
                  no_worked_days_total,
                  d_ext_hrs,
                  n_ext_hrs,
                  total_d_ext_hrs,
                  total_n_ext_hrs,
                  holydays_sundays,
                  total_hds_sds,
                  bonus_days,
                  subtotal_asg,
                  tax1,
                  unpaid_hours,
                  total_unpaid_hours,
                  tax2,
                  loan,
                  tax3,
                  tax4,
                  subtotal_dec,
                  net)
                  
                  SELECT
                  emp.name_related,
                  emp.identification_id,
                  (SELECT name FROM hr_job WHERE id = emp.job_id),
                  (SELECT wage FROM hr_contract WHERE id = ps.contract_id),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'SD'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'VHT'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'DLQ'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'SB'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'DD'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'TDD'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'HED'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'HEN'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'THED'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'THEN'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'DFL'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'TDFL'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'BDB'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'SubAsg'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'IVSS'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'HNR'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'THNR'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'PF'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'PRE'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'OD'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'LPH'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'SubDed'),
                  (SELECT amount FROM hr_payslip_line WHERE slip_id = ps.id AND code = 'NET')
                  
                  FROM hr_employee emp, hr_payslip ps 
                  WHERE emp.id = %s AND ps.id = %s''' % (emp.id, ps_id)
            _logger.info(sql)
            self.env.cr.execute(sql)

    def open_report(self):

        self._set_report()

        view_ref = self.env['ir.model.data'].get_object_reference('wolftrakglobal','hr_payroll_report_view')
        view_id = view_ref[1] if view_ref else False

        return {
            'name':'Hr payroll Report',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'hr.payroll.report.wizard',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'target':'new'
        }

class WolftrakPayrollReportWizard(models.TransientModel):
    _name = 'hr.payroll.report.wizard'

    def _default(self):
        return self.env['hr.payroll.report.list'].search([])
    report_list_id = fields.Many2many('hr.payroll.report.list', default=_default)

    # @api.multi
    # def print_report(self):
    #
    #     datas = {
    #         'ids' : self.ids,
    #         'model' : 'hr.payroll.report.list',
    #         'form' : self.read()[0]
    #     }
    #     _logger.info('DATAS!')
    #     _logger.info(datas)
    #
    #     x = {
    #         'type' : 'ir.action.report.xml',
    #         'report_name' : 'template_report_payroll_list',
    #         'datas' : datas
    #     }
    #     _logger.info('SELF')
    #     _logger.info(self)
    #     _logger.info('READ!')
    #     _logger.info(self.read)
    #     _logger.info('RESULT!')
    #     _logger.info(x)
    #     return x

class WolftrakPayrollList(models.Model):
    _name = 'hr.payroll.report.list'

    emp_name = fields.Char(string='Nombre')
    emp_ident_doc = fields.Char(string='C.I')
    emp_charge = fields.Char(string='Cargo')
    basic_wage = fields.Char(string='Sueldo base')
    daily_wage = fields.Char(string='Sueldo diario')
    hour_value = fields.Char(string='Valor hora')
    worked_days = fields.Char(string='Días Trabajados')
    worked_days_total = fields.Char(string='Total Días Trab.')
    no_worked_days = fields.Char(string='Días Descanso')
    no_worked_days_total = fields.Char(string='Total Días Desc.')
    d_ext_hrs = fields.Char(string="Horas Ext. Diur.")
    n_ext_hrs = fields.Char(string="Horas Ext. Noc.")
    total_d_ext_hrs = fields.Char(string="Total Horas Diur.")
    total_n_ext_hrs = fields.Char(string="Total Horas Noc.")
    holydays_sundays = fields.Char(string="Domingos y Feriados")
    total_hds_sds = fields.Char(string="Total por Dom. y Feriados")
    bonus_days = fields.Char(string="Bono Día de Beneficio")
    subtotal_asg = fields.Char(string="SubTotal de Asignaciones")

    tax1 = fields.Char(string="IVSS")
    unpaid_hours = fields.Char(string="Horas no Remuneradas")
    total_unpaid_hours = fields.Char(string="Total Hrs. no Remuneradas")
    tax2 = fields.Char(string="Paro Forzoso")
    loan = fields.Char(string="Prestamo")
    tax3 = fields.Char(string="Deduc. Atrasadas")
    tax4 = fields.Char(string="Ley de Politica Hab.")
    subtotal_dec = fields.Char(string="Subtotal Deducciones")
    net = fields.Char(string="Total")





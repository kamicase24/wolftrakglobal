# -*- coding: utf-8 -*-
from odoo import api, fields, models
import time
from datetime import datetime, date
import calendar
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class AutoTimesheet(models.Model):
    _name = "hr.auto.timesheet"

    employee_id = fields.Many2one('hr.employee', string="Empleado", required=True)
    user_id = fields.Many2one('res.users', related='employee_id.user_id', string="Usuario", store=True)
    date_to = fields.Date(string="Desde")
    date_from = fields.Date(string="Hasta")
    department_id = fields.Many2one('hr.department')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id
            self.user_id = self.employee_id.user_id


class HrTimesheetSheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"

    def auto_timesheet_1(self):
        self.date_from = time.strftime('%Y-%m-01')
        self.date_to = time.strftime('%Y-%m-15')

        project = self.env['project.project'].search([('user_id','=',self.user_id.id)])
        _logger.info("...")
        _logger.info(project)
        _logger.info("...")

    def auto_timesheet_2(self):
        final_month = calendar.monthrange(date.today().year, date.today().month)[1]
        self.date_from = time.strftime('%Y-%m-16')
        self.date_to = time.strftime('%Y-%m-'+str(final_month)+"'")
# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2014 Odoo Canada. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.getnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm
from openerp.tools.translate import _
import datetime
from datetime import date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from calendar import monthrange
import math

class hr_payslip(orm.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    def timesheet_mapping(
        self, cr, uid,
        timesheet_sheets,
        payslip,
        date_from,
        date_to,
        date_format,
        context=None,
    ):
        """This function takes timesheet objects imported from the timesheet
        module and creates a dict of worked days to be created in the payslip.
        """
        worked_days = []
        worked_days.append({}) # 0 Lunes del mes
        worked_days.append({}) # 1 Tiempo no Remunerado
        worked_days.append({}) # 2 Dias del mes
        worked_days.append({}) # 3 Dias de descanso
        worked_days.append({}) # 4 Domingos y Feriados Lab.
        worked_days.append({}) # 5 Total de la parte de tiempo
        worked_days.append({}) # 6 Dia de beneficio
        worked_days.append({}) # 7 Permisos de previo aviso

        # Create one worked days record for each timesheet sheet
        for ts_sheet in timesheet_sheets:

            # Get formated date from the timesheet sheet
            date_from = datetime.datetime.strptime(
                ts_sheet.date_from,
                DEFAULT_SERVER_DATE_FORMAT
            ).strftime(date_format)

            # Create a worked days record with no time
            # worked_days[0][ts_sheet.id] = {
            #     'name': _('Total servicio %s') % date_from,
            #     'number_of_hours': 0,
            #     'contract_id': payslip.contract_id.id,
            #     'code': 'TS',
            #     'imported_from_timesheet': True,
            # }
            # for ts in ts_sheet.timesheet_ids:
            #     # The timesheet_sheet overlaps the payslip period,
            #     # but this does not mean that every timesheet in it
            #     # overlaps the payslip period.
            #     if date_from <= ts.date <= date_to:
            #         worked_days[0][ts_sheet.id][
            #             'number_of_hours'
            #         ] += ts.unit_amount
            #     unit_amount = ts.unit_amount #Total de las partes de tiempo
            #     total_att = ts_sheet.total_attendance #Total del servicio

            # worked_days[0][ts_sheet.id]['number_of_hours'] = ts_sheet.total_attendance
            # worked_days[0][ts_sheet.id]['number_of_days'] = math.ceil(ts_sheet.total_attendance/unit_amount)

            # Diferencia de tiempo
            fulldate = datetime.datetime.now()
            monthdate = fulldate.month
            yeardate = fulldate.year

            finaldaymonth = monthrange(yeardate, monthdate)[1]
            i = 1
            j = True
            monday = 0
            while j:
                if datetime.date(yeardate, monthdate, i).weekday() == 0:
                    monday += 1
                if i == finaldaymonth:
                    j = False
                else:
                    i = i+1

            worked_days[0][ts_sheet.id] = {
                'name': _('Lunes del mes'),
                'number_of_days': monday,
                'contract_id': payslip.contract_id.id,
                'code': 'CLM',
                'imported_from_timesheet': True,
            }

            # Diferencia de tiempo
            worked_days[1][ts_sheet.id] = {
                'name': _('Diferencia'),
                'number_of_hours': ts_sheet.total_difference,
                'contract_id': payslip.contract_id.id,
                'code': 'DE',
                'imported_from_timesheet': True,
            }

            # Dias del mes
            actual = datetime.datetime.now()
            month = monthrange(actual.year, actual.month)[1]

            worked_days[2][ts_sheet.id] = {
                'name': _('Dias del mes'),
                'number_of_days': month,
                'contract_id': payslip.contract_id.id,
                'code': 'DM',
                'imported_from_timesheet': True,
            }

            # Dias de descanso AAAA/MM/DD
            final_mes = date_to[8:10]
            if final_mes > 15:
                DD = int(final_mes) - 15
            else:   
                DD = 15                

            worked_days[3][ts_sheet.id] = {
                'name': _('Dias de descanso'),
                'number_of_hours': 0,
                'number_of_days': DD,
                'contract_id': payslip.contract_id.id,
                'code': 'DD',
                'imported_from_timesheet': True,
            }

            worked_days[4][ts_sheet.id] = {
                'name': _('Domingos y feriados laborados'),
                'number_of_hours': 0,
                'number_of_days': 0,
                'contract_id': payslip.contract_id.id,
                'code': 'DF',
                'imported_from_timesheet': True,
            }

            worked_days[5][ts_sheet.id] = {
                'name': _('Total en horas'),
                'number_of_hours': ts_sheet.total_timesheet,
                'contract_id': payslip.contract_id.id,
                'code': 'TH',
                'imported_from_timesheet': True,
            }

            worked_days[6][ts_sheet.id] = {
                'name': _('Horas extras nocturnas'),
                'number_of_hours': 0,
                'contract_id': payslip.contract_id.id,
                'code': 'HED',
                'imported_from_timesheet': True,
            }

            # Dia de Beneficio
            final_mes = date_to[8:10]
            if final_mes >= 15:
                DB = 1
            else:
                DB = 2

            worked_days[7][ts_sheet.id] = {
                'name': _('Dia de Beneficio'),
                'number_of_days': DB,
                'contract_id': payslip.contract_id.id,
                'code': 'DB',
                'imported_from_timesheet': True,
            }


        return worked_days

    def import_worked_days(
        self, cr, uid,
        payslip_id,
        context=None
    ):
        """This method retreives the employee's timesheets for a payslip period
        and creates worked days records from the imported timesheets
        """
        payslip = self.browse(cr, uid, payslip_id, context=context)[0]
        employee = payslip.employee_id

        date_from = payslip.date_from
        date_to = payslip.date_to

        # get user date format
        lang_pool = self.pool['res.lang']
        user_pool = self.pool['res.users']
        code = user_pool.context_get(cr, uid).get('lang', 'en_US')
        lang_id = lang_pool.search(
            cr, uid,
            [('code', '=', code)],
            context=context
        )
        date_format = lang_pool.read(
            cr, uid,
            lang_id,
            ['date_format'],
            context=context
        )[0]['date_format']

        # Delete old imported worked_days
        # The reason to delete these records is that the user may make
        # corrections to his timesheets and then reimport these.
        old_worked_days_ids = [
            wd.id for wd in payslip.worked_days_line_ids
            # We only remove records that were imported from
            # timesheets and not those manually entered.
            if wd.imported_from_timesheet
        ]
        self.pool.get(
            'hr.payslip.worked_days'
        ).unlink(cr, uid, old_worked_days_ids, context)

        # get timesheet sheets of employee
        timesheet_sheets = [
            ts_sheet for ts_sheet in employee.timesheet_sheet_ids
            if (
                # We need only the timesheet sheets that overlap
                # the payslip period.
                date_from <= ts_sheet.date_from <= date_to or
                date_from <= ts_sheet.date_to <= date_to
            )
            # We want only approved timesheets
            and ts_sheet.state == 'done'
        ]
        if not timesheet_sheets:
            raise orm.except_orm(
                _("Warning"),
                _("""\
Sorry, but there is no approved Timesheets for the entire Payslip period"""),
            )

        # The reason to call this method is for other modules to modify it.
        worked_days = self.timesheet_mapping(
            cr, uid,
            timesheet_sheets,
            payslip,
            date_from,
            date_to,
            date_format,
            context=context,
        )
        
        # Lunes del mes
        worked_daysA = [(0, 0, wd) for key, wd in worked_days[0].items()]

        self.write(
            cr, uid, payslip_id,
            {'worked_days_line_ids': worked_daysA},
            context=context
        )

        #Tiempo no remunerado
        worked_daysD = [(0, 0, wd) for key, wd in worked_days[1].items()]

        self.write(
            cr, uid, payslip_id,
            {'worked_days_line_ids': worked_daysD},
            context=context
        )
        #Dias del actual mes
        worked_daysM = [(0, 0, wd) for key, wd in worked_days[2].items()]

        self.write(
            cr, uid, payslip_id,
            {'worked_days_line_ids': worked_daysM},
            context=context
        )
        #Dias de Descanso
        worked_daysF = [(0, 0, wd) for key, wd in worked_days[3].items()]

        self.write(
            cr, uid, payslip_id,
            {'worked_days_line_ids': worked_daysF},
            context=context
        )
        #Domingos y feriados laborados
        worked_daysL = [(0, 0, wd) for key, wd in worked_days[4].items()]

        self.write(
            cr, uid, payslip_id,
            {'worked_days_line_ids': worked_daysL},
            context=context
        )  
        #Total de la partes de tiempo
        worked_daysPT = [(0, 0, wd) for key, wd in worked_days[5].items()]

        self.write(
            cr, uid, payslip_id,
            {'worked_days_line_ids': worked_daysPT},
            context=context
        ) 
        #Permiso Previo Aviso
        worked_daysPPA = [(0, 0, wd) for key, wd in worked_days[6].items()]

        self.write(
            cr, uid, payslip_id,
            {'worked_days_line_ids': worked_daysPPA},
            context=context
        )
        #Dia Beneficio
        worked_daysDB = [(0, 0, wd) for key, wd in worked_days[7].items()]

        self.write(
            cr, uid, payslip_id,
            {'worked_days_line_ids': worked_daysDB},
            context=context
        )              

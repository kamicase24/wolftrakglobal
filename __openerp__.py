{
    'name': "WolftrakGlobal",

    'description': """
        Modulo Personalizado para WolftrakGlobal c.a 2016""",
    'summary': """
        Modulo Personalizado para WolftrakGlobal c.a 2016""",
    'author': "Jesus Rojas",
    'website': "http://www.wolftrakglobal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/   blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'hr_payroll', 'gamification'],
    # always loaded
    'data': [
        # secutiry
        'security/ir.model.access.csv',
        # reports
        # 'report/wolftrak_report_footer.xml', dejar comentado 4 ever
        'report/wolftrak_report_606.xml',
        'report/wolftrak_report_607.xml',
        'report/wolftrak_report_cesta_ticket.xml',  # cesta ticket
        'report/wolftrak_report_act_det.xml',
        'report/wolftrak_report_statement.xml',  # estado de cuenta
        'report/wolftrak_report_payslip.xml',  # nomina
        'report/wolftrak_report_header.xml',  # header
        'report/wolftrak_report_invoice.xml',  # factura
        'report/wolftrak_report_saleorder.xml',  # presupuesto
        'report/wolftrak_report_daily_journal.xml',
        'report/wolftrak_report_gps_device.xml',  # dispositivos gps
        'report/wolftrak_report_partners.xml',  # reporte dispositivos mensuales (cliente)
        'report/wolftrak_report_debt_clients.xml',  # Clientes Morosos
        # views
        'views/606_wolftrak.xml',
        'views/607_wolftrak.xml',
        'views/hr_payroll_wolftrak.xml',
        'views/gamification_badge_wolftrak.xml',
        'views/res_partner_wolftrak.xml',
        'views/account_wolftrak.xml',
        'views/sale_order_wolftrak.xml',
        'views/crm_lead_wolftrak.xml',
        'views/act_det_wolftrak.xml',
        'views/daily_journal_wolftrak.xml',
        # 'views/wolftrak_move_report.xml',
        # 'views/wolftrak_move_views.xml',
        # 'views/hr_timesheet_wolftrak.xml',
        'views/layouts.xml',
        'views/maintenance_wolftrak.xml',
        'views/custom_reports_wolftrak.xml',
        'views/product_wolftrak.xml',
        'views/purchase_wolftrak.xml',
        'views/example_webpage.xml',
        # data
        'data/base_action_wolftrak.xml',
        # wizards
        'wizard/crm_activity_log_wolftrak.xml',
        'wizard/grant_badge_wolftrak.xml'
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
# -*- coding: utf-8 -*-

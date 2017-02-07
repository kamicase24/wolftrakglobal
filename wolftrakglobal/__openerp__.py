{
    'name': "WolftrakGlobal",

    'description': """
        Modulo Personalizado para WolftrakGlobal c.a 2016""",
    'summary': """
        Modulo Personalizado para WolftrakGlobal c.a 2016""",
    'author': "Jesus Rojas",
    'website': "http://www.wolftrakglobal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','hr_payroll','gamification'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/607.xml',
        # 'views/607_view.xml',
        # 'views/606_view.xml',
        # 'views/606.xml',
        # 'views/608_view.xml',
        # 'views/608.xml',
        # 'views/609_view.xml',
        # 'views/609.xml',
        # reports
        # 'report/wolfttrak_report_payroll.xml',
        # 'report/wolftrak_report_footer.xml', dejar comentado 4 ever
        # 'report/wolftrak_report_overdue.xml', # pagos pendientes / estado de cuenta temporal
        'report/wolftrak_report_header.xml',
        'report/wolftrak_report_invoice.xml', # factura
        'report/wolftrak_report_saleorder.xml', # presupuesto
        # views
        'views/gamification_badge_wolftrak.xml',
        'views/res_partner_wolftrak.xml',
        'views/invoice_wolftrak.xml',
        'views/sale_order_wolftrak.xml',
        'views/crm_lead_wolftrak.xml',
        # 'views/wolftrak_move_report.xml',
        # 'views/wolftrak_move_views.xml',
        # 'views/wolftrak_act_det_view.xml',
        # 'views/wolftrak_cesta_ticket.xml',
        # 'views/wolftrak_act_det_report.xml',
        'views/layouts.xml',
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

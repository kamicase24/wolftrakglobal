# -*- coding: utf-8 -*-
{
    'name': "WolftrakGlobal",

    'description': """
        Modulo Personalizado para WolftrakGlobal c.a 2016""",
    'summary': """
        Modulo Personalizado para WolftrakGlobal c.a 2016""",
    'author': "WolftrakGlobal",
    'website': "http://www.wolftrakglobal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','hr_payroll'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/nominawolf.xml',
        'views/templates.xml',
        'views/layouts.xml',
        'views/factura.xml',
        'views/headerwolftrakglobal.xml',
        #'views/footerwolftrakglobal.xml',
        'views/badge_wolftrak.xml',
        'views/userswolftrak.xml',
        'views/invoicewolftrakg.xml',
        'views/pagwolftrak.xml',
        'views/custom_sale_order.xml',
        'views/presupuesto.xml',
        'views/custom_overdue.xml',
        'views/607.xml',
        'views/607_view.xml',
        'views/606_view.xml',
        'views/606.xml',
        'views/608_view.xml',
        'views/608.xml',
        'views/609_view.xml',
        'views/609.xml',
        'views/wolftrak_move_report.xml',
        'views/wolftrak_move_views.xml',
        'views/wolftrak_act_det_view.xml',
        'views/wolftrak_cesta_ticket.xml',
        'views/wolftrak_act_det_report.xml',
        'views/wolftrak_crm_lead.xml',
        'views/wolftrak_res_partner.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}

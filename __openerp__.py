# -*- coding: utf-8 -*-
{
    'name': "WolftrakGlobal",

    'description': """
        Modulo Personalizado para WolftrakGlobal c.a 2016
    """,
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
    'depends': ['base','account'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/nominawolf.xml',
        'views/templates.xml',
        'views/layouts.xml',
        'views/factura.xml',
        'views/headerwolftrakglobal.xml',
        'views/footerwolftrakglobal.xml',
        'views/menubar.xml',
        #'views/userswolftrak.xml',
        #'views/invoicewolftrakg.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}
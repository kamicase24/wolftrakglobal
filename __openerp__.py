# -*- coding: utf-8 -*-
{
    'name': "WolftrakGlobal",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "WolftrakGlobal",
    'website': "http://www.wolftrakglobal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/nominawolf.xml',
        'views/templates.xml',
        'views/layouts.xml',
        'views/factura.xml',
        'views/headerwolftrakglobal.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}
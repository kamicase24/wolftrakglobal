# -*- coding: utf-8 -*-
{
    'name': "WolftrakGlobal",

    'description': """
  def next_weekday(d, weekday):
#     days_ahead = weekday - d.weekday()
#     if days_ahead <= 0: # Target day already happened this week
#         days_ahead += 7
#     return d + datetime.timedelta(days_ahead)

# d = datetime.datetime.today()
# next_monday = next_weekday(d, 0) # 0 = Monday, 1=Tuesday, 2=Wednesday...
# print(next_monday)      Modulo Personalizado para WolftrakGlobal c.a 2016
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
        #'views/menubar.xml',
        'views/userswolftrak.xml',
        'views/invoicewolftrakg.xml',
        #'views/pagwolftrak.xml',
        'views/custom_sale_order.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}

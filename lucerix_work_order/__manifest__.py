# -*- coding: utf-8 -*-
{
    'name': "Lucerix Work Order",
    'summary': """
        Work Order Pause and start option
    """,
    'description': """
        Work Order Pause and start option
    """,
    'author': "Syncoria",
    'website': "http://www.syncoria.com",
    'category': 'MRP',
    'version': '0.1',
    'depends': ['base', 'mrp', 'mrp_workorder'],

    'data': [
        'security/ir.model.access.csv',
        'views/timeline_codes_view.xml',
        'views/mrp_workorder_view.xml',
        'wizard/additional_pause_reason_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

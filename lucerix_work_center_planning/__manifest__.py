# -*- coding: utf-8 -*-
{
    'name': "Lucerix Work Center Capacity Planning",
    'summary': """
        Work Center Capacity Planning
    """,
    'description': """
        Work Center Capacity Planning
    """,
    'author': "Syncoria",
    'website': "http://www.syncoria.com",
    'category': 'MRP',
    'version': '0.1',
    'depends': ['base', 'mrp'],

    'data': [
        'security/ir.model.access.csv',
        'views/mrp_workcenter_planning_view.xml',
        'views/mrp_workorder_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

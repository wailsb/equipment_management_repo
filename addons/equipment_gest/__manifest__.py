{
    'name': 'Enterprise Equipment Management',
    'version': '1.0',
    'category': 'Enterprise Equipment Management',
    'sequence': -100,
    'description': 'Enterprise Equipment Management',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'hr', 'mail'],
    'data': [
        'security/equipment_security.xml',
        'security/ir.model.access.csv',
        'views/equipment_views.xml',
        'views/assignment_views.xml',
        'views/menu.xml',
    ],
}

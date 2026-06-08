{
    'name': 'HR Leave Management ETB',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Time Off',
    'summary': 'Leave entitlement, service-based increments, and ETB monetary value calculation',
    'description': """
HR Leave Management Extension for Ethiopian Payroll
=====================================================
- Register total annual leave entitlement per employee
- Auto-apply leave increments based on service period
- Calculate leave days used and remaining
- Calculate monetary value of leave in Ethiopian Birr (ETB)
""",
    'author': 'Custom Development',
    'depends': [
        'base',
        'hr',
        'hr_contract',
        'hr_holidays'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/leave_increment_data.xml',
        'views/hr_leave_entitlement_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_leave_increment_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
{
    'name': 'Payroll Deduction',
    'version': '17.0.0.1',
    'summary': 'HR Payroll',
    'description': """HR Payroll""",
    'category': '',
    'website': '',
    'depends': [
        'hr',
        'base',
        'base_setup',
        'hr_contract',
        'om_hr_payroll',
        'hr_work_entry_holidays'
    ],

    'license': 'LGPL-3',

    'data': [
        'security/ir.model.access.csv',      
        'views/deduction.xml',
    ],
    'assets': {},
    'installable': True,
    'application': False,
}

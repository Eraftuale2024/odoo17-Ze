{
    'name': 'HR Employee Extension',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Add TIN Number and Pension Number to Employees',
    'author': 'Abraham Getachew',
    'depends': [
        'hr',
      'hr_contract'
    ],
    'data': [
        'views/hr_employee_views.xml',
        'views/hr_contract_views.xml'
    ],
    'installable': True,
    'application': False,
}
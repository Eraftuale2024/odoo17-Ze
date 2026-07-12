{
    'name': 'Custom Payroll Report',
    'version': '17.0',
    'summary': 'Custom Payroll Report',
    'sequence': 100,
    'description': """
        Custom Payroll Report module.
    """,

    'depends': ['base','om_hr_payroll','hr_holidays'],

    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/custom_hr_payroll_report_view.xml',
        'views/hr_payslip_custom_view.xml',
        'views/request_payroll_report_form_view.xml',
        'wizards/report_wizard_view.xml',
        'wizards/payroll_report_pdf_wizard.xml',
        'reports/print_pdf_payroll.xml',
        'reports/print_pdf_payroll_report.xml',
        'data/bank_latter_seq.xml',
    ],

    'assets': {
        'web.assets_backend': [
            # 'custom_hr_payroll_report/static/src/js/tree_view_redirect.js',
        ]
    },

    'installable': True,
    'auto_install': False,
}
from pprint import pprint

from reportlab.lib.pagesizes import landscape

from odoo import models, fields,api
from datetime import datetime


class PayrollReportWizard(models.TransientModel):
    _name = 'hr.payroll.report2'
    _description = 'Payroll Report Wizard'

    month = fields.Date(string='Month',default=fields.Date.today)
    payslip_id = fields.Boolean( string="Payslip")
    employee = fields.Boolean(string="Employee", default=True)
    department_id = fields.Boolean(string="Department")
    bank_account_id = fields.Boolean(string="Bank Account")
    period = fields.Boolean(string="Period")
    tin_no = fields.Boolean(string="Tin No", default=True)
    pension_no = fields.Boolean(string="Pension No", default=True)
    employment_date = fields.Boolean(string="Employment Date", default=True)
    monthly_basic_salary = fields.Boolean(string="Monthly Basic Salary")
    total_working_days = fields.Boolean(string="Total Working Days")
    total_day_worked = fields.Boolean(string="Total Day Worked")
    payslip_run_name = fields.Boolean(string="Month Of Payroll")
    structure = fields.Boolean(string="Structure")
    payslip_name = fields.Boolean(string="Payslip Name")
    basic = fields.Boolean(string="BASIC")
    basic_etb = fields.Boolean(string="BASIC Salary", default=True)
    gross = fields.Boolean(string="GROSS", default=True)
    net = fields.Boolean(string="NET", default=True)
    pension = fields.Boolean(string="Employee Pension (7%)")
    pension_comp = fields.Boolean(string="Employer Pension(11%)", default=True)
    tax = fields.Boolean(string="Income Tax", default=True)
    total_deduction = fields.Boolean(string="Total Deduction", default=True)
    overtime = fields.Boolean(string="Overtime", default=True)
    hra = fields.Boolean(string="Housing Allowance", default=True)
    da = fields.Boolean(string="Position Allowance", default=True)
    travel_allowance = fields.Boolean(string="Transport Allowance", default=True)
    travel_allowance_notax = fields.Boolean(string="None Taxable Transport Allowance", default=True)
    meal_allowance = fields.Boolean(string="Provision For Leave")
    medical_allowance = fields.Boolean(string="Medical Insurance")
    communication_allowance = fields.Boolean(string="Communication Allowance")
    internet_allowance = fields.Boolean(string="Mobile Allowance", default=False)
    non_tax_internet_allowance = fields.Boolean(string="None Taxable Mobile Allowance", default=True)
    fuel_allowance = fields.Boolean(string="Fuel Allowance")
    unused_leave_payment = fields.Boolean(string="Unused Leave Payment")
    severance_pay_compensation = fields.Boolean(string="Severance Pay Compensation")
    training_development = fields.Boolean(string="Training And Development")
    position_allowance = fields.Boolean(string="Position Allowance", default=True)
    other_deduction = fields.Boolean(string="Other Deduction", default=True)
    cost_sharing = fields.Boolean(string="Cost Sharing", default=True)
    non_tax_position_allowance = fields.Boolean(string="None Taxable Position Allowance", default=True)
    desert_allowance = fields.Boolean(string="Desert Allowance")
    non_tax_desert_allowance = fields.Boolean(string="None Taxable Desert Allowance", default=True)
    representation_allowance = fields.Boolean(string="Representation Allowance")
    taxable_salary = fields.Boolean(string="Taxable Income", default=True)
    total_payment = fields.Boolean(string="Severance net payment ")
    total_adjusted_payout = fields.Boolean(string="Severance TAX payment ")
    expense = fields.Boolean(string="Expense")
    loan = fields.Boolean(string="Loan")
    advance_salary = fields.Boolean(string="Advance Salary")
    bonus = fields.Boolean(string="Bonus")
    income_task_region = fields.Boolean(string="Income Tax Region")
    pension_task_region = fields.Boolean(string="Pension Tax Region")
    updated_on = fields.Boolean(string="Updated On")
    created_on = fields.Boolean(string="Created Date")
    last_updated = fields.Boolean(string="Last Updated")
    provident_employee = fields.Boolean(string="Employee Provident Fund")
    provident_employer = fields.Boolean(string="Employer Provident Fund", default=True)
    total_provident = fields.Boolean(string="Total Provident Fund")
    cleaning_allowance = fields.Boolean(string="Cleaning Allowance", default=False)
    non_tax_cleaning_allowance = fields.Boolean(string="None Taxable Cleaning Allowance", default=True)
    sum_non_taxable = fields.Boolean(string="Sum of None Taxable(mnth)", default=True)
    none_tax_das_allowance = fields.Boolean(string="None Tax DSA Allowance", default=True)
    tax_dsa_allowance = fields.Boolean(string="Tax, DSA Allowance", default=True)
    additional = fields.Boolean(string="Additional", default=True)
    pf_14 = fields.Boolean(string="PF 14%", default=True)
    pension_18 = fields.Boolean(string="Pension 18%", default=True)
    different_deduction = fields.Boolean(string="Different Deduction", default=True)
    other_allowance = fields.Boolean(string="Other Allowance", default=False)
    non_tax_other_allowance = fields.Boolean(string="None Taxable  Other Allowance", default=True)
    total_non_taxable = fields.Boolean(string="Total none taxable", default=False)
    dsa_allowance = fields.Boolean(string="DSA Allowance", default=False)
    payroll_ids = fields.Many2many("custom.hr.payroll.report")





    def action_print_report(self):
        data = {
            'payroll_ids': self.payroll_ids.ids,
            'month': self.month,
            'employee': self.employee,
            'tin_no': self.tin_no,
            'pension_no': self.pension_no,
            'employment_date': self.employment_date,

            'department_id': self.department_id,
            'bank_account_id': self.bank_account_id,
            'period': self.period,
            'monthly_basic_salary': self.monthly_basic_salary,
            'total_working_days': self.total_working_days,
            'total_day_worked': self.total_day_worked,
            'payslip_run_name': self.payslip_run_name,
            'structure': self.structure,
            'payslip_name': self.payslip_name,
            'basic': self.basic,
            'basic_etb': self.basic_etb,
            'gross': self.gross,
            'net': self.net,
            'pension': self.pension,
            'pension_comp': self.pension_comp,
            'tax': self.tax,
            'total_deduction': self.total_deduction,
            'overtime': self.overtime,
            'hra': self.hra,
            'da': self.da,
            'travel_allowance': self.travel_allowance,
            'travel_allowance_notax': self.travel_allowance_notax,
            'meal_allowance': self.meal_allowance,
            'medical_allowance': self.medical_allowance,
            'communication_allowance': self.communication_allowance,
            'internet_allowance': self.internet_allowance,
            'non_tax_internet_allowance': self.non_tax_internet_allowance,
            'fuel_allowance': self.fuel_allowance,
            'other_deduction': self.other_deduction,
            'cost_sharing': self.cost_sharing,
            'unused_leave_payment': self.unused_leave_payment,
            'severance_pay_compensation': self.severance_pay_compensation,
            'training_development': self.training_development,
            'position_allowance': self.position_allowance,
            'non_tax_position_allowance': self.non_tax_position_allowance,
            'desert_allowance': self.desert_allowance,
            'non_tax_desert_allowance': self.non_tax_desert_allowance,
            'representation_allowance': self.representation_allowance,
            'taxable_salary': self.taxable_salary,
            'total_payment': self.total_payment,
            'total_adjusted_payout': self.total_adjusted_payout,
            'expense': self.expense,
            'loan': self.loan,
            'advance_salary': self.advance_salary,
            'bonus': self.bonus,
            'income_task_region': self.income_task_region,
            'pension_task_region': self.pension_task_region,
            'updated_on': self.updated_on,
            'created_on': self.created_on,
            'last_updated': self.last_updated,
            'provident_employee': self.provident_employee,
            'provident_employer': self.provident_employer,
            'total_provident': self.total_provident,
            'cleaning_allowance': self.cleaning_allowance,
            'non_tax_cleaning_allowance': self.non_tax_cleaning_allowance,
            'sum_non_taxable': self.sum_non_taxable,
            'none_tax_das_allowance': self.none_tax_das_allowance,
            'tax_dsa_allowance': self.tax_dsa_allowance,
            'additional': self.additional,
            'pf_14': self.pf_14,
            'pension_18': self.pension_18,
            'different_deduction': self.different_deduction,
            'other_allowance': self.other_allowance,
            'non_tax_other_allowance': self.non_tax_other_allowance,
            'total_non_taxable': self.total_non_taxable,
            'dsa_allowance': self.dsa_allowance,
        }

        return self.env.ref('custom_hr_payroll_report.payroll_report_action_id').with_context(landscape=True).report_action(self, data=data)

class HrPayrollReportPDF(models.AbstractModel):
    _name = 'report.custom_hr_payroll_report.hr_report_template_id'

    def _get_report_values(self, docids, data=None):
        domain = [('status', '!=', 'cancel'),
                  ('id', 'in', data.get('payroll_ids'))]
        docs = self.env['custom.hr.payroll.report'].search(domain)
        departments = self.env['hr.department'].search([])
        total_data=[]
        for department in departments:
            domain = [('status', '!=', 'cancel'),('department_id', '=', department.id), ('id', 'in', data.get('payroll_ids'))]
            docs = self.env['custom.hr.payroll.report'].search(domain)
            if len(docs)>0:
                new_line={
                    "department": department.name,
                    "docs": docs
                    }
                total_data.append(new_line)

        raw_date = data.get('month')
        date_obj = datetime.strptime(raw_date, '%Y-%m-%d')
        month_year = date_obj.strftime('%B, %Y')
        colum = {
            'month': month_year,
            'employee': data.get('employee'),
            'tin_no': data.get('tin_no'),
            'pension_no': data.get('pension_no'),
            'employment_date': data.get('employment_date'),

            'department_id': data.get('department_id'),
            'bank_account_id': data.get('bank_account_id'),
            'period': data.get('period'),
            'monthly_basic_salary': data.get('monthly_basic_salary'),
            'total_working_days': data.get('total_working_days'),
            'total_day_worked': data.get('total_day_worked'),
            'payslip_run_name': data.get('payslip_run_name'),
            'structure': data.get('structure'),
            'payslip_name': data.get('payslip_name'),
            'basic': data.get('basic'),
            'basic_etb': data.get('basic_etb'),
            'gross': data.get('gross'),
            'net': data.get('net'),
            'pension': data.get('pension'),
            'pension_comp': data.get('pension_comp'),
            'tax': data.get('tax'),
            'total_deduction': data.get('total_deduction'),
            'overtime': data.get('overtime'),
            'hra': data.get('hra'),
            'da': data.get('da'),
            'travel_allowance': data.get('travel_allowance'),
            'travel_allowance_notax': data.get('travel_allowance_notax'),
            'meal_allowance': data.get('meal_allowance'),
            'medical_allowance': data.get('medical_allowance'),
            'communication_allowance': data.get('communication_allowance'),
            'internet_allowance': data.get('internet_allowance'),
            'non_tax_internet_allowance': data.get('non_tax_internet_allowance'),
            'fuel_allowance': data.get('fuel_allowance'),
            'cost_sharing': data.get('cost_sharing'),
            'other_deduction': data.get('other_deduction'),
            'unused_leave_payment': data.get('unused_leave_payment'),
            'severance_pay_compensation': data.get('severance_pay_compensation'),
            'training_development': data.get('training_development'),
            'position_allowance': data.get('position_allowance'),
            'non_tax_position_allowance': data.get('non_tax_position_allowance'),
            'desert_allowance': data.get('desert_allowance'),
            'non_tax_desert_allowance': data.get('non_tax_desert_allowance'),
            'representation_allowance': data.get('representation_allowance'),
            'taxable_salary': data.get('taxable_salary'),
            'total_payment': data.get('total_payment'),
            'total_adjusted_payout': data.get('total_adjusted_payout'),
            'expense': data.get('expense'),
            'loan': data.get('loan'),
            'advance_salary': data.get('advance_salary'),
            'bonus': data.get('bonus'),
            'income_task_region': data.get('income_task_region'),
            'pension_task_region': data.get('pension_task_region'),
            'updated_on': data.get('updated_on'),
            'created_on': data.get('created_on'),
            'last_updated': data.get('last_updated'),
            'provident_employee': data.get('provident_employee'),
            'provident_employer': data.get('provident_employer'),
            'total_provident': data.get('total_provident'),
            'cleaning_allowance': data.get('cleaning_allowance'),
            'non_tax_cleaning_allowance': data.get('non_tax_cleaning_allowance'),
            'sum_non_taxable': data.get('sum_non_taxable'),
            'none_tax_das_allowance': data.get('none_tax_das_allowance'),
            'tax_dsa_allowance': data.get('tax_dsa_allowance'),
            'additional': data.get('additional'),
            'pf_14': data.get('pf_14'),
            'pension_18': data.get('pension_18'),
            'different_deduction': data.get('different_deduction'),
            'other_allowance': data.get('other_allowance'),
            'non_tax_other_allowance': data.get('non_tax_other_allowance'),
            'total_non_taxable': data.get('total_non_taxable'),
            'dsa_allowance': data.get('dsa_allowance'),
        }

        return {
            'doc_ids': docs.ids,
            'doc_model': 'custom.hr.payroll.report',
            'docs': docs,
            'total_data': total_data,
            'datas': data,
            'colum': colum,
        }



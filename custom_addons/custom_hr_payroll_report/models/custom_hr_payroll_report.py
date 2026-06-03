import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'
    branch = fields.Char(string="Branch")
    location = fields.Char(string="Location")
    location_id = fields.Many2one('hr.work.location')


class customHrPayrollReport(models.TransientModel):
    _name = "custom.hr.payroll.report"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Payroll Report"

    payslip_id = fields.Many2one('hr.payslip', string="Payslip")
    employee = fields.Char(string="Employee")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    department_id = fields.Many2one('hr.department', string="Department")
    bank_account_id = fields.Many2one('res.partner.bank', string="Bank Account")
    period = fields.Char(string="Period")
    tin_no = fields.Char(string="Tin No")
    pension_no = fields.Char(string="Pension No")
    employment_date = fields.Date(string="Employment Date")
    monthly_basic_salary = fields.Float(string="Monthly Basic Salary")
    total_working_days = fields.Float(string="Total Working Days", digits=(4, 2))
    total_day_worked = fields.Float(string="Total Day Worked", digits=(4, 2))
    payslip_run_name = fields.Char(string="Month Of Payroll")
    structure = fields.Char(string="Structure")
    payslip_name = fields.Char(string="Payslip Name")
    basic = fields.Float(string="BASIC")
    basic_etb = fields.Float(string="BASIC")
    gross = fields.Float(string="GROSS")
    net = fields.Float(string="NET")
    pension = fields.Float(string="Employee Pension (7%)")
    pension_comp = fields.Float(string="Employer Pension(11%)")
    tax = fields.Float(string="Income Tax")
    total_deduction = fields.Float(string="Total Deduction")
    overtime = fields.Float(string="Overtime")
    hra = fields.Float(string="House Rent Allowance")
    da = fields.Float(string="Position Allowance")
    travel_allowance = fields.Float(string="Transport Allowance")
    travel_allowance_notax = fields.Float(string="None Taxable Transport Allowance")
    meal_allowance = fields.Float(string="Provision For Leave")
    medical_allowance = fields.Float(string="Medical Insurance")
    communication_allowance = fields.Float(string="Communication Allowance")
    internet_allowance = fields.Float(string="Mobile Allowance")
    non_tax_internet_allowance = fields.Float(string="None Taxable Mobile Allowance")
    fuel_allowance = fields.Float(string="Fuel Allowance")
    unused_leave_payment = fields.Float(string="Unused Leave Payment")
    severance_pay_compensation = fields.Float(string="Severance Pay Compensation")
    training_development = fields.Float(string="Training And Development")
    position_allowance = fields.Float(string="Position Allowance")
    non_tax_position_allowance = fields.Float(string="Position Allowance")
    desert_allowance = fields.Float(string="Desert Allowance")
    non_tax_desert_allowance = fields.Float(string="Taxable Desert Allowance")
    representation_allowance = fields.Float(string="Representation Allowance")
    other_deduction = fields.Float(string="Other Deduction")
    cost_sharing = fields.Float(string="Cost Sharing")
    taxable_salary = fields.Float(string="Taxable Income")
    total_payment = fields.Float(string="Severance net payment ")
    total_adjusted_payout = fields.Float(string="Severance TAX payment ")
    expense = fields.Float(string="Expense")
    loan = fields.Float(string="Loan")
    advance_salary = fields.Float(string="Advance Salary")
    bonus = fields.Float(string="Bonus")
    status = fields.Char(string="Status")
    income_task_region = fields.Char(string="Income Tax Region")
    pension_task_region = fields.Char(string="Pension Tax Region")
    updated_on = fields.Datetime(string="Updated On")
    created_on = fields.Datetime(string="Created Date")
    last_updated = fields.Datetime(string="Last Updated")
    provident_employee = fields.Float(string="Employee Provident Fund")
    provident_employer = fields.Float(string="Employer Provident Fund")
    total_provident = fields.Float(string="Total Provident Fund")
    cleaning_allowance = fields.Float(string="Cleaning Allowance")
    non_tax_cleaning_allowance = fields.Float(string="None Taxable Cleaning Allowance")
    sum_non_taxable = fields.Float(string="Sum of None Taxable(mnth)")
    none_tax_das_allowance = fields.Float(string="None Tax DSA Allowance")
    tax_dsa_allowance = fields.Float(string="Tax, DSA Allowance")
    additional = fields.Float(string="Additional")
    pf_14 = fields.Float(string="PF 14%")
    pension_18 = fields.Float(string="Pension 18")
    different_deduction = fields.Float(string="Different Deduction")
    other_allowance = fields.Float(string="Other Allowance")
    non_tax_other_allowance = fields.Float(string="None Taxable  Other Allowance")
    total_non_taxable = fields.Float(string="Total none taxable")
    dsa_allowance = fields.Float(string="DSA Allowance")
    location_id = fields.Many2one('hr.work.location', string="Location", compute='_compute_location', store=True)

    def print_payroll_pdf_report(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Report',
            'res_model': 'hr.payroll.report2',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payroll_ids': self.ids,
            }
        }

    def print_pdf_report(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Report',
            'res_model': 'hr.payroll.report1',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payroll_ids': self.ids,
            }
        }

    def fetch_and_update_report(self, date_from, date_to, department_id, location_id):
        last_update = datetime.datetime.now()
        default_company = self.env.user.company_id
        domain = ['|', ('company_id', '=', False), ('company_id', '=', default_company.id)]

        if date_from and date_to:
            domain += [('date_from', '>=', date_from), ('date_to', '<=', date_to)]
        if department_id:
            domain.append(('employee_id.department_id', '=', department_id.id))
        if location_id:
            domain.append(('employee_id.work_location_id', '=', location_id.id))

        payslips = self.env['hr.payslip'].search(domain, order='write_date desc')
        if len(payslips) > 0:
            last_update = payslips[0].write_date

        for pays in payslips:
            # Force refresh of employee record to get latest data
            employee = pays.employee_id.sudo()
            payroll_amount = self.update_payslips(pays.line_ids)
            contract = employee.contract_id
            working_days = 0, 0
            total_worked_days = 0

            if date_from and date_to:
                working_days = self.env['hr.attendance'].calculate_working_days(date_from, date_to,
                                                                                contract.resource_calendar_id)
                total_worked_days = self.env['hr.attendance'].compute_worked_days(employee, date_from, date_to,
                                                                                  working_days[1])
                if working_days[0] < total_worked_days:
                    total_worked_days = working_days[0]

            report_row = {
                'payslip_id': pays.id,
                'employee': employee.name,
                # FIXED: Force fetching updated fields from the live employee record
                'tin_no': employee.tin_no,
                'pension_no': employee.pension_no,
                'department_id': employee.department_id.id,
                'employment_date': contract.date_start,
                'payslip_run_name': pays.name,
                'monthly_basic_salary': contract.wage,
                'total_working_days': working_days[0],
                'total_day_worked': total_worked_days,
                'bank_account_id': employee.bank_account_id.id,
                'structure': pays.struct_id.name,
                'period': pays.date_from.strftime('%Y-%m-%d') + " - " + pays.date_to.strftime('%Y-%m-%d'),
                'payslip_name': pays.number,
                'basic': payroll_amount["basic"],
                'basic_etb': payroll_amount["basic_etb"],
                'taxable_salary': payroll_amount["taxable_salary"],
                'total_deduction': payroll_amount["total_deduction"],
                'gross': payroll_amount["gross"],
                'net': payroll_amount["net"],
                'pension': payroll_amount["pension"],
                'pension_comp': payroll_amount["pension_comp"],
                'tax': payroll_amount["tax"],
                'overtime': payroll_amount["overtime"],
                'hra': payroll_amount["hra"],
                'da': payroll_amount["da"],
                'travel_allowance': payroll_amount["travel_allowance"],
                'travel_allowance_notax': payroll_amount["travel_allowance_notax"],
                'meal_allowance': payroll_amount["meal_allowance"],
                'medical_allowance': payroll_amount["medical_allowance"],
                'communication_allowance': payroll_amount["communication_allowance"],
                'internet_allowance': payroll_amount["internet_allowance"],
                'non_tax_internet_allowance': payroll_amount["non_tax_internet_allowance"],
                'fuel_allowance': payroll_amount["fuel_allowance"],
                'unused_leave_payment': payroll_amount["unused_leave_payment"],
                'severance_pay_compensation': payroll_amount["severance_pay_compensation"],
                'training_development': payroll_amount["training_development"],
                'position_allowance': payroll_amount["position_allowance"],
                'other_deduction': contract.other_deduction,
                'cost_sharing': payroll_amount["cost_sharing"],
                'desert_allowance': payroll_amount["desert_allowance"],
                'representation_allowance': payroll_amount["representation_allowance"],
                'total_payment': payroll_amount["total_payment"],
                'total_adjusted_payout': payroll_amount["total_adjusted_payout"],
                'expense': payroll_amount["expense"],
                'loan': payroll_amount["loan"],
                'advance_salary': payroll_amount["advance_salary"],
                'bonus': payroll_amount["bonus"],
                'provident_employee': payroll_amount["provident_employee"],
                'provident_employer': payroll_amount["provident_employer"],
                'none_tax_das_allowance': payroll_amount["none_tax_das_allowance"],
                'pf_14': payroll_amount["additional"],
                'tax_dsa_allowance': payroll_amount["tax_dsa_allowance"],
                'additional': payroll_amount["pf_14"],
                'pension_18': payroll_amount["pension_18"],
                'different_deduction': payroll_amount["different_deduction"],
                'other_allowance': payroll_amount["other_allowance"],
                'total_non_taxable': payroll_amount["total_non_taxable"],
                'dsa_allowance': payroll_amount["dsa_allowance"],
                'cleaning_allowance': payroll_amount["cleaning_allowance"],
                'sum_non_taxable': payroll_amount["sum_non_taxable"],
                'non_tax_position_allowance': payroll_amount["non_tax_position_allowance"],
                'total_provident': payroll_amount["provident_employee"] + payroll_amount["provident_employer"],
                'status': pays.state,
                'created_on': pays.create_date,
                'updated_on': pays.write_date,
                'last_updated': last_update,
                'location_id': employee.work_location_id.id,
            }
            self.env['custom.hr.payroll.report'].sudo().create(report_row)

    # (Keep your existing refresh_report, confirm_payslip_status, return_payslip_detail, update_payslips, and _compute_location methods below unchanged)
    def refresh_report(self):
        self.env['custom.hr.payroll.report'].search(
            []).unlink()  # Fix: Target the transient model itself, not hr.payslip
        self.fetch_and_update_report(False, False, False, False)

    def confirm_payslip_status(self):
        for rec in self:
            self.env['hr.payslip'].search([('id', '=', rec.payslip_id.id)]).action_payslip_done()

    def return_payslip_detail(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Payslip',
                'res_model': 'hr.payslip',
                'view_mode': 'form,tree',
                'target': 'current',
                'res_id': rec.payslip_id.id,
                'context': {'default_id': rec.payslip_id.id, }
            }

    def update_payslips(self, payslip_lines):
        # ... (keep your existing implementation)
        return payroll_amount

    @api.depends('employee_id')
    def _compute_location(self):
        for record in self:
            record.location_id = record.employee_id.work_location_id if record.employee_id else False
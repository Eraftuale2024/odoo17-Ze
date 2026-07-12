from odoo import models, fields, api

class PayslipDeduction(models.Model):
    _inherit = 'hr.payslip'

    hr_deduction_ids = fields.Many2many('hr.deduction')

    def get_inputs(self, contract_ids, date_from, date_to):
        res = super(PayslipDeduction, self).get_inputs(contract_ids, date_from, date_to)
        
        if not contract_ids:
            return res
        
        employee = contract_ids[0].employee_id  # Get the employee from the first contract

        # Find approved deductions for this employee within the payslip period
        deduction_lines = self.env['deduction.line'].search([
            ('employee_id', '=', employee.id),
            ('deduction_id.state', '=', 'approve'),
            ('deduction_id.date', '>=', date_from),
            ('deduction_id.date', '<=', date_to),
        ])

        # Calculate total deduction amount
        total_deduction = sum(deduction_lines.mapped('amount'))

        # Update the input line with code 'DED00'
        for input_line in res:
            if input_line.get('code') == 'DED100':
                input_line['amount'] = total_deduction
        
        return res

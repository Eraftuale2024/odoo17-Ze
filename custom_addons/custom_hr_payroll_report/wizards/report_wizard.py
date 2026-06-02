from datetime import datetime, date
from pkg_resources import require
from reportlab.lib.pagesizes import landscape

from odoo import models, fields,api,_
from num2words import num2words
# from abyssinica import Date as EthiopicDate
# ✅ ADD THIS
from ethiopian_date import EthiopianDateConverter




class PayrollReportWizard(models.TransientModel):
    _name = 'hr.payroll.report1'
    _description = 'Payment Request'

    bank_id = fields.Many2one('res.partner.bank', string="Bank",required=True)
    date = fields.Date(string="Payroll Month",default=fields.Datetime.now)
    ref_no = fields.Char(string="Reference",default=lambda self: _('New'))
    payroll_ids = fields.Many2many("custom.hr.payroll.report")
    amount_in_word = fields.Char("Amount in word", compute="compute_amount_in_word")

    @api.depends('payroll_ids')
    def compute_amount_in_word(self):
        for rec in self:
            total=sum(pay.net  for pay in rec.payroll_ids)
            total1=round(total, 2)
            rec.amount_in_word = num2words(total1)


    def action_print_report(self):
        ref_no = self.env['ir.sequence'].next_by_code('hr.payroll.report1') or _('New')
        data = {
            'bank_id':self.bank_id.bank_id.name,
            'ref_no':ref_no,
            'branch':self.bank_id.branch,
            'branch_location':self.bank_id.location,
            'bank_acc':self.bank_id.acc_number,
            'date':  self.date.strftime("%B, %Y") if self.date else None ,
            'payroll_ids': self.payroll_ids.ids,
            'amount_in_word': self.amount_in_word,
        }
        return self.env.ref('custom_hr_payroll_report.payroll_report_action_id_bank_latter').report_action(self, data=data)

class HrPayrollReportPDF(models.AbstractModel):
    _name = 'report.custom_hr_payroll_report.hr_bank_latter_template_id'

    def _get_report_values(self, docids, data=None):
        domain = [('status', '!=', 'cancel'), ('id', 'in', data.get('payroll_ids'))]

        docs = self.env['custom.hr.payroll.report'].search(domain)


        page_no=int(len(docs)/24)
        if len(docs)%24 > 0:
            page_no=page_no+1


        today_date=datetime.now().strftime("%B,%d,%Y")
        today = date.today()

        # Step 2: Convert to Ethiopic date
        eth = EthiopianDateConverter.to_ethiopian(
            today.year, today.month, today.day
        )

        ethiopic_year = eth.year
        ethiopic_month_number = eth.month
        ethiopic_day = eth.day

        # Step 4: Map month number to name
        ethiopic_months = [
            "Meskerem", "Tikimt", "Hidar", "Tahsas", "Tir", "Yekatit",
            "Megabit", "Miyazya", "Ginbot", "Sene", "Hamle", "Nehase", "Pagumen"
        ]

        ethiopic_month_name = ethiopic_months[ethiopic_month_number - 1]
        print(f"Ethiopian Month: {ethiopic_month_name}")
        print(f"Ethiopian Year: {ethiopic_year}")


        colum = {
            'bank': data.get('bank_id'),
            'ref_no': data.get('ref_no'),
            'date': data.get('date'),
            'branch': data.get('branch'),
            'branch_location': data.get('branch_location'),
            'today_date': today_date,
            'amount_in_word': data.get('amount_in_word'),
            'bank_acc': data.get('bank_acc'),
            'no_pages': page_no,
            'no_pages_word': num2words(page_no),
            'ethiopic_year': ethiopic_year,
            'ethiopic_month': ethiopic_month_name,
        }

        return {
            'doc_ids': docs.ids,
            'doc_model': 'custom.hr.payroll.report',
            'docs': docs,
            'datas': data,
            'colum': colum,
        }



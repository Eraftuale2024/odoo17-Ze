from odoo import models, fields, api
from datetime import datetime

from odoo.exceptions import ValidationError


class OvertimeRequest(models.Model):
    _name = 'hr.deduction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "requested_by"
    requested_by = fields.Many2one('hr.employee', string="Requested By",required=True, tracking=True, )
    date = fields.Date(string="Date",tracking=True,)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('review', 'Review'),
        ('reject', 'Rejected'),
        ('approve', 'Approved'),
    ], string="state", default="draft", tracking=True)
    review_by = fields.Many2one('res.users', string="Review By", tracking=True, )
    approve_by = fields.Many2one('res.users', string="Approve By", tracking=True, )
    reject_by = fields.Many2one('res.users', string="Reject By", tracking=True, )
    employee_ids = fields.One2many('deduction.line',
                                      inverse_name='deduction_id', tracking=True)

    def action_submit(self):
        for rec in self:
            rec.state="submit"
    def action_review(self):
        for rec in self:
            rec.state="review"
            rec.review_by=self.env.user.id
    def action_approve(self):
        for rec in self:
            rec.state = "approve"
            rec.approve_by = self.env.user.id
    def action_reject(self):
        for rec in self:
            rec.state = "reject"
            rec.reject_by = self.env.user.id


class OvertimeRequestEmployee(models.Model):
    _name = 'deduction.line'
    deduction_id = fields.Many2one('hr.deduction', string="Request")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    reason = fields.Char(string="Reason", tracking=True)
    amount = fields.Float(string="Amount", tracking=True)
    remark = fields.Char(string="Remark", tracking=True)




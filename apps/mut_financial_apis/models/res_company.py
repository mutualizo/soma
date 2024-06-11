from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    user_to_notify_cnab = fields.Many2one(
        comodel_name="res.users", string="Usuário para Notificar CNAB"
    )
    days_until_bank_slips_due = fields.Integer(
        string="Dias até o vencimento dos boletos"
    )

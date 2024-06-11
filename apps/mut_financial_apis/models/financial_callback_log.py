from odoo import models, fields


class FinancialCallbackLog(models.Model):
    _name = "financial.callback.log"
    _description = "Financial Callback Log"

    cnab_return_id = fields.Many2one(
        comodel_name="l10n_br_cnab.return.log", string="CNAB Return Log"
    )
    payload = fields.Text(string="Payload", required=True)
    success = fields.Boolean(string="Success")
    error = fields.Char(string="Error Message")

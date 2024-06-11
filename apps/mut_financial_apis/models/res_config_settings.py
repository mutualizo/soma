from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    nifi_callback_url = fields.Char(
        string="Nifi Callback URL", config_parameter="mut_financial_apis.nifi_callback_url"
    )
    financial_api_key = fields.Char(
        string="Financial API Key", config_parameter="mut_financial_apis.load_api_key"
    )
    user_to_notify_cnab = fields.Many2one(
        comodel_name="res.users",
        related="company_id.user_to_notify_cnab",
        string="Usuário",
        readonly=False,
    )
    days_until_bank_slips_due = fields.Integer(
        related="company_id.days_until_bank_slips_due",
        string="Número de Dias",
        readonly=False,
    )

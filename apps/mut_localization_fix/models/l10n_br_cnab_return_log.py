from odoo import fields, models, api


class L10nBrCNABReturnLog(models.Model):
    _inherit = "l10n_br_cnab.return.log"
    _order = "id desc"

    company_id = fields.Many2one(comodel_name="res.company", string="Empresa")

    @api.model
    def create(self, vals):
        if vals.get("bank_account_id"):
            bank_account_id = (
                self.env["res.partner.bank"].sudo().browse(vals.get("bank_account_id"))
            )
            vals["company_id"] = bank_account_id.company_id.id
        return super(L10nBrCNABReturnLog, self).create(vals)

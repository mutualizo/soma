from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def multi_move_import(self, file_stream, ftype="csv"):
        res = super(AccountJournal, self).multi_move_import(
            file_stream=file_stream, ftype=ftype
        )
        if res._name == "l10n_br_cnab.return.log":
            res.update_bank_slip_status()
            res.send_cnab_return_callbacks()
        if res._name == "account.move":
            res.cnab_return_log_id.update_bank_slip_status()
            res.cnab_return_log_id.send_cnab_return_callbacks()
        return res

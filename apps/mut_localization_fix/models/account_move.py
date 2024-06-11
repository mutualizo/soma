# -*- coding: utf-8 -*-

from odoo import models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def get_overdues(self, *post):
        # TODO We need to improve the original SQL so the page do not take
        # 5min to load
        return {
            "due_partner": [],
            "due_amount": [],
            "result": [],
        }

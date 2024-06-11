# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    def write(self, vals):
        if 'value' in vals:
            if "http://" in vals['value'] and "http://localhost" not in vals['value']:
                base_url = vals['value'].replace("http://", "https://")
                vals['value'] = base_url
        return super(IrConfigParameter, self).write(vals)

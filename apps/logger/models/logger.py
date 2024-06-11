from odoo import models, fields


class Logger(models.Model):
    _name = 'logger'
    _description = 'Logger'

    message = fields.Char(string='Log Message', required=True)
    sender_ip = fields.Char(string='Sender IP')
    timestamp_message = fields.Char(string='Timestamp Message', readonly=True)
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now(), readonly=True)
    log_type = fields.Char(string='Log Type', default='debug')

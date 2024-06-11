# -*- coding: utf-8 -*-
from odoo import http, fields
import logging

from odoo.http import Response

_logger = logging.getLogger(__name__)


def log(**kw):
    if kw.get('type') == 'debug':
        _logger.debug(log)
    elif kw.get('type') == 'info':
        _logger.info(log)
    elif kw.get('type') == 'warning':
        _logger.warning(log)
    elif kw.get('type') == 'error':
        _logger.error(log)
    elif kw.get('type') == 'critical':
        _logger.critical(log)


def log_parser(**kw):
    log_type = kw.get('log_type') if kw.get('log_type') else 'debug'
    log_message = kw.get('message') if kw.get('message') else 'missing "message" on args'
    log_timestamp = kw.get('timestamp') if kw.get('timestamp') else 'missing "timestamp" on args'
    log_ip = kw.get('ip') if kw.get('ip') else 'missing "ip" on args'
    return {
        'sender_ip': log_ip,
        'log_type': log_type,
        'message': log_message,
        'timestamp_message': log_timestamp,
        'timestamp': fields.Datetime.now(),
    }


class LogController(http.Controller):
    @http.route('/log', auth='public')
    def index(self, **kw):
        try:
            parsed_log = log_parser(**kw)
            log(**parsed_log)
            http.request.env['logger'].sudo().create(parsed_log)
            return Response(status=200)
        except ValueError:
            return Response(status=404)

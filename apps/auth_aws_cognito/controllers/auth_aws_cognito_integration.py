"""AWS Cognito login"""
# -*- coding: utf-8 -*-
###################################################
#  __  __       _               _ _               #
# |  \/  |_   _| |_ _   _  __ _| (_)_______       #
# | |\/| | | | | __| | | |/ _` | | |_  / _ \      #
# | |  | | |_| | |_| |_| | (_| | | |/ / (_) |     #
# |_|  |_|\__,_|\__|\__,_|\__,_|_|_/___\___/      #
#                                                 #
###################################################
import werkzeug.urls
import werkzeug.utils
from werkzeug.urls import url_join

from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home


class OAuthLogin(Home):
    """This class is used for oauth login"""

    def cognito_direct_redirection(self):
        """Which provides the oauth provider to login to the odoo"""

        rec = request.env["auth.oauth.provider"].sudo().browse(
            request.env.ref('auth_aws_cognito.provider_aws_cognito').id
        )
        base_url = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param('web.base.url')
        )
        return_url = url_join(base_url, '/auth_oauth/signin')
        params = dict(
            client_id=rec.client_id,
            response_type=rec.cognito_response_type,
            scope=rec.scope,
            redirect_uri=return_url,
        )
        rec.write({
            'auth_link': "%s?%s" % (rec.auth_endpoint, werkzeug.urls.url_encode(params)),
        })

        return list(rec)

    def list_providers(self):
        """Which provides the oauth provider to login to the odoo"""
        return self.cognito_direct_redirection()

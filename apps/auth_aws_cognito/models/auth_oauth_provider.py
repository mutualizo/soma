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
from odoo import fields, models


class AuthOauthProvider(models.Model):
    """This class is used to add new fields into the provider"""

    _inherit = "auth.oauth.provider"

    cognito_response_type = fields.Selection(
        [("token", "Token"), ("code", "Code")],
        default="token",
        required=True,
        string="Response Type",
        help="Response type of the AWS Cognito",
    )
    cognito_aws_region = fields.Char('Região AWS', default='us-east-1')
    cognito_user_pool_id = fields.Char('Cognito Pool Id', default='us-east-1_QWi225cTs')

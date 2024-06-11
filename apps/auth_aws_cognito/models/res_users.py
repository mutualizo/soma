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
import json, logging, requests, boto3

from ast import literal_eval

from odoo.http import request
from odoo import api, models, fields, _, SUPERUSER_ID
from odoo import exceptions
from odoo.addons import base
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_users import SignupError

from botocore.exceptions import ClientError

base.models.res_users.USER_PRIVATE_FIELDS.append('oauth_access_token')
base.models.res_users.USER_PRIVATE_FIELDS.append('oauth_token_uid')
_logger = logging.getLogger(__name__)

try:
    import jwt
except ImportError:
    _logger.warning(
        "Login with AWS Cognito account won't be available.Please install PyJWT "
        "python library, ")
    jwt = None


class ResUsers(models.Model):
    """This class is used to inheriting the res.users and provides the oauth
    access"""
    _inherit = 'res.users'

    oauth_token_uid = fields.Char(string='OAuth User Token ID', help="Oauth Provider user_id", copy=False)
    email_verified = fields.Boolean(string='User Email Verified', default=False)

    def create_cognito_client(self, user_pool_id, region_name):
        if not self.env.user.oauth_access_token and self.env.user.name != 'OdooBot':
            raise UserError(
                _('You must be logged in to AWS Cognito to perform this action.'))
        if self.env.user.name == 'OdooBot':
            return boto3.client('cognito-idp', region_name=region_name)
        # Logins requer um mapeamento de identificador para o token de identidade
        logins = {
            f'cognito-idp.{region_name}.amazonaws.com/{user_pool_id}': self.env.user.oauth_token_uid
        }

        cognito_identity_client = boto3.client('cognito-identity', region_name=region_name)

        # Obtenha as credenciais temporárias do usuário autenticado
        response = cognito_identity_client.get_id(
            IdentityPoolId='us-east-1:7890c1de-cb95-46d8-934c-f3801199a1e9',
            Logins=logins
        )
        identity_id = response['IdentityId']

        credentials = cognito_identity_client.get_credentials_for_identity(
            IdentityId=identity_id,
            Logins=logins
        )

        # Extrai as credenciais temporárias
        temporary_credentials = credentials['Credentials']
        aws_access_key_id = temporary_credentials['AccessKeyId']
        aws_secret_access_key = temporary_credentials['SecretKey']
        aws_session_token = temporary_credentials['SessionToken']

        # Configura o cliente boto3 com as credenciais temporárias
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name
        )
        cognito_client = session.client('cognito-idp')

        return cognito_client

    def get_all_cnpjs_for_string(self, company_ids: list):
        cnpjs = ""
        for record in company_ids:
            companies = self.env["res.company"].browse(record)
            if companies.cnpj_cpf:
                cnpjs += companies.cnpj_cpf + ", "

        if cnpjs:
            cnpjs = cnpjs[:-2]

        return cnpjs

    def get_user_attributes(self, username):
        auth_oauth_provider = request.env["auth.oauth.provider"].sudo().browse(
            request.env.ref('auth_aws_cognito.provider_aws_cognito').id
        )
        client = self.create_cognito_client(auth_oauth_provider.cognito_user_pool_id,
                                            auth_oauth_provider.cognito_aws_region)
        try:
            response = client.admin_get_user(
                UserPoolId=auth_oauth_provider.cognito_user_pool_id,
                Username=username
            )
            return response['UserAttributes']

        except ClientError as e:
            return f"An error occurred: {e}"

    def register_user_without_password(self, name: str, email: str, companies_ids="", mobile="", address=""):
        auth_oauth_provider = request.env["auth.oauth.provider"].sudo().browse(
            request.env.ref('auth_aws_cognito.provider_aws_cognito').id
        )
        client = self.create_cognito_client(auth_oauth_provider.cognito_user_pool_id,
                                            auth_oauth_provider.cognito_aws_region)

        try:
            response = client.admin_create_user(
                UserPoolId=auth_oauth_provider.cognito_user_pool_id,
                Username=email,
                UserAttributes=[
                    {
                        'Name': 'name',
                        'Value': name
                    },
                    {
                        'Name': 'email_verified',
                        'Value': 'false'
                    },
                    {
                        'Name': 'email',
                        'Value': email
                    },
                    {
                        'Name': 'custom:companies_enabled',
                        'Value': companies_ids
                    },
                    {
                        'Name': 'phone_number',
                        'Value': mobile
                    },
                    {
                        'Name': 'address',
                        'Value': address
                    }
                ],
                DesiredDeliveryMediums=['EMAIL']
            )
            return response

        except ClientError as e:
            return f"An error occurred: {e}"

    def find_user_by_email(self, email: str):
        auth_oauth_provider = request.env["auth.oauth.provider"].sudo().browse(
            request.env.ref('auth_aws_cognito.provider_aws_cognito').id
        )
        client = self.create_cognito_client(auth_oauth_provider.cognito_user_pool_id,
                                            auth_oauth_provider.cognito_aws_region)

        try:
            response = client.list_users(
                UserPoolId=auth_oauth_provider.cognito_user_pool_id,
                Filter=f'email="{email}"'
            )
            return response['Users']

        except ClientError as e:
            return f"An error occurred: {e}"

    def disable_user(self, username):
        auth_oauth_provider = request.env["auth.oauth.provider"].sudo().browse(
            request.env.ref('auth_aws_cognito.provider_aws_cognito').id
        )
        client = self.create_cognito_client(auth_oauth_provider.cognito_user_pool_id,
                                            auth_oauth_provider.cognito_aws_region)

        try:
            response = client.admin_disable_user(
                UserPoolId=auth_oauth_provider.cognito_user_pool_id,
                Username=username
            )
            return response

        except ClientError as e:
            return f"An error occurred: {e}"

    def enable_user(self, username):
        auth_oauth_provider = request.env["auth.oauth.provider"].sudo().browse(
            request.env.ref('auth_aws_cognito.provider_aws_cognito').id
        )
        client = self.create_cognito_client(auth_oauth_provider.cognito_user_pool_id,
                                            auth_oauth_provider.cognito_aws_region)

        try:
            response = client.admin_enable_user(
                UserPoolId=auth_oauth_provider.cognito_user_pool_id,
                Username=username
            )
            return response

        except ClientError as e:
            return f"An error occurred: {e}"

    def is_user_enabled(self, username):
        auth_oauth_provider = request.env["auth.oauth.provider"].sudo().browse(
            request.env.ref('auth_aws_cognito.provider_aws_cognito').id
        )
        client = self.create_cognito_client(auth_oauth_provider.cognito_user_pool_id,
                                            auth_oauth_provider.cognito_aws_region)

        try:
            # Retrieve user details
            response = client.admin_get_user(
                UserPoolId=auth_oauth_provider.cognito_user_pool_id,
                Username=username
            )
            # Check the user's status
            user_status = response['UserStatus']
            # User is considered enabled if the status is 'CONFIRMED'
            is_enabled = user_status == 'CONFIRMED'
            return is_enabled
        except ClientError as e:
            return f"An error occurred: {e}"

    def update_user_attributes(self, username, user_attributes):
        auth_oauth_provider = request.env["auth.oauth.provider"].sudo().browse(
            request.env.ref('auth_aws_cognito.provider_aws_cognito').id
        )
        client = self.create_cognito_client(auth_oauth_provider.cognito_user_pool_id,
                                            auth_oauth_provider.cognito_aws_region)

        try:
            response = client.admin_update_user_attributes(
                UserPoolId=auth_oauth_provider.cognito_user_pool_id,
                Username=username,
                UserAttributes=user_attributes
            )
            return response

        except ClientError as e:
            return f"An error occurred: {e}"

    @api.model
    def _auth_oauth_rpc(self, endpoint, access_token):
        """This is used to pass the response of sign in."""
        if endpoint:
            headers = {'Authorization': 'Bearer %s' % access_token}
            return requests.get(endpoint, headers=headers).json()

    @api.model
    def _auth_oauth_code_validate(self, provider, code):
        """ Return the validation data corresponding to the access token """
        auth_oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        req_params = dict(
            client_id=auth_oauth_provider.client_id,
            grant_type='authorization_code',
            code=code,
            redirect_uri=request.httprequest.url_root + 'auth_oauth/signin',
        )
        headers = {'Accept': 'application/json'}
        token_info = requests.post(auth_oauth_provider.validation_endpoint,
                                   headers=headers, data=req_params).json()
        if token_info.get("error"):
            raise Exception(token_info['error'])
        access_token = token_info.get('access_token')
        validation = {
            'access_token': access_token
        }
        if token_info.get('id_token'):
            if not jwt:
                raise exceptions.AccessDenied()
            data = jwt.decode(token_info['id_token'], verify=False)
        else:
            data = self._auth_oauth_rpc(auth_oauth_provider.data_endpoint,
                                        access_token)
        validation.update(data)
        return validation

    @api.model
    def _auth_oauth_validate(self, provider, access_token):
        """ return the validation data corresponding to the access token """
        oauth_provider = self.env['auth.oauth.provider'].search([('name', '=', provider)])
        validation = self._auth_oauth_rpc(oauth_provider.validation_endpoint, access_token)
        if validation.get("error") and validation.get("error") is not None:
            raise Exception(validation['error'])
        if oauth_provider.data_endpoint:
            data = self._auth_oauth_rpc(oauth_provider.data_endpoint, access_token)
            validation.update(data)
        # unify subject key, pop all possible and get most sensible. When this
        # is reworked, BC should be dropped and only the `sub` key should be
        # used (here, in _generate_signup_values, and in _auth_oauth_signin)
        subject = next(filter(None, [
            validation.pop(key, None)
            for key in [
                'sub',  # standard
                'id',  # google v1 userinfo, facebook opengraph
                'user_id',  # google tokeninfo, odoo (tokeninfo)
            ]
        ]), None)
        if not subject:
            raise exceptions.AccessDenied('Missing subject identity')
        validation['user_id'] = subject

        return validation

    @api.model
    def auth_oauth(self, provider, params):
        """This is used to take the access token to sign in with the user account."""
        if params.get('code'):
            validation = self._auth_oauth_code_validate(provider,
                                                        params['code'])
            access_token = validation.pop('access_token')
            params['access_token'] = access_token
        else:
            access_token = params.get('access_token')
            validation = self._auth_oauth_validate(provider, access_token)
        if not validation.get('user_id'):
            if validation.get('id'):
                validation['user_id'] = validation['id']
            elif validation.get('oid'):
                validation['user_id'] = validation['oid']
            else:
                raise exceptions.AccessDenied()
        provider_id = self.env['auth.oauth.provider'].search([('name', '=', provider)]).id
        login = self._auth_oauth_signin(provider_id, validation, params)
        if not login:
            raise exceptions.AccessDenied()
        if provider and params:
            return self.env.cr.dbname, login, access_token
        return super(ResUsers, self).auth_oauth(provider, params)

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        """ Retrieve and sign in the user corresponding to provider and validated access token
                    :param provider: oauth provider id (int)
                    :param validation: result of validation of access token (dict)
                    :param params: oauth parameters (dict)
                    :return: user login (str)
                    :raise: AccessDenied if signin failed

                    This method can be overridden to add alternative signin methods.
                """
        try:
            user = self.search([('login', '=', validation.get('email'))])
            companies_enabled = ''

            if not self.is_user_enabled(validation.get('email')) or not user.active:
                raise exceptions.AccessDenied()

            for user_attributes in self.get_user_attributes(validation.get('email')):
                if not isinstance(user_attributes, dict):
                    continue

                if user_attributes.get('Name') == 'custom:companies_enabled':
                    companies_enabled = user_attributes.get('Value', '')
                    break

            if companies_enabled == '':
                raise exceptions.AccessDenied()

            companies_in_system_enable = []

            for all_companies in self.env['res.company'].search([]):
                if all_companies.cnpj_cpf:
                    if all_companies.cnpj_cpf in companies_enabled:
                        companies_in_system_enable.append(all_companies.id)

            if not companies_in_system_enable:
                raise exceptions.AccessDenied()

            if not user:

                user = self.create({
                    'login': str(validation.get('email')),
                    'name': str(validation.get('email')),
                    'oauth_provider_id': provider,
                    'company_ids': [(6, 0, companies_in_system_enable)],
                })
                template_user_id = literal_eval(
                    self.env['ir.config_parameter'].sudo().get_param('base.default_user', 'False')
                )
                template_user = self.browse(template_user_id)
                if template_user.exists():
                    user.groups_id = [(6, 0, template_user.groups_id.ids)]

            if not user:
                raise exceptions.AccessDenied()

            if (user.oauth_provider_id.id != provider or
                    user.oauth_uid != validation.get('user_id') or
                    user.oauth_token_uid != params.get('id_token') or
                    user.oauth_access_token != params.get('access_token')):
                user.write({
                    'oauth_provider_id': provider,
                    'oauth_uid': validation.get('user_id'),
                    'oauth_token_uid': params.get('id_token'),
                    'oauth_access_token': params.get('access_token'),
                })
            return user.login
        except exceptions.AccessDenied:
            if self.env.context.get('no_user_creation'):
                return None
            state = json.loads(params.get('state'))
            token = state.get('t')
            values = self._generate_signup_values(provider, validation, params)
            try:
                _, login, _ = self.signup(values, token)
                return login
            except SignupError:
                raise exceptions.AccessDenied

    def create(self, vals_list):
        # connect to cognito
        for vals in vals_list:
            if not self.find_user_by_email(vals['login']):
                empresas = self.get_all_cnpjs_for_string(vals.get('company_ids')[0][2])
                self.register_user_without_password(
                    name=vals['name'],
                    email=vals.get('login'),
                    companies_ids=empresas,
                    mobile=vals.get('mobile') or vals.get('phone') or "",
                )

        return super(ResUsers, self).create(vals_list)

    def unlink(self):
        if SUPERUSER_ID in self.ids:
            raise UserError(_('You can not remove the admin user as it is used internally for resources created by '
                              'Odoo (updates, module installation, ...)'))
        else:
            for user in self.ids:
                self.browse(user).write({'active': False})

    def write(self, values):
        if 'login' in values:
            raise UserError(
                _('You cannot change the login, as it is used internally for the primary key "username" for resources '
                  'created by Soma. If you really need to do this action, you can disable/delete the user in '
                  'question and create a new one with the new login...'))

        for user in self.ids:
            user_id = self.browse(user)
            if not user_id.email_verified:
                for user_attributes in user_id.get_user_attributes(user_id.login):
                    if not isinstance(user_attributes, dict):
                        continue
                    if user_attributes.get('Name') == 'email_verified':
                        values['email_verified'] = user_attributes.get('Value') == 'true'
                        break

            if 'active' in values:
                if not values['active']:
                    user_id.disable_user(values.get('login') or user_id.login)
                else:
                    user_id.enable_user(values.get('login') or user_id.login)

            if 'company_ids' in values or 'company_id' in values:
                user_id = self.browse(user)
                copanies_registered = ''
                companies_editable = ''

                for user_attributes in self.get_user_attributes(user_id.login):
                    if not isinstance(user_attributes, dict):
                        continue
                    if user_attributes.get('Name') == 'custom:companies_enabled':
                        copanies_registered = user_attributes.get('Value', '')
                        break

                if not copanies_registered:
                    if values.get('company_id') and not values.get('company_ids'):
                        if len(user_id.company_ids) > 1:
                            companies_editable = self.get_all_cnpjs_for_string(user_id.company_ids.ids).split(', ')
                        else:
                            companies_editable = self.get_all_cnpjs_for_string(values.get('company_id')).split(', ')
                    else:
                        companies_editable = self.get_all_cnpjs_for_string(values.get('company_ids')[0][2]).split(', ')

                elif values.get('company_ids') or values.get('company_id'):
                    if values.get('company_id') and not values.get('company_ids'):
                        if len(user_id.company_ids) > 1:
                            companies_toedit = self.get_all_cnpjs_for_string(user_id.company_ids.ids).split(', ')
                        else:
                            companies_toedit = self.get_all_cnpjs_for_string(values.get('company_id')).split(', ')
                    else:
                        companies_toedit = self.get_all_cnpjs_for_string(values.get('company_ids')[0][2]).split(', ')

                    copanies_registered_list = copanies_registered.split(', ')
                    companies_all_to_remove = self.get_all_cnpjs_for_string(
                        self.env['res.company'].search([]).ids
                    ).split(', ')

                    if companies_all_to_remove != ['']:
                        match = set(copanies_registered.split(', ')) & set(companies_all_to_remove)

                        if match:
                            for m in match:
                                copanies_registered_list.remove(m)

                        copanies_registered_list.extend(companies_toedit)
                        companies_editable = ", ".join(str(element) for element in copanies_registered_list)

                    else:
                        copanies_registered_list.extend(companies_toedit)
                        companies_editable = ", ".join(str(element) for element in copanies_registered_list)

                user_id.update_user_attributes(
                    username=user_id.login,
                    user_attributes=[
                        {
                            'Name': 'custom:companies_enabled',
                            'Value': companies_editable
                        },
                        {
                            'Name': 'address',
                            'Value': user_id.partner_id.contact_address
                        }
                    ]
                )
            if 'name' in values or 'mobile' in values or 'phone' in values:
                user_id.update_user_attributes(
                    username=user_id.login,
                    user_attributes=[
                        {
                            'Name': 'name',
                            'Value': values.get('name') or user_id.name
                        },
                        {
                            'Name': 'phone_number',
                            'Value': user_id.mobile or user_id.phone or ""
                        },
                        {
                            'Name': 'address',
                            'Value': user_id.partner_id.contact_address
                        }
                    ]
                )
        return super(ResUsers, self).write(values)

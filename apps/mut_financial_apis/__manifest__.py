{
    'name': 'Financial APIs',
    'version': "14.0.0.0",
    'category': 'Extra Tools',
    'description':  """
                    Create the APIs endpoints to load financial data to be invoiced in Odoo
                    and then sent to customers.
                    Before run set the following config settings:
                        - mut_financial_apis.callback_url
                            The endpoint to send the callback information when there's
                            status changes in Odoo invoices/bank slips
                        - mut_financial_apis.callback_api_key
                            The API KEY required to authenticate the Odoo invoice callbacks
                        - mut_financial_apis.load_api_key
                            The API KEY required to authenticate the requests sent to load
                            the invoices/bank slips in Odoo.
                    """,
    'author': 'Mutualizo',
    'company': 'Mutualizo',
    'maintainer': 'Mutualizo',
    'website': "https://www.mutualizo.com.br",
    'depends': ['l10n_br_account_payment_brcobranca', 'base_accounting_kit'],
    'data': [
        # Security
        "security/ir.model.access.csv",
        # Data
        "data/data.xml",
        "data/mail_template_data.xml",
        # Views
        "views/account_move.xml",
        "views/l10n_br_cnab_return_log.xml",
        "views/res_config_settings.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

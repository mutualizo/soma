import json
import requests
import logging

from odoo.http import request

logger = logging.getLogger(__name__)


def format_callback(external_id, status, error={}):
    return {
        "external_id_installment": external_id,
        "installment_state": status,
        "error": error,
    }

def send_callbacks(env, url, callbacks):
    callback_url = (
        env["ir.config_parameter"]
        .sudo()
        .get_param("mut_financial_apis.callback_url")
    )
    api_key = (
        env["ir.config_parameter"]
        .sudo()
        .get_param("mut_financial_apis.callback_api_key")
    )
    headers = {"Content-Type": "application/json", "x-api-key": api_key}
    if not callback_url:
        logger.error(
            "The Financial API Callback URL is not set. "
            "Please set the config parameter 'mut_financial_apis.callback_url'"
        )
        return
    res = requests.request(
        "POST",
        callback_url,
        headers=headers,
        data=json.dumps({"url_callback": url, "items": callbacks}),
    )
    if not res.ok:
        logger.error(
            f"Error communicating with the Financial API Callback URL: {res.text}"
        )
        if res.status_code == 403:
            logger.error(
                "Authorization error communicating with the Financial API Callback URL,"
                " please set the config parameter 'mut_financial_apis.callback_api_key'"
            )
        raise Exception(res.text)
    return res


class FinanceApiErrorMessages:
    MISSING_EXTERNAL_ID = {
        "code": "00",
        "message": "The field 'external_id' is required!"
    }
    COMPANY_NOT_FOUND = {
        "code": "01",
        "message": "No Company was found for the given 'cnpj_singular'!"
    }
    INVALID_CNPJ_CPF = {
        "code": "02",
        "message": "The payer's CNPJ/CPF is invalid!"
    }
    INVALID_DUE_DATE = {
        "code": "03",
        "message": "The installment due date is invalid! The correct date format is 'yyyy-mm-dd'."
    }
    INVALID_INSTALLMENT_AMOUNT = {
        "code": "04",
        "message": "The installment amount is invalid! Please use . as decimal separator."
    }
    INVALID_EMAIL = {
        "code": "05",
        "message": "The payer's e-mail is invalid!"
    }
    PAYMENT_MODE_NOT_FOUND = {
        "code": "06",
        "message": "The payment configuration is not set for the given 'cnpj_singular'"
    }
    EXTERNAL_ID_NOT_FOUND = {
        "code": "07",
        "message": "No invoice was founded for the given 'external_id'."
    }
    COMMAND_NOT_FOUND = {
        "code": "08",
        "message": "The value provided in 'command' is not valid."
    }

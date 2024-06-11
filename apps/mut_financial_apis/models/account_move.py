import pytz

from odoo import models, fields

from werkzeug.urls import url_join
from datetime import timedelta, date, datetime, time

from ..helpers import send_callbacks, format_callback


class AccountMove(models.Model):
    _inherit = "account.move"

    contract_number = fields.Char(string="Contract Number", tracking=True)
    total_installments = fields.Integer(string="Total Installments")
    installment_uid = fields.Char(string="Installment External Identifier")
    installment_number = fields.Integer(string="Installment Number")
    url_callback = fields.Char(string="URL Callback")
    additional_description_installment = fields.Text(
        string="Additional Description Installment"
    )
    notification_status = fields.Selection(
        [("not_sent", "Not Sent"), ("in_queue", "In Queue"), ("sent", "Sent")],
        string="Notification Status",
        default="not_sent",
    )
    bank_slip_status = fields.Selection(
        [
            ("bank_slip_not_issued", "Não Emitido"),
            ("bank_slip_issued", "Emitido"),
            ("bank_slip_error", "Erro"),
            ("bank_slip_registered", "Registrado"),
            ("bank_slip_paid", "Pago"),
            ("bank_slip_canceled", "Cancelado"),
        ],
        string="Status do Boleto",
        default="bank_slip_not_issued",
        tracking=True,
    )

    def _cron_confirm_invoices_generate_cnab(self):
        now = datetime.now(pytz.timezone("America/Sao_Paulo"))
        if now.weekday() < 5 and time(8, 0) <= now.time() <= time(17, 0):
            company_ids = self.env["res.company"].search(
                [
                    ("user_ids", "in", self.env.user.id),
                    ("days_until_bank_slips_due", "!=", False),
                ]
            )
            for company_id in company_ids:
                invoices_to_confirm = self.env["account.move"].search(
                    [
                        ("company_id", "=", company_id.id),
                        ("move_type", "=", "out_invoice"),
                        ("state", "=", "draft"),
                        (
                            "payment_mode_id.fixed_journal_id.bank_id",
                            "=",
                            self.env.ref("l10n_br_base.res_bank_237").id,
                        ),
                        ("contract_number", "!=", False),
                        ("invoice_line_ids", "!=", False),
                        (
                            "invoice_date_due",
                            "<=",
                            date.today()
                            + timedelta(days=company_id.days_until_bank_slips_due),
                        ),
                    ],
                    limit=2000,
                    order="id asc",
                )
                for invoice in invoices_to_confirm:
                    invoice.action_post()
                if invoices_to_confirm:
                    action_payment_order = (
                        invoices_to_confirm.create_account_payment_line()
                    )
                    payment_order_id = self.env["account.payment.order"].browse(
                        action_payment_order.get("res_id")
                    )
                    payment_order_id.draft2open()
                    payment_order_id.open2generated()
                    if company_id.user_to_notify_cnab:
                        self.env["mail.activity"].create(
                            {
                                "summary": (
                                    "Novo Arquivo de Remessa Criado: "
                                    + f"{payment_order_id.name}"
                                ),
                                "res_model_id": self.env.ref(
                                    "account_payment_order.model_account_payment_order"
                                ).id,
                                "res_id": payment_order_id.id,
                                "date_deadline": date.today(),
                                "user_id": company_id.user_to_notify_cnab.id,
                            }
                        )
        return

    def get_bank_slip_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        bank_slip = self.file_boleto_pdf_id
        if bank_slip:
            bank_slip.generate_access_token()
            return url_join(
                base_url,
                f"/web/content/{bank_slip.id}"
                + f"?download=true&access_token={bank_slip.access_token}",
            )
        return ""

    def send_bank_slip_to_invoice_followers(self):
        mail_template = self.env.ref("mut_financial_apis.email_template_send_bank_slip")
        context = {
            "invoice_date_due": self.invoice_date_due.strftime("%d/%m/%Y"),
            "contract_number": self.contract_number,
            "installment_number": self.installment_number,
            "company_email": self.company_id.email,
            "company_name": self.company_id.name,
            "payer_name": self.partner_id.name,
            "total_installments": self.total_installments,
        }

        for partner_id in self.message_follower_ids.mapped("partner_id"):
            mail_template.write(
                {
                    "email_to": partner_id.email,
                }
            )
            mail_template.with_context(context).send_mail(self.id, force_send=True)

    def _get_brcobranca_boleto(self, boletos):
        for boleto in boletos:
            cedente = boleto["cedente"] or ""
            cedente = cedente if len(cedente) < 70 else cedente[:70].strip() + "[...]"
            boleto["instrucoes"] = boleto.pop("instrucao1")
            boleto["cedente"] = cedente
        return super(AccountMove, self)._get_brcobranca_boleto(boletos)

    def generate_boleto_pdf(self):
        super(AccountMove, self).generate_boleto_pdf()
        if self.file_boleto_pdf_id and self.contract_number and self.installment_number:
            self.file_boleto_pdf_id.write(
                {"name": f"Boleto-{self.contract_number}-{self.installment_number}.pdf"}
            )
        self.write({"bank_slip_status": "bank_slip_issued"})

    def _cron_send_bank_slip_to_invoice_followers(self):
        now = datetime.now(pytz.timezone("America/Sao_Paulo"))
        if now.weekday() < 5 and time(8, 0) <= now.time() <= time(17, 0):
            account_move_ids = self.env["account.move"].search(
                [("notification_status", "=", "in_queue")], limit=500, order="id asc"
            )
            for account_move in account_move_ids:
                if not account_move.file_boleto_pdf_id:
                    account_move.generate_boleto_pdf()
                account_move.send_bank_slip_to_invoice_followers()
            account_move_ids.write({"notification_status": "sent"})
            api_user = self.env.ref("mut_financial_apis.api_user")
            env = self.env(user=api_user)
            callbacks = []
            for url_callback in set(account_move_ids.mapped("url_callback")):
                callbacks = [
                    format_callback(invoice.installment_uid, "bank_slip_issued")
                    for invoice in account_move_ids.filtered(
                        lambda x: x.url_callback == url_callback
                    )
                ]
                send_callbacks(env, url_callback, callbacks)

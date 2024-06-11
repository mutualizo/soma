from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Binary


class BinaryInherit(Binary):

    @http.route(
        [
            "/web/content",
            "/web/content/<string:xmlid>",
            "/web/content/<string:xmlid>/<string:filename>",
            "/web/content/<int:id>",
            "/web/content/<int:id>/<string:filename>",
            "/web/content/<int:id>-<string:unique>",
            "/web/content/<int:id>-<string:unique>/<string:filename>",
            "/web/content/<int:id>-<string:unique>/<path:extra>/<string:filename>",
            "/web/content/<string:model>/<int:id>/<string:field>",
            "/web/content/<string:model>/<int:id>/<string:field>/<string:filename>",
        ],
        type="http",
        auth="public",
    )
    def content_common(
        self,
        xmlid=None,
        model="ir.attachment",
        id=None,
        field="datas",
        filename=None,
        filename_field="name",
        unique=None,
        mimetype=None,
        download=None,
        data=None,
        token=None,
        access_token=None,
        **kw,
    ):
        res = super(BinaryInherit, self).content_common(
            xmlid=xmlid,
            model=model,
            id=id,
            field=field,
            filename=filename,
            filename_field=filename_field,
            unique=unique,
            mimetype=mimetype,
            download=download,
            data=data,
            token=token,
            access_token=access_token,
            kw=kw,
        )
        if model != "ir.attachment" or not download or not id:
            return res
        attachment_id = request.env["ir.attachment"].sudo().search([("id", "=", id)])
        if attachment_id.res_model != "account.payment.order":
            return res
        payment_order_id = (
            request.env["account.payment.order"].sudo().browse(attachment_id.res_id)
        )
        if payment_order_id.state != "generated":
            return res
        payment_order_id.payment_line_ids.mapped("move_id").write(
            {"notification_status": "in_queue"}
        )
        payment_order_id.generated2uploaded()
        return res

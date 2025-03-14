from odoo import fields, models, api
from odoo.tools import float_compare

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    account_payment_ids = fields.One2many(
        "account.payment", "purchase_id", string="Pay purchase advanced", readonly=True
    )



    # Total Amount Order dikurangi advanced payment dan dikurangi dengan nilai invoice yang sudah dibayar atas PO (Purchase Order)
    amount_residual = fields.Float(
        string="Residual Amount",
        readonly=True,
        compute="_compute_purchase_advanced_payment",
        store=True,
    )

    # Baris baris advanced payment dari PO
    payment_line_ids = fields.Many2many(
        "account.move.line",
        readonly="Payment move lines",
        compute="_compute_purchase_advanced_payment",
        store="True",
    )

    # Status advanced payment dari PO untuk mengetahui sudah Paid / Belum
    advanced_payment_status = fields.Selection(
        selection=[
            ("not_paid", "Not Paid"),
            ("paid", "Paid"),
            ("partial", "Partially Paid"),
        ],
        store=True,
        readonly=True,
        copy=False,
        tracking=True,
        # Semua Field diatas merupakan compute disini
        compute="_compute_purchase_advanced_payment",
    )

    # Bagian ini mendefinisikan field-field yang mempengaruhi perhitungan advanced payment
    @api.depends(
        "currency_id",                                              # Mata uang yang digunakan
        "company_id",                                               # Perusahaan yang terkait
        "amount_total",                                             # Total jumlah order
        "account_payment_ids",                                      # Daftar pembayaran yang terkait dengan PO
        "account_payment_ids.state",                                # Status dari pembayaran
        "account_payment_ids.move_id",                              # Jurnal entri dari pembayaran
        "account_payment_ids.move_id.line_ids",                     # Baris jurnal dari pembayaran
        "account_payment_ids.move_id.line_ids.date",                # Tanggal dari baris jurnal
        "account_payment_ids.move_id.line_ids.debit",               # Nilai debit dari baris jurnal
        "account_payment_ids.move_id.line_ids.credit",              # Nilai kredit dari baris jurnal
        "account_payment_ids.move_id.line_ids.currency_id",         # Mata uang dari baris jurnal
        "account_payment_ids.move_id.line_ids.amount_currency",     # Nilai mata uang dari baris jurnal
        "order_line.invoice_lines.move_id",                         # Jurnal entri dari invoice
        "order_line.invoice_lines.move_id.amount_total",            # Total jumlah dari jurnal invoice
        "order_line.invoice_lines.move_id.amount_residual",         # Sisa jumlah dari jurnal invoice
    )

    # Mendefinisikan fungsi dari Field Compute yang diatas
    # Fungsi compute dalam ini juga adalah sebuah compute method dalam odoo yang digunakan 
    # Untuk menghitung status pembayaran uang muka advanced payment status pada suatu purchase order 
    def _compute_purchase_advanced_payment(self):

        # Mengambil semua jurnal entries dari pembayaran yang beruhubungan dengan PO
        for order in self:
            mls = order.account_payment_ids.mapped("move_id.line_ids").filtered(
                lambda x: x.account_id.account_type == "liability_payable"
                    and x.parent_state == "posted"
            )

            # Menghitung total pembayaran uang muka
            advanced_amount = 0.0

            for line in mls:
                line.currency_id == line.currency_id or line.company_id.currency_id
                line_amount = (
                    line.amount_residual_currency
                    if line.currency_id
                    else line.amount_residual
                )
                if line.currency_id != order.currency_id:
                    advanced_amount += line.currency_id._convert(
                        line_amount,
                        order.currency_id,
                        order.company_id,
                        line.date or fields.Date.today(),
                    )

                else:
                    advanced_amount += line_amount

            # Menghitung Pembayaran dalam Invoice
            invoice_paid_amount = 0.0
            for inv in order.invoice_ids:
                invoice_paid_amount += inv.amount_total - inv.amount_residual

            # Menentukan sisa pembayaran
            amount_residual = (order.amount_total - advanced_amount - invoice_paid_amount)


            # Menentukan status pembayaran
            payment_state = "not_paid"
            if mls or order.invoice_ids:
                # Untuk mengkomparasi Nilai Float
                has_due_amount = float_compare(
                    amount_residual, 0.0,     # Jika amount residual kurang dari atau sama dengan 0 maka status pembayaran adalah paid
                    precision_rounding=order.currency_id.rounding
                )
                # Jika amount residual lebih dari 0 maka status pembayaran adalah partial, jika tidak maka status pembayaran adalah not paid
                if has_due_amount <= 0:
                    payment_state = "paid"
                elif has_due_amount > 0:
                    payment_state = "partial"

            # Menentapkan nilai dari field-field yang telah dihitung
            order.payment_line_ids = mls

            # Untuk Menyimpan nilai sisa pembayaran
            order.amount_residual = amount_residual

            # Untuk Menyimpan status pembayaran
            order.advanced_payment_status = payment_state
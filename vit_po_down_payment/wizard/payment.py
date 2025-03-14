from logging import exception
from zoneinfo import available_timezones
from odoo.exceptions import ValidationError

from odoo import _, api, fields, models

class AccountVoucherWizardPurchase(models.TransientModel):
    _name ="account.voucher.wizard.purchase"
    _description = "Account Voucher Wizard Purchase"

    # Menentukan relasi wizard ini dengan purchase.order
    order_id = fields.Many2one('purchase.order', required=True)

    # Untuk menampilkan pilihan journal yang akan digunakan pada Payment
    journal_id = fields.Many2one(
        'account.journal',
        'Journal',
        required=True,
        domain=[("type", "in", ("bank", "cash"))],
    )

    # Untuk menampilkan pilihan currency yang digunakan oleh Journal yang dipilih pada Payment
    journal_currency_id = fields.Many2one(
        'res.currency',
        'Journal Currency',
        store="True",
        readonly=False,
        # Untuk mencari default Currency yang akan digunakan
        compute="compute_get_journal_currency",
    )

    # Untuk menampilkan pilihan Currency yang digunakan oleh Purchase Order yang dipilih pada Payment
    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        readonly=False,
        required=True,
    )

    # Untuk menampilan informasi total amount yang harus dibayar
    amount_total = fields.Monetary(readonly=True)

    # Untuk tempat menampung isian amount down payment yang akan dibayarkan
    amount_advance = fields.Monetary(
        "Amount advanced",
        required=True,
        currency_field="journal_currency_id",
    )

    # Untuk menyimpan tanggal transaksi down payment
    date = fields.Date(
        required=True,
        default=fields.Date.context_today,
    )

    # Untuk menampilkan amount dalam currency yang digunakan oleh PO
    currency_amount = fields.Monetary(
        "Curr. amount",
        readonly=True,
        currency_field="currency_id",
        compute="_compute_currency_amount",
        store=True,
    )

    # Sebagai tempat isian Referensi / Informasi tambahan pembayaran Down Payment
    payment_ref = fields.Char("Ref.")


    # Menjalakan fungsi compute untuk menampilkan Payment Method
    payment_method_line_id = fields.Many2one(
        comodel_name="account.payment.method.line",
        string="Payment Method",
        readonly=False,
        store="True",
        compute="_compute_payment_method_line_id",
        domain="[('id', 'in', available_payment_method_line_ids)]",
    )

    # Menjalankan fungsi compute available payment method line ids
    available_payment_method_line_ids = fields.Many2many(
        comodel_name="account.payment.method.line",
        compute="_compute_available_payment_method_line_ids",
    )
    # Yang akan berjalan ketika ada perubahan Field Journal currency ID (BERLAKU UNTUK SEMUA @api.depends('journal_currency_id'))
    @api.depends("journal_id")
    def _compute_get_journal_currency(self):
        # Dalam rangka mencari currency yang digunakan oleh Journal yang dipilih
        for wzd in self:
            # Gunakan currency Company jika Journal tidak punya default Currency
            wzd.journal_currency_id = (
                wzd.journal_id.currency_id.id
                or self.env.user.company_id.currency_id.id
            )

    @api.depends("journal_id")
    def _compute_payment_method_line_id(self):
        # Dalam rangka mencari payment method Line pertama dari payment method yang tersedia bertipe outbound
        for wizard in self:
            if wizard.journal_id:
                available_payment_method_lines = (
                    wizard.journal_id._get_available_payment_method_lines("outbound")
                )
            else:
                available_payment_method_lines = False

            # Jika ditemukan oleh available_payment_method_lines
            if available_payment_method_lines:
                # Maka is Field payment method ini dengan ID payment Method yang pertama ditemukan yaitu melalui atribut origin
                wizard.payment_method_line_id = available_payment_method_lines[
                    0
                ]._origin
            # Jika tidak ditemukan maka is Field payment method ini dengan False
            else:
                wizard.payment_method_line_id = False

    @api.depends("journal_id")
    def _compute_available_payment_method_line_ids(self):
        # Untuk mencari Payment Method yang bertipe outbound
        for wizard in self:
            if wizard.journal_id:
                wizard.available_payment_method_line_ids = (
                    wizard.journal_id._get_available_payment_method_lines("outbound")
                )
            else:
                wizard.available_payment_method_line_ids = False

    @api.constrains("amount_advance")
    def check_amount(self):
        # Untuk mengecek apakah amount advance yang diinputkan adalah positif
        if self.journal_currency_id.compare_amounts(self.amount_advance, 0.0) <= 0:
            raise ValidationError(_("Amount of advance must be positive"))

        if self.env.context.get("active_id", False):
            if (
                    # Dan tidak lebih besar daripada Amount PO (Purchase Order)
                    self.currency_id.compare_amounts(
                        self.currency_amount, self.order_id.amount_residual
                    )
                    > 0
            ):
                raise ValidationError(
                    _("Amount of advance is greater than residual "
                      "amount on purchase")
                )


    @api.model
    def default_get(self, fields_list):
        # Untuk Override fungsi default get bawaan dari odoo
        res = super().default_get(fields_list)
        purchase_ids = self.env.context.get("active_ids", [])
        # Agar ketika dipanggil Fungsi ini akan mengeluarkan Dictionary yang menampilkan Purchase Order ID
        if not purchase_ids:
            return res

        purchase_id = fields.first(purchase_ids)
        purchase = self.env["purchase.order"].browse(purchase_id)

        if "amount_total" in fields_list:
            res.update(
                {
                    "order_id": purchase.id,
                    "amount_total": purchase.amount_residual,
                    "currency_id": purchase.currency_id.id,
                }
            )

        res["journal_id"] = (
            self.env["account.journal"]
            .search(
                [
                    ("type", "in", ("bank", "cash")),
                    ("company_id", "=", purchase.company_id.id),
                    ("outbound_payment_method_line_ids", "!=", False),
                ],
                limit=1,
            )
            .id
        )

        usd_currency = self.env.ref('base.USD')
        res["journal_currency_id"] = usd_currency.id if usd_currency else self.env.user.company_id.currency_id.id

        return res

    @api.depends("journal_id", "date", "amount_advance", "journal_currency_id")
    def _compute_currency_amount(self):
        # Menghitung amount dalam currency jika currency yang dipilih tidak sama dengan currency PO
        if self.journal_currency_id != self.currency_id:
            amount_advance = self.journal_currency_id._convert(
                self.amount_advance,
                self.currency_id,
                self.order_id.company_id,
                self.date or fields.Date.today(),
            )

        else:
            # Jika currency Journal yang dipilih sama dengan currency PO
            amount_advance = self.amount_advance
        # maka amount advance akan mengeluarkan nilai amount advance apa adanya tanpa Konversi
        self.currency_amount = amount_advance

    def make_advance_payment(self):
        self.ensure_one()
        payment_obj = self.env["account.payment"]
        purchase_obj = self.env["purchase.order"]

        # Yang akan dibuat Down Paymentnya
        purchase_ids = self.env.context.get("active_ids", [])
        # Jika ada maka ambil dan baca record PO yang pertama dari Active ID
        if purchase_ids:
            purchase_id = fields.first(purchase_ids)
            purchase = purchase_obj.browse(purchase_id)
            # Membuat record Payment melalui fungsi prepare payment vals
            payment_vals = self._prepare_payment_vals(purchase)
            # Setelah itu akan menjalankan create atas object payment yang telah dibuat
            payment = payment_obj.create(payment_vals)

        return {
            "type": "ir.actions.act_window_close",
        }

    def _prepare_payment_vals(self, purchase):
        partner_id = purchase.partner_id.commercial_partner_id.id
        return {
            "purchase_id": purchase.id,             # Field purchase id harus mengarah ke ID dari object Purchase Order yang sedang dibuat Down Paymentnya
            "date": self.date,
            "amount": self.amount_advance,          # Field linenya adalah standed Field untuk membuat record payment
            "payment_type": "outbound",
            "partner_type": "supplier",
            "ref": self.payment_ref or purchase.name,
            "journal_id": self.journal_id.id,
            "currency_id": self.journal_currency_id.id,
            "partner_id": partner_id,
            "payment_method_line_id": self.payment_method_line_id.id,
        }
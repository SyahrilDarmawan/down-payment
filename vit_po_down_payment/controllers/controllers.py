# -*- coding: utf-8 -*-
# from odoo import http


# class VitPoDownPayment(http.Controller):
#     @http.route('/vit_po_down_payment/vit_po_down_payment', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vit_po_down_payment/vit_po_down_payment/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vit_po_down_payment.listing', {
#             'root': '/vit_po_down_payment/vit_po_down_payment',
#             'objects': http.request.env['vit_po_down_payment.vit_po_down_payment'].search([]),
#         })

#     @http.route('/vit_po_down_payment/vit_po_down_payment/objects/<model("vit_po_down_payment.vit_po_down_payment"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vit_po_down_payment.object', {
#             'object': obj
#         })

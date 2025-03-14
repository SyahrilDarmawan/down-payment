# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class vit_po_down_payment(models.Model):
#     _name = 'vit_po_down_payment.vit_po_down_payment'
#     _description = 'vit_po_down_payment.vit_po_down_payment'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

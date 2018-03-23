# -*- coding: utf-8 -*-
from odoo import http

# class AmosCar(http.Controller):
#     @http.route('/amos_car/amos_car/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/amos_car/amos_car/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('amos_car.listing', {
#             'root': '/amos_car/amos_car',
#             'objects': http.request.env['amos_car.amos_car'].search([]),
#         })

#     @http.route('/amos_car/amos_car/objects/<model("amos_car.amos_car"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('amos_car.object', {
#             'object': obj
#         })
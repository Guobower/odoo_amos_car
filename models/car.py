# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError

class amos_car(models.Model):
    _name = 'amos_car.amos_car'

    name = fields.Char(u"车辆名称",size=4)
    code = fields.Char(u"单据编号",size=64,default='New')
    active = fields.Boolean(u"有效", default=True)  # 专用属性，为False的话实例为不可见, required=True
    instructor = fields.Boolean(u"是否停产")
    date = fields.Date(u"短日期")
    date_order = fields.Datetime(u"长日期")
    qty = fields.Integer(u"数量")
    list_price = fields.Float(u"优惠", default=0.0, digits=(16, 3))
    note = fields.Text(u"备注", translate=True)  # 设置可翻译字段
    content = fields.Html(u"正文", strip_style=False)
    sex = fields.Selection([(0, u"不限"), (1, "男"), (2, "女")], u"性别", )  # 选项必须在前面，否则报错
    user_id = fields.Many2one('res.users', u"业务员", default=lambda self: self.env.user, domain=[('id', '=', 1)])  # domain在客户端候选值里设定一个可选的domain
    lines = fields.One2many("res.car.line", "order_id", u"维修日记")
    partner_ids = fields.Many2many("res.partner", string=u"联系人1")  # 必须是string=u"",不可以直接写u"",不知道为什么
    partner_idss = fields.Many2many("res.partner", "res_car_amos_rel", "car_id", "partner_id",string=u"联系人2")  # 自定义第三张表及字段
    function = fields.Char(related="user_id.partner_id.function", store=True, string=u"职位")
    state = fields.Selection([  # 保留字段
        ('draft', u"草稿"),
        ('review', u"等待审核"),
        ('done', u"已完成"),
        ('sent', u"发送邮件"),
        ('cancel', u"取消")
    ], string=u"状态",default="draft")
    total = fields.Float(compute="_compute_total", string=u"合计", store=True, )  # 将值存到数据库，否则为动态合计

    @api.model
    def create(self,vals): #重写create创建,创建自动编号，vals为当前界面传过来的所有值
        print vals,'11'
        vals['list_price'] = 100
        print vals.get('code'),'22'

        if vals.get('code','New') == 'New':
            vals['code']=self.env['ir.sequence'].next_by_code('123') or 'New'

        result = super(amos_car,self).create(vals)
        return result

    @api.multi
    def write(self, values): #重写write编辑

        values['list_price'] = 400

        if values.has_key('qty'):
            if values['qty'] == 100:
                values['list_price']=10

        result = super(amos_car, self).write(values)
        return result

    @api.multi
    def unlink(self):  # 重写unlink删除
        for order in self: #重命名self为order
            if self._uid == 1:#uid为当前登录用户user表的索引id,
                pass
            else:
                if order.state != 'draft':
                    raise UserError(u'只能删除草稿单据!')
        return super(amos_car, self).unlink()

    @api.multi
    def read(self,fields=None,load='_classic_read'):  # 重写read读取过滤权限
        print fields #print结果为[u'name', u'active', u'instructor', u'date', u'date_order']
        fields = [u'name', u'active', u'instructor']#过滤掉date，date_order，使其看不见数据
        return super(amos_car, self).read(fields=fields,load=load)
        


    @api.depends('lines.price', 'list_price')
    def _compute_total(self):
        acc = 0.00
        for record in self.lines:
            acc += record.price

        self.total = acc - self.list_price

    @api.multi
    def action_draft(self):
        self.write({"state":"draft"})

    @api.multi
    def action_done(self):
        self.write({"state": "done"})

    @api.multi
    def action_cancel(self):
        self.write({"state": "cancel"})

    @api.multi
    def action_review(self):
        self.write({"state": "review"})

    @api.multi
    def action_amos(self):
        model_id = self.env['ir.model'].search([]) #self.env['model'].search(domain) 获取某个model的环境，查询其中的记录集
        name = self.env['res.company'].search([],limit=1).name
        count = self.env['res.users'].search_count([])
        object = self.env['res.partner'].search([('is_company','=',True),('customer','=',True)])

        for i in model_id:
            print i.name
            print i.id

        print model_id
        print model_id._ids #得到id集合
        print name
        print count
        print object

    @api.multi
    def action_amos_create(self):
        values = {
            'name':'amos',
            'qty':100,
            'state':'done',
        }
        self.env['amos_car.amos_car'].create(values)

    @api.multi
    def action_amos_update(self):
        object = self.env['amos_car.amos_car'].search([('name', '=','amos')])
        values = {
            'name': 'amos',
            'qty': 1001,
            'state': 'draft',
        }
        object.write(values)

    @api.multi
    def action_amos_browse(self):
        partner = self.env['res.partner'].browse(1)
        partners = self.env['res.partner'].browse([1, 2])

        for i in partners:
            print i.name
            print i.email or ""

        print partner.name


class Res_Car_Line(models.Model):
    _name="res.car.line"
    _description=u"日志"
    _log_access=False #是否创建日期字段，默认是创建True,设为False减轻数据库负担

    name = fields.Char(u"res.car.line备注")
    sequence = fields.Integer(u"排序",default=10,help=".")#保留字段
    price = fields.Float(u"价格",default=0.0)
    order_id = fields.Many2one("res.car",u"车辆信息",ondelete='cascade',index=True)#联动删除，索引
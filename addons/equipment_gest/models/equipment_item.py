from odoo import models, fields

class EquipmentItem(models.Model):
    _name = 'equipment.item'
    _description = 'Equipment Item'

    status = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned'),
    ], default='available')

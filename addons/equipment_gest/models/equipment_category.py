from odoo import models, fields

class EquipmentCategory(models.Model):
    _name = 'equipment.category'
    _description = 'Equipment Category'

    name = fields.Char(required=True)

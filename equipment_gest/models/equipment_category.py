from odoo import models, fields


class EquipmentCategory(models.Model):
    _name = 'equipment.category'
    _description = 'Equipment Category'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True, index=True)
    equipment_ids = fields.One2many('equipment.item', 'category_id', string='Equipment Items')
    equipment_count = fields.Integer(string='Equipment Count', compute='_compute_equipment_count')

    def _compute_equipment_count(self):
        for category in self:
            category.equipment_count = len(category.equipment_ids)

    def action_save_and_close(self):
        self.ensure_one()
        return self.env.ref('equipment_gest.action_equipment_category').read()[0]


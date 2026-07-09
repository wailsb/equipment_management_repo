from odoo import api, models

class EquipmentAssignment(models.Model):
    _inherit = 'equipment.assignment'

    @api.model
    def create(self, vals):
        assignment = super(EquipmentAssignment, self).create(vals)
        if assignment.state == 'active':
            equipment = self.env['equipment.item'].browse(assignment.equipment_id.id)
            equipment.status = 'assigned'
        return assignment

    def write(self, vals):
        res = super(EquipmentAssignment, self).write(vals)
        if 'state' in vals:
            if vals['state'] == 'active':
                equipment = self.env['equipment.item'].browse(self.equipment_id.id)
                equipment.status = 'assigned'
            elif vals['state'] == 'returned':
                equipment = self.env['equipment.item'].browse(self.equipment_id.id)
                equipment.status = 'available'
        return res

from odoo import models, fields


class EquipmentLog(models.Model):
    _name = 'equipment.log'
    _description = 'Equipment Log'
    _order = 'date desc, id desc'

    date = fields.Datetime(string='Date', default=fields.Datetime.now, required=True, index=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, index=True)
    log_type = fields.Selection([
        ('equipment', 'Equipment'),
        ('assignment', 'Assignment'),
    ], string='Type', required=True, index=True)
    action = fields.Selection([
        ('created', 'Created'),
        ('confirmed', 'Confirmed'),
        ('returned', 'Returned'),
        ('reset', 'Reset'),
        ('status_change', 'Status Change'),
    ], string='Action', required=True)
    equipment_id = fields.Many2one('equipment.item', string='Equipment', index=True)
    assignment_id = fields.Many2one('equipment.assignment', string='Assignment', index=True)
    description = fields.Text(string='Description')

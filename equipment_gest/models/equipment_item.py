from odoo import models, fields, api


class EquipmentItem(models.Model):
    _name = 'equipment.item'
    _description = 'Equipment Item'
    _order = 'name'

    _sql_constraints = [
        ('serial_no_unique', 'UNIQUE(serial_no)', 'Serial number must be unique.'),
    ]

    name = fields.Char(string='Name', required=True, index=True)
    image = fields.Image(string='Image', max_width=1024, max_height=1024)
    serial_no = fields.Char(string='Serial Number', required=True, index=True)
    category_id = fields.Many2one('equipment.category', string='Category', index=True)
    status = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'Under Maintenance'),
    ], string='Status', default='available', required=True, index=True)
    notes = fields.Text(string='Notes')
    assignment_ids = fields.One2many('equipment.assignment', 'equipment_id', string='Assignment History')

    # Computed: who currently has this equipment
    assigned_to_id = fields.Many2one('hr.employee', string='Assigned To', compute='_compute_assigned_to', store=True)

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            domain = ['|', ('name', operator, name), ('serial_no', operator, name)] + domain
        return self._search(domain, limit=limit, order=order)

    @api.depends('assignment_ids.state', 'assignment_ids.employee_id')
    def _compute_assigned_to(self):
        for record in self:
            active = self.env['equipment.assignment'].search([
                ('equipment_id', '=', record.id),
                ('state', '=', 'active'),
            ], limit=1)
            record.assigned_to_id = active.employee_id.id if active else False

    def action_set_available(self):
        for record in self:
            record.status = 'available'
            self.env['equipment.log'].sudo().create({
                'log_type': 'equipment',
                'action': 'status_change',
                'equipment_id': record.id,
                'description': 'Status changed to Available',
            })

    def action_set_maintenance(self):
        for record in self:
            record.status = 'maintenance'
            self.env['equipment.log'].sudo().create({
                'log_type': 'equipment',
                'action': 'status_change',
                'equipment_id': record.id,
                'description': 'Status changed to Under Maintenance',
            })

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            self.env['equipment.log'].sudo().create({
                'log_type': 'equipment',
                'action': 'created',
                'equipment_id': record.id,
                'description': 'Equipment "%s" (S/N: %s) registered' % (record.name, record.serial_no),
            })
        return records

    def action_save_and_close(self):
        self.ensure_one()
        return self.env.ref('equipment_gest.action_equipment_item').read()[0]

    def action_open_assign_wizard(self):
        self.ensure_one()
        return {
            'name': 'Assign Equipment',
            'type': 'ir.actions.act_window',
            'res_model': 'equipment.quick.assignment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_equipment_id': self.id},
        }


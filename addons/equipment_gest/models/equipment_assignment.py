from odoo import api, models, fields
from odoo.exceptions import ValidationError


class EquipmentAssignment(models.Model):
    _name = 'equipment.assignment'
    _description = 'Equipment Assignment'
    _order = 'date_assigned desc'

    # Core fields
    equipment_id = fields.Many2one('equipment.item', string='Equipment', required=True, index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, index=True)
    date_assigned = fields.Date(string='Assigned On', default=fields.Date.today, required=True, index=True)
    date_returned = fields.Date(string='Returned On')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('returned', 'Returned'),
    ], string='State', default='draft', required=True, index=True)

    # Optional detail fields
    department_id = fields.Many2one('hr.department', string='Department')
    location = fields.Char(string='Location')
    purpose = fields.Char(string='Purpose')
    condition_on_assign = fields.Selection([
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ], string='Condition at Assignment')
    condition_on_return = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged'),
    ], string='Condition at Return')
    notes = fields.Text(string='Notes')

    @api.constrains('equipment_id', 'state')
    def _check_one_active_assignment(self):
        """Ensure each equipment has at most one active assignment at a time."""
        for record in self:
            if record.state == 'active':
                existing = self.search_count([
                    ('equipment_id', '=', record.equipment_id.id),
                    ('state', '=', 'active'),
                    ('id', '!=', record.id),
                ])
                if existing:
                    raise ValidationError(
                        'Equipment "%s" is already assigned. '
                        'Return it first before creating a new assignment.'
                        % record.equipment_id.name
                    )

    def action_confirm(self):
        for record in self:
            if record.equipment_id.status != 'available':
                raise ValidationError(
                    'Equipment "%s" is not available (current status: %s). '
                    'It must be available before assignment.'
                    % (record.equipment_id.name, record.equipment_id.status)
                )
            record.state = 'active'
            record.equipment_id.status = 'assigned'
            self.env['equipment.log'].sudo().create({
                'log_type': 'assignment',
                'action': 'confirmed',
                'equipment_id': record.equipment_id.id,
                'assignment_id': record.id,
                'description': 'Equipment "%s" assigned to %s' % (
                    record.equipment_id.name, record.employee_id.name),
            })

    def action_return(self):
        for record in self:
            record.state = 'returned'
            record.date_returned = fields.Date.today()
            record.equipment_id.status = 'available'
            self.env['equipment.log'].sudo().create({
                'log_type': 'assignment',
                'action': 'returned',
                'equipment_id': record.equipment_id.id,
                'assignment_id': record.id,
                'description': 'Equipment "%s" returned by %s' % (
                    record.equipment_id.name, record.employee_id.name),
            })

    def action_reset_draft(self):
        for record in self:
            record.state = 'draft'
            self.env['equipment.log'].sudo().create({
                'log_type': 'assignment',
                'action': 'reset',
                'equipment_id': record.equipment_id.id,
                'assignment_id': record.id,
                'description': 'Assignment reset to draft',
            })

    @api.model
    def create(self, vals):
        record = super().create(vals)
        self.env['equipment.log'].sudo().create({
            'log_type': 'assignment',
            'action': 'created',
            'equipment_id': record.equipment_id.id,
            'assignment_id': record.id,
            'description': 'Assignment created: "%s" for %s' % (
                record.equipment_id.name, record.employee_id.name),
        })
        return record

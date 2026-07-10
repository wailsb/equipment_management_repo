from odoo import models, fields, api


class EquipmentQuickAssignmentWizard(models.TransientModel):
    _name = 'equipment.quick.assignment.wizard'
    _description = 'Quick Assign Equipment'

    equipment_id = fields.Many2one('equipment.item', string='Equipment', required=True, readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Assign To Employee', required=True, index=True)
    date_assigned = fields.Date(string='Assigned On', default=fields.Date.today, required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    location = fields.Char(string='Location')
    purpose = fields.Char(string='Purpose')
    condition_on_assign = fields.Selection([
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ], string='Condition at Assignment', default='good')
    notes = fields.Text(string='Notes')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id and 'equipment_id' in fields_list:
            res['equipment_id'] = active_id
            # Auto-fill department if employee has one? We will let user pick or compute it when employee is selected.
        return res

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id.id

    def action_assign(self):
        self.ensure_one()
        # Create assignment
        assignment = self.env['equipment.assignment'].create({
            'equipment_id': self.equipment_id.id,
            'employee_id': self.employee_id.id,
            'date_assigned': self.date_assigned,
            'department_id': self.department_id.id,
            'location': self.location,
            'purpose': self.purpose,
            'condition_on_assign': self.condition_on_assign,
            'notes': self.notes,
        })
        # Confirm the assignment (sets state to active and equipment to assigned)
        assignment.action_confirm()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Equipment Assigned',
                'message': 'Successfully assigned to %s.' % self.employee_id.name,
                'sticky': False,
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

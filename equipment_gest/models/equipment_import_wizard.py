import base64
import csv
import io
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EquipmentImportWizard(models.Model):
    _name = 'equipment.import.wizard'
    _description = 'Import Equipment from Spreadsheet'

    import_type = fields.Selection([
        ('category', 'Categories'),
        ('equipment', 'Equipment Items'),
        ('assignment', 'Assignments'),
    ], string='Import Type', required=True, default='equipment')
    
    file = fields.Binary(string='Spreadsheet File (CSV)', required=True)
    filename = fields.Char(string='Filename')

    def action_import(self):
        self.ensure_one()
        if not self.file:
            raise ValidationError("Please upload a file.")

        # Decode the file
        try:
            csv_data = base64.b64decode(self.file)
            # Try to decode as utf-8-sig (handles Excel BOM) or fallback to latin-1
            try:
                decoded_data = csv_data.decode('utf-8-sig')
            except UnicodeDecodeError:
                decoded_data = csv_data.decode('latin-1')
        except Exception as e:
            raise ValidationError("Failed to read file. Make sure it is a valid CSV file.\nError: %s" % str(e))

        # Detect delimiter (comma or semicolon)
        delimiter = ','
        if decoded_data:
            first_line = decoded_data.split('\n')[0]
            if ';' in first_line and first_line.count(';') > first_line.count(','):
                delimiter = ';'

        f = io.StringIO(decoded_data)
        reader = csv.DictReader(f, delimiter=delimiter)

        # Normalize field names (strip whitespace and convert to lowercase)
        if reader.fieldnames:
            reader.fieldnames = [field.strip().lower() for field in reader.fieldnames]
        else:
            raise ValidationError("The CSV file is empty or has no header row.")

        created_count = 0
        row_idx = 1  # 1-indexed for header row

        try:
            if self.import_type == 'category':
                created_count = self._import_categories(reader)
            elif self.import_type == 'equipment':
                created_count = self._import_equipment(reader)
            elif self.import_type == 'assignment':
                created_count = self._import_assignments(reader)
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError("Error parsing CSV at row %d:\n%s" % (row_idx, str(e)))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Import Completed',
                'message': 'Successfully imported %d records.' % created_count,
                'sticky': False,
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def _import_categories(self, reader):
        created = 0
        for row in reader:
            name = row.get('name', '').strip() or row.get('category name', '').strip()
            if not name:
                continue
            
            # Check if category already exists
            existing = self.env['equipment.category'].search([('name', '=ilike', name)], limit=1)
            if not existing:
                self.env['equipment.category'].create({'name': name})
                created += 1
        return created

    def _import_equipment(self, reader):
        created = 0
        for row in reader:
            name = row.get('name', '').strip() or row.get('equipment name', '').strip()
            serial_no = row.get('serial_no', '').strip() or row.get('serial number', '').strip()
            category_name = row.get('category', '').strip()
            status = row.get('status', '').strip().lower() or 'available'
            notes = row.get('notes', '').strip()

            if not name or not serial_no:
                continue

            # Check if serial number already exists
            existing_sn = self.env['equipment.item'].search([('serial_no', '=', serial_no)], limit=1)
            if existing_sn:
                raise ValidationError("Serial Number '%s' already exists in the system." % serial_no)

            # Find or create category if specified
            category_id = False
            if category_name:
                category = self.env['equipment.category'].search([('name', '=ilike', category_name)], limit=1)
                if not category:
                    category = self.env['equipment.category'].create({'name': category_name})
                category_id = category.id

            # Create the item
            self.env['equipment.item'].create({
                'name': name,
                'serial_no': serial_no,
                'category_id': category_id,
                'status': status if status in ['available', 'assigned', 'maintenance'] else 'available',
                'notes': notes,
            })
            created += 1
        return created

    def _import_assignments(self, reader):
        created = 0
        for row in reader:
            serial_no = row.get('equipment_serial', '').strip() or row.get('serial number', '').strip()
            employee_name = row.get('employee', '').strip() or row.get('employee name', '').strip()
            date_assigned_str = row.get('date_assigned', '').strip()
            date_returned_str = row.get('date_returned', '').strip()
            state = row.get('state', '').strip().lower() or 'draft'
            notes = row.get('notes', '').strip()

            if not serial_no or not employee_name:
                continue

            # Find equipment by serial number
            equipment = self.env['equipment.item'].search([('serial_no', '=', serial_no)], limit=1)
            if not equipment:
                raise ValidationError("Equipment with serial number '%s' not found." % serial_no)

            # Find employee by name
            employee = self.env['hr.employee'].search([('name', '=ilike', employee_name)], limit=1)
            if not employee:
                # Try creating a minimal employee or raise error? Standard is to raise error since HR records are important.
                raise ValidationError("Employee '%s' not found. Please create the employee first." % employee_name)

            vals = {
                'equipment_id': equipment.id,
                'employee_id': employee.id,
                'state': state if state in ['draft', 'active', 'returned'] else 'draft',
                'notes': notes,
            }
            if date_assigned_str:
                vals['date_assigned'] = date_assigned_str
            if date_returned_str and state == 'returned':
                vals['date_returned'] = date_returned_str

            # Create assignment
            self.env['equipment.assignment'].create(vals)
            created += 1
        return created

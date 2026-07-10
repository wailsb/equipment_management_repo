# Enterprise Equipment Management - Odoo 17

an odoo 17 module built to solve a real problem : tracking which employee has what equipment, when it was given, when it comes back, and keeping a clean history of everything

companies that rely on spreadsheets and emails to track equipment end up with the same issues, no one knows who has what, equipment disappears or shows as unavailable when its actually sitting in a drawer, and managers have zero visibility

this module fixes that by bringing equipment management directly into odoo where it belongs

## what it does

- register equipment items with name, serial number, category and optional image
- assign equipment to employees with full workflow (draft, active, returned)
- track assignment history per equipment so you always know who had what and when
- categories to organize equipment by type (laptops, phones, tools, etc) each item has a unique serial number
- automatic status management, when you confirm an assignment the equipment status updates to assigned, when its returned it goes back to available
- full audit log system, every creation, assignment, return and status change is recorded with timestamp and user

## architecture

```
equipment_gest/
    models/
        equipment_item.py       # core equipment model with image support
        equipment_category.py   # equipment type grouping
        equipment_assignment.py # assignment workflow with constraints
        equipment_log.py        # immutable audit log
    views/
        equipment_views.xml     # tree, kanban, form, search
        assignment_views.xml    # assignment workflow views
        category_views.xml      # category management
        log_views.xml           # history views filtered by type
        menu.xml                # role-based navigation
    security/
        equipment_security.xml  # groups definition
        ir.model.access.csv     # permission matrix
```

depends on `base` and `hr`

## data model

one equipment can only be assigned to one employee at a time, enforced by a constraint that blocks activating a second assignment on the same item

one employee can hold multiple equipment items

each equipment item has a unique serial number enforced at database level

categories group equipment by type, a category like "macbook pro" can have hundreds of individual items each with their own serial number

the `assigned_to_id` field on equipment is a stored computed field that always reflects the current holder, this makes filtering and searching by assignee fast even with large datasets

## access management

two roles :

**operational user** - the people doing daily work, they can view equipment, create and manage assignments, but cannot modify equipment records or categories directly, they also cannot delete assignments

**manager** - full control over everything including equipment registration, category management and access to the history/log section

menus adapt to the user role, managers see equipment, assignments, categories and history, operational users see equipment and assignments only

## built for scale

the module is designed to handle tens of thousands of equipment items and a growing volume of historical data

- database indexes on every frequently queried field (name, serial_no, category_id, status, employee_id, state, date_assigned, log_type)
- stored computed fields for assigned_to_id so filtering by current holder doesnt require joins at query time
- ordered default views (equipment by name, assignments by date desc, logs by date desc)
- search views with smart filters, you can search equipment by name or serial number in a single search bar

## features summary

- equipment registration with image, serial number, category
- assignment workflow with confirm / return / reset actions
- optional assignment details : department, location, purpose, condition at assign and return
- assignment history visible directly on the equipment form
- kanban view grouped by status for quick availability overview
- full audit log divided by type (equipment logs, assignment logs)
- role-based menus and permissions
- unique serial number constraint
- one active assignment per equipment constraint

## setup

### local development

```bash
docker compose up -d
```

the module auto-installs via the docker-compose command, navigate to `http://localhost:8069`

### odoo.sh / hosting

the module sits at the repository root as required by the odoo app store and hosting platforms

## license

LGPL-3

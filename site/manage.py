from app import create_app
from flask_script import Manager
import database as db
import importlib

from modules.account.models import Account, PasswordReset
from modules.donations.models import Donation
from modules.security.models import Permission
from modules.volunteer.models import Volunteer, LoggedHours

manager = Manager(create_app)
manager.add_option('-e', '--environment', dest='environment', required=True)

@manager.shell
def shell_ctx():
    return dict(db=db)

@manager.command
def sync_volunteers():
    """Fix any Volunteers where local names differ from account names"""
    volunteers = db.Volunteer.select().where(db.Volunteer.account != None)
    print("Syncing {} volunteer(s)".format(volunteers.count()))
    for volunteer in volunteers:
        print(volunteer.full_name)
        volunteer.local_first_name = volunteer.account.first_name
        volunteer.local_last_name = volunteer.account.last_name
        volunteer.save()

@manager.command
def create_db():
    """Create tables in the database"""
    tables = [Account, PasswordReset, Donation, Permission, Volunteer, LoggedHours]
    for table in tables:
        if table.table_exists():
            print("Table already exists for {}".format(table))
        else:
            table.create_table()
            print("Created table for {}".format(table))

@manager.command
def migrate(migration):
    """Run a migration"""
    importlib.import_module("migrations.{}".format(migration)).migrate(db.database)

if __name__ == '__main__':
    manager.run()

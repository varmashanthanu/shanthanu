from shanthanu_micro import db
from shanthanu_micro.models import User


def create_admin():
    print('Trying to create admin user...')
    user = User()
    user.username = 'admin'
    user.set_password('admin')
    db.session.add(user)
    db.session.commit()
    print('Created admin user.')

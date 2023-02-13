from flask_sqlalchemy import SQLAlchemy as Sql
from flask_login import LoginManager
from flask import Flask

app = Flask(__name__)
login = LoginManager(app)
login.login_view = 'login'
app.config.from_object('config')
db = Sql(app)

from shanthanu_micro import routes
# if __name__ == '__main__':
#     app.run()

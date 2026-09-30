from flask import Flask
from backend.database import db 
app = None

def create_app():
    app = Flask(__name__) #create app
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.sqlite3'
    db.init_app(app) #connection between db and app
    app.app_context().push() #gives app context to database so that it know for which app the database is working
    return app

app = create_app()
from backend.controllers import *  
if __name__ == '__main__':
    db.create_all() #creates table based on your model
    admin = User.query.filter_by(username='admin123').first()
    if not admin:
        admin = User(username="admin123", email="admin@user.com", password="1234", role="Admin")
        db.session.add(admin)
        db.session.commit()
    app.run()



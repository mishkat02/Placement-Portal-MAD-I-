from .database import db
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(),nullable=False,unique =True)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(),nullable=False,default="Student") 
    is_blacklisted = db.Column(db.Boolean, default=False)

    student = db.relationship('Student', backref='user', uselist=False,cascade="all,delete",lazy=True)
    company = db.relationship('Company', backref='user', uselist=False, cascade='all,delete',lazy=True)

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer(), primary_key=True)
    student_name = db.Column(db.String(),nullable=False)
    skills = db.Column(db.Text(),nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False, unique=True)
    resume = db.Column(db.Text())
    contact_info = db.Column(db.String())
    
    application = db.relationship('Application', backref='student', lazy=True)
class Company(db.Model):
    __tablename__ = 'company'
    company_id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False, unique=True)
    company_name = db.Column(db.String(),nullable=False)
    hr_contact = db.Column(db.String())
    website = db.Column(db.String())
    approval_status = db.Column(db.String, default="Pending")

    drives = db.relationship('PlacementDrive', backref='company', lazy=True, cascade='all,delete')

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drive'
    drive_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.Text)
    application_deadline = db.Column(db.String, nullable=False)
    drive_status = db.Column(db.String(20), default="Pending")  #Pending/Approved/Rejected

    applications = db.relationship('Application', backref='drive', lazy=True, cascade='all,delete')

class Application(db.Model):
    __tablename__ = 'application'
    application_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.drive_id'), nullable=False)
    application_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    application_status = db.Column(db.String(20),default="Applied")  # Applied/Shortlisted/Selected/Rejected


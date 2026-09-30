from flask import render_template, redirect, request, url_for
from flask import current_app as app
from .models import *
from .database import db


@app.route("/",methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        password = request.form.get("Password")
        username = request.form.get("Username")
        user = User.query.filter_by(password = password, username = username).first()
        if user and user.role == 'Admin':
            return redirect(url_for("admin", username = username))
        elif user and user.role == 'Student' and user.is_blacklisted == False:
            return redirect(url_for("student", username = username))
        elif user and user.role == 'Company' and user.is_blacklisted == False and user.company.approval_status == 'Approved':
            return redirect(url_for("company", username = username))
        else:
            return render_template("login.html")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("Username")
        password = request.form.get("Password")
        email = request.form.get("Email")
        college = request.form.get("College")
        role = request.form.get("Role")
        user = User.query.filter_by(username = username).first()
        if user:
            if len(password) < 5 or password.isdigit():
                return render_template("register.html", msg="Password must be at least 5 chars and alphanumeric!")
            return render_template("register.html", msg= "User already exists !!")
        newuser = User(email = email, password = password, username = username, role=role)
        db.session.add(newuser)
        db.session.commit()
        if role == 'Student':
            new_student = Student(user_id=newuser.id, student_name=username, skills="")
            db.session.add(new_student)
        elif role == 'Company':
            new_company = Company(user_id=newuser.id, company_name=username)
            db.session.add(new_company)
        db.session.commit()
        return render_template("login.html", msg = "You can login and continue")
    return render_template("register.html")


#ADMIN
@app.route("/admin/<username>", methods=["GET","POST"])
def admin(username):
    query = request.form.get("search_query","").strip()
    pattern = f"%{query}%"

    student_results = Student.query.filter(Student.student_name.ilike(pattern)).all()
    
    company_results = Company.query.filter(Company.company_name.ilike(pattern)).all()
    
    stats = {
        "total_students" : Student.query.count(),
        "total_company" : Company.query.count(),
        "total_drives" : PlacementDrive.query.count(),
        "total_applications" : Application.query.count()
    }

    registered_students = Student.query.all()
    all_drives = PlacementDrive.query.all()
    pending_drives = PlacementDrive.query.filter_by(drive_status = 'Pending').all()
    closed_drives = PlacementDrive.query.filter_by(drive_status ='Closed').all()
    all_applications = Application.query.all()
    approved_companies = Company.query.filter_by(approval_status ='Approved').all()
    pending_companies = Company.query.filter_by(approval_status = 'Pending').all()
    return render_template("admin.html", username = username,stats=stats,registered_students=registered_students,
                           approved_companies=approved_companies,pending_companies=pending_companies,
                           all_drives=all_drives, all_applications=all_applications,query=query,
                           results_s=student_results,results_c=company_results,closed_drives=closed_drives,
                           pending_drives=pending_drives)

@app.route("/admin/approve_company/<int:company_id>")
def approve_company(company_id):
    company = Company.query.get(company_id)
    if company:
        company.approval_status = 'Approved'
        for drive in company.drives:
            drive.drive_status = 'Approved'
        db.session.commit()
    return redirect(url_for('admin', username="admin123"))

@app.route("/admin/reject_company/<int:company_id>")
def reject_company(company_id):
    company = Company.query.get(company_id)
    if company:
        company.approval_status = 'Rejected'
        for drive in company.drives:
            drive.drive_status = 'Cancelled'
        db.session.commit()
    return redirect(url_for('admin', username = "admin123"))

@app.route("/admin/blacklist_student/<int:user_id>")
def blacklist_student(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_blacklisted = not user.is_blacklisted
        db.session.commit()
    return redirect(url_for('admin', username = "admin123"))


@app.route("/admin/blacklist_company/<int:user_id>")
def blacklist_company(user_id):
    user = User.query.get(user_id)
    if user and user.role == 'Company':
        user.is_blacklisted = not user.is_blacklisted
        comp_profile = user.company
        if user.is_blacklisted and comp_profile:
            for drive in comp_profile.drives:
                drive.drive_status = 'Cancelled'

        db.session.commit()
    return redirect(url_for('admin', username="admin123"))

@app.route("/admin/approve_drive/<int:drive_id>")
def approve_drive(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    if drive:
        drive.drive_status = 'Approved'
        db.session.commit()
    return redirect(url_for('admin', username="admin123"))

@app.route("/admin/reject_drive/<int:drive_id>")
def reject_drive(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    if drive:
        drive.drive_status = 'Rejected'
        db.session.commit()
    return redirect(url_for('admin', username="admin123"))

#-----------------------------------------------------------------------------
#STUDENT ROUTES
#-----------------------------------------------------------------------------

@app.route("/student/<username>", methods=["GET","POST"])
def student(username):
    user = User.query.filter_by(username=username).first()
    student_profile = user.student
    current_drives = PlacementDrive.query.filter_by(drive_status ='Approved').all()
    applied_drives = student_profile.application
    return render_template("student.html", username = username,current_drives=current_drives,
                           applied_drives=applied_drives,student=student_profile)

@app.route("/edit_student/<username>", methods=["GET","POST"])
def edit_student(username):
    user = User.query.filter_by(username = username).first()
    if not user:
        return "User not found", 404
    
    student = user.student
    if request.method == "POST":
        student.student_name = request.form.get("Student_name")
        student.skills = request.form.get("Skills")
        student.resume = request.form.get("Resume")
        student.college = request.form.get("College")
        student.contact_info = request.form.get("Contact_info")
        db.session.commit()
        return redirect(url_for("student", username = username))
    return render_template("edit_student.html", student = student, username = username, user = user)
 
@app.route("/apply/<username>/<int:drive_id>")
def apply(username,drive_id):
    user = User.query.filter_by(username=username).first()
    student_profile = user.student
    existing_app = Application.query.filter_by(student_id=student_profile.student_id,
                                               drive_id=drive_id).all()
    if not existing_app:
        new_app = Application(student_id=student_profile.student_id,
                              drive_id=drive_id, application_status='Applied')
        db.session.add(new_app)
        db.session.commit()
    return redirect(url_for('student', username=username))

@app.route("/student_history/<username>")
def student_history(username):
    user = User.query.filter_by(username=username).first()
    student = user.student
    history = student.application
    return render_template('student_history.html',username=username,history=history,student=student)

@app.route("/drive_details/<int:drive_id>")
def drive_details(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return "Drive not found",404
    return render_template('drive_details.html',drive=drive)

#-----------------------------------------------------------------------------
# COMPANY ROUTES
#-----------------------------------------------------------------------------
@app.route("/company/<username>", methods=["GET","POST"])
def company(username):
    user = User.query.filter_by(username=username).first()
    if not user or user.role !='Company' or user.company.approval_status != 'Approved':
        return redirect(url_for('login'))
    company_profile = user.company
    upcoming_drives = PlacementDrive.query.filter_by(company_id=company_profile.company_id, drive_status='Approved').all()
    closed_drives = PlacementDrive.query.filter_by(company_id=company_profile.company_id, drive_status='Closed').all()
    pending_drives = PlacementDrive.query.filter_by(company_id=company_profile.company_id, drive_status='Pending').all()

    return render_template("company.html", username=username, company=company_profile,
                           upcoming_drives=upcoming_drives,closed_drives=closed_drives,
                           pending_drives=pending_drives)

@app.route("/edit_company/<username>", methods=['GET','POST'])
def edit_company(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return "User not found", 404
    company = user.company
    if request.method == "POST":
        company.company_name = request.form.get("company_name")
        company.hr_contact = request.form.get("hr_contact")
        company.website = request.form.get("website")
        db.session.commit()
        return redirect(url_for("company", username=username))
    
    return render_template("edit_company.html", company=company, username=username, user=user)

@app.route("/company/<username>/create_drive", methods=['GET','POST'])
def create_drive(username):
    user = User.query.filter_by(username=username).first()
    company_profile = user.company
    if request.method == 'POST':
        new_drive = PlacementDrive(
            company_id = company_profile.company_id,
            job_title = request.form.get('job_title'),
            job_description = request.form.get('job_description'),
            eligibility_criteria = request.form.get('eligibility_criteria'),
            application_deadline = request.form.get('application_deadline'),
            drive_status = 'Pending'
        )
        db.session.add(new_drive)
        db.session.commit()
        return redirect(url_for('company', username=username))
    return render_template("create_drive.html", username=username)

@app.route('/company/<username>/edit_drive/<int:drive_id>', methods=['GET','POST'])
def edit_drive(username, drive_id):
    drive = PlacementDrive.query.get(drive_id)
    username = drive.company.user.username
    if request.method == 'POST':
        drive.job_title = request.form.get("job_title")
        drive.job_description = request.form.get("job_description")
        drive.eligibility_criteria = request.form.get("eligibility_criteria")
        drive.application_deadline = request.form.get("application_deadline")
        drive.drive_status = 'Pending'
        db.session.commit()
        return redirect(url_for('company', username=username))
    return render_template("edit_drive.html",drive=drive,username=username)

@app.route('/company/close_drive/<int:drive_id>')
def close_drive(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    if drive:
        drive.drive_status = 'Closed'
        db.session.commit()
        username = drive.company.user.username
        return redirect(url_for('company', username=username))
    
@app.route('/company/view_application/<int:drive_id>')
def view_application(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return "Drive not found", 404
    apps = Application.query.filter_by(drive_id=drive_id).all()
    username = drive.company.user.username
    return render_template("applicants_list.html", drive=drive,apps=apps,username=username)

@app.route('/company/update_status/<int:app_id>/<string:new_status>')
def update_status(app_id, new_status):
    application = Application.query.get(app_id)
    if not application:
        return "Application not found", 404
    application.application_status = new_status
    db.session.commit()
    return redirect(url_for('view_application', drive_id=application.drive_id))

@app.route('/company/view_single_application/<int:app_id>')
def view_single_application(app_id):
    application = Application.query.get(app_id)
    if application:
        student = application.student
        drive = application.drive
        username = drive.company.user.username
        return render_template("applicants_profile.html", student=student, 
                               application=application, username=username)
    return "Application not found", 404

@app.route('/drive_history/<int:drive_id>')
def drive_history(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return "Drive not found",404
    apps= drive.applications
    return render_template('drive_history.html',drive=drive,applications=apps)



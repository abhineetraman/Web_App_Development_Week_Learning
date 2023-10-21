from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///week7_database.sqlite3'
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    roll_number = db.Column(db.String, unique = True, nullable = False)
    first_name = db.Column(db.String, nullable = False)
    last_name = db.Column(db.String)
    courses = db.relationship("Course", secondary = "enrollments")


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    course_code = db.Column(db.String, unique = True, nullable = False)
    course_name = db.Column(db.String, nullable = False)
    course_description = db.Column(db.String)
    students = db.relationship("Student", secondary = "enrollments")


class Enrollments(db.Model):
    __tablename__ = "enrollments"
    enrollment_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    estudent_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), nullable = False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), nullable = False)

@app.route('/')
def index():
    if request.method == "GET":
        students = Student.query.all()
        if len(students) ==0:
            return render_template("nostudent.html")
        return render_template("index.html",students = students)


@app.route('/courses')
def course_index():
    if request.method == "GET":
        courses = Course.query.all()
        print(courses)
        if len(courses) == 0:
            return render_template("nocourses.html")
        return render_template("index_course.html", courses = courses)


@app.route('/student/create',methods = ['GET','POST'])
def addstu():
    if request.method=="GET":
        return render_template("addstu.html")
    else:
        temp = Student.query.filter_by(roll_number = request.form["roll"]).first()
        if temp is None:
            stu = Student(roll_number = request.form["roll"],first_name = request.form["f_name"],last_name = request.form["l_name"])
            db.session.add(stu)
            db.session.commit()
            return redirect("/")
        else:
            return render_template("rollexists.html")

@app.route('/course/create',methods = ['GET','POST'])
def addcourse():
    if request.method=="GET":
        return render_template("addcourse.html")
    else:
        temp = Course.query.filter_by(course_code = request.form["code"]).first()
        if temp is None:
            course = Course(course_code = request.form["code"], course_name = request.form["c_name"], course_description = request.form["desc"])
            db.session.add(course)
            db.session.commit()
            return redirect("/courses")
        else:
            return render_template("courseexists.html")


@app.route('/student/<int:studentid>/update',methods = ["GET","POST"])
def upda(studentid):
    if request.method == "GET":
        stud = Student.query.filter_by(student_id = studentid).one()
        curs = Course.query.all()
        return render_template("update.html",stud = stud, curs=curs)
    else:
        temp = Enrollments.query.filter_by(estudent_id = studentid).first()
        if temp is not None:
            enroll = Enrollments.query.filter_by(estudent_id = studentid).all()
            for enrollment in enroll:
                db.session.delete(enrollment)
        studa = Student.query.filter_by(student_id = studentid).one()
        studa.first_name = request.form["f_name"]
        studa.last_name = request.form["l_name"]
        course=request.form.__getitem__("course")
        for i in range(len(course)):
            if course[i] == str(Course.course_id):
                studa.courses.append(Course.query.filter_by(course_id=course[i]).one())
        db.session.commit()
        return redirect("/")


@app.route('/course/<int:courseid>/update',methods = ["GET","POST"])
def update_course(courseid):
    if request.method == "GET":
        cur = Course.query.filter_by(course_id = courseid).one()
        return render_template("update_course.html", cur = cur)
    else:
        temp = Enrollments.query.filter_by(ecourse_id = courseid).first()
        if temp is not None:
            enroll = Enrollments.query.filter_by(ecourse_id = courseid).all()
            for enrollment in enroll:
                db.session.delete(enrollment)
        curs = Course.query.filter_by(course_id = courseid).one()
        curs.course_name = request.form["c_name"]
        curs.course_description = request.form["desc"]
        db.session.commit()
        return redirect("/courses")


@app.route('/student/<int:studentid>/delete')
def dele(studentid):
    temp = Enrollments.query.filter_by(estudent_id = studentid).first()
    if temp is not None:
        enroll = Enrollments.query.filter_by(estudent_id = studentid).all()
        for enrollment in enroll:
            db.session.delete(enrollment)
    studa = Student.query.filter_by(student_id = studentid).one()
    db.session.delete(studa)
    db.session.commit()
    return redirect("/")


@app.route('/course/<int:courseid>/delete')
def delete_course(courseid):
    temp = Enrollments.query.filter_by(ecourse_id = courseid).first()
    if temp is not None:
        enroll = Enrollments.query.filter_by(ecourse_id = courseid).all()
        for enrollment in enroll:
            db.session.delete(enrollment)
    curs = Course.query.filter_by(course_id = courseid).one()
    db.session.delete(curs)
    db.session.commit()
    return redirect("/courses")


@app.route('/student/<int:studentid>')
def show(studentid):
    stud = Student.query.filter_by(student_id = studentid).one()
    return render_template("show.html",stud = stud)


@app.route('/course/<int:courseid>')
def show_course(courseid):
    curs = Course.query.filter_by(course_id = courseid).one()
    return render_template("show_courses.html",curs = curs)


@app.route('/student/<int:studentid>/withdraw/<int:courseid>')
def withdraw(courseid, studentid):
    enroll = Enrollments.query.filter_by(ecourse_id=courseid , estudent_id = studentid).all()
    for enrollment in enroll:
        db.session.delete(enrollment)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run()
from flask import Flask,make_response,request, redirect, render_template
from flask_restful import Resource, Api
from flask_restful import fields, marshal_with
from flask_restful import reqparse
from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app
import werkzeug
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.exceptions import HTTPException
from flask import abort
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
db = SQLAlchemy()
#db.init_app(app)
app.app_context().push()
engine = None
Base = declarative_base()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "database.sqlite3")
    DEBUG = False


class SchemaValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        data = { "error_code" : error_code, "error_message": error_message }
        self.response = make_response(json.dumps(data), status_code)


class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        data = { "error_code" : error_code, "error_message": error_message }
        self.response = make_response(json.dumps(data), status_code)


class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)


class DuplicateValueError(HTTPException):
    def __init__(self,status_code):
        self.response=make_response('',status_code)


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
    #students = db.relationship("Student", secondary = "enrollments")


class Enrollments(db.Model):
    __tablename__ = "enrollments"
    enrollment_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    estudent_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), nullable = False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), nullable = False)




create_student_parser = reqparse.RequestParser()
create_student_parser.add_argument('first_name')
create_student_parser.add_argument('last_name')
create_student_parser.add_argument('roll_no')

create_course_parser = reqparse.RequestParser()
create_course_parser.add_argument('course_name')
create_course_parser.add_argument('course_code')
create_course_parser.add_argument('course_description')

create_enrollment_parser=reqparse.RequestParser()
create_enrollment_parser.add_argument('estudent_id')
create_enrollment_parser.add_argument('ecourse_id')

update_student_parser = reqparse.RequestParser()
update_student_parser.add_argument('first_name')
update_student_parser.add_argument('last_name')

update_course_parser = reqparse.RequestParser()
update_course_parser.add_argument('course_name')
update_course_parser.add_argument('course_description')

resource_fields1 = {
    'student_id':   fields.Integer,
    'first_name':   fields.String,
    'last_name':    fields.String,
    'roll_no':      fields.String
}

output_fields = {
    'course_id':   fields.Integer,
    'course_name': fields.String,
    'course_code': fields.String,
    'course_description': fields.String
}

output_fields1={
    "enrollment_id" : fields.Integer,
    "estudent_id" : fields.Integer,
    "ecourse_id" : fields.Integer
}


class StudentAPI(Resource):
    @marshal_with(output_fields)
    def get(self, student_id):
        # Get the student_id
        print("In StudentAPI GET Method")
        # Get the Student fromn the database based on student_id
        student = db.session.query(Student).filter(Student.student_id == student_id).first()

        if student:
            # Format the return JSON
            return student
        else:
            # Return 404 error
            raise NotFoundError(status_code=404)

    @marshal_with(output_fields)
    def put(self, student_id):
        args = update_student_parser.parse_args()
        student = db.session.query(Student).filter(Student.student_id == student_id).first()
        if student:
            # Format the return JSON
            return student

    def delete(self, student_id):
        # Check if the students exists
        student = db.session.query(Student).filter(Student.student_id == student_id).first()
        if student:
            # return a valid JSON file
            db.session.delete(student)
            db.session.commit()
            return "", 200
        else:
            raise NotFoundError(status_code=404)
            # If no dependency then delete

    @marshal_with(output_fields)
    def post(self):
        args = create_student_parser.parse_args()
        first_name = args.get("first_name", None)
        last_name = args.get("last_name", None)
        roll_number = args.get("roll_number", None)

        if roll_number is None:
            raise BusinessValidationError(status_code=400, error_code='STUDENT001',
                                          error_message='Roll Number is required and should be String')
        # else:
        #    if type(roll_number)!=type(test):
        #        raise BuisnessValidationError(status_code=400,error_code='STUDENT001',error_message='Roll Number is required and should be String')

        if first_name is None:
            raise BusinessValidationError(status_code=400, error_code='STUDENT002',
                                          error_message='First Name is required and should be String')
        # else:
        #    if type(first_name)!=type(test):
        #        raise BuisnessValidationError(status_code=400,error_code='STUDENT002',error_message='First Name is required and should be String')

        if last_name is not None:
            pass
        # else:
        #    if type(last_name)!=type(test):
        #        raise BuisnessValidationError(status_code=400,error_code='STUDENT003',error_message='Last Name is String')

        student = db.session.query(Student).filter(Student.roll_number == roll_number).first()

        if student:
            raise DuplicateValueError(status_code=409)

        new_student = Student(first_name=first_name, last_name=last_name, roll_number=roll_number)
        db.session.add(new_student)
        db.session.commit()
        new_student = db.session.query(Student).filter(Student.roll_number == roll_number).first()
        return new_student, 201


class CourseAPI(Resource):

    @marshal_with(output_fields)
    def get(self, course_id):
        # Get the course_id
        print("In CourseAPI GET Method")
        # Get the Course fromn the database based on course_id
        course = db.session.query(Course).filter(Course.course_id == course_id).first()

        if course:
            # Format the return JSON
            return course
        else:
            # Return 404 error
            raise NotFoundError(status_code=404)

    def put(self, course_id):
        args = update_course_parser.parse_args()
        return {'hello': 'world'}

    def delete(self, course_id):
        # Check if the students exists
        course = db.session.query(Course).filter(Course.course_id == course_id).first()
        if course:
            # return a valid JSON file
            db.session.delete(course)
            db.session.commit()
            return "", 200
        else:
            raise NotFoundError(status_code=404)
            # If no dependency then delete

    def post(self):
        args = create_course_parser.parse_args()
        course_name = args.get("course_name", None)
        course_code = args.get("course_code", None)
        course_description = args.get("course_description", None)

        if course_name is None:
            raise BusinessValidationError(status_code=400, error_code='COURSE001',
                                          error_message='Course Name is required and should be String')
        # else:
        #    if type(course_name)!=type(test):
        #        raise BuisnessValidationError(status_code=400,error_code='COURSE001',error_message='Course Name is required and should be String')

        if course_code is None:
            raise BusinessValidationError(status_code=400, error_code='COURSE002',
                                          error_message='Course Code is required and should be String')
        # else:
        #    if type(course_code)!=type(test):
        #        raise BuisnessValidationError(status_code=400,error_code='COURSE002',error_message='Course Code is required and should be String')

        if course_description is None:
            pass
        # else:
        #    if type(course_description)!=type(test):
        #        raise BuisnessValidationError(status_code=400,error_code='COURSE003',error_message='Course Description is String')

        course = db.session.query(Course).filter(Course.course_code == course_code).first()

        if course:
            raise DuplicateValueError(status_code=409)

        new_course = Course(course_name=course_name, course_code=course_code, course_description=course_description)
        db.session.add(new_course)
        db.session.commit()
        return "", 201


class EnrollmentAPI(Resource):

    @marshal_with(output_fields1)
    def get(self, estudent_id):
        # Get the student_id
        print("In EnrollmentAPI GET Method")
        # Get the Student fromn the database based on student_id
        enrollment=db.session.query(Enrollments).filter(Enrollments.estudent_id==estudent_id).first()

        if enrollment:
            # Format the return JSON
            return enrollment
        else:
            # Return 404 error
            raise NotFoundError(status_code=404)

    @marshal_with(output_fields1)
    def post(self,estudent_id):
        args=create_enrollment_parser.parse_args()
        ecourse_id=args.get("ecourse_id",None)
        #courses=db.session.query(Enrollments).filter_by(Enrollments.estudent_id==estudent_id).all()
        #if ecourse_id not in courses:
        #    raise BuisnessValidationError(status_code=400,error_code='ENROLLMENT001',error_message='Course does not exist.')

        student=db.session.query(Enrollments).filter(Enrollments.estudent_id==estudent_id).first()
        if student is None:
            raise BusinessValidationError(status_code=400,error_code='ENROLLMENT002',error_message='Student does not exist.')

        new_enrollment=Enrollments(estudent_id=estudent_id,ecourse_id=ecourse_id)
        db.session.add(new_enrollment)
        db.session.commit()
        new_enrollment=db.session.query(Enrollments).filter(Enrollments.estudent_id==estudent_id).first()
        return new_enrollment,201

    def delete(self,student_id,course_id):
        print("DELETE student_id & course_id",student_id,course_id)
        return {"student_id":student_id,"course_id":course_id,"action":"DELETE"}


@app.route('/')
def index():
    if request.method == "GET":
        students = Student.query.all()
        if len(students) ==0:
            return render_template("nostudent.html")
        return render_template("index.html",students = students)


@app.route('/student/create',methods = ['GET','POST'])
def addstu():
    if request.method=="GET":
        return render_template("addstu.html")
    else:
        temp = Student.query.filter_by(roll_number = request.form["roll"]).first()
        if temp is None:
            stu = Student(roll_number = request.form["roll"],first_name = request.form["f_name"],last_name = request.form["l_name"])
            courses_taken = request.form.getlist("courses")
            for cour in courses_taken:
                if cour=='course_1':
                    stu.courses.append(Course.query.filter_by(course_id = 1).one())
                elif cour=='course_2':
                    stu.courses.append(Course.query.filter_by(course_id = 2).one())
                elif cour == 'course_3':
                    stu.courses.append(Course.query.filter_by(course_id = 3).one())
                elif cour == 'course_4':
                    stu.courses.append(Course.query.filter_by(course_id = 4).one())
            db.session.add(stu)
            db.session.commit()
            return redirect("/")
        else:
            return render_template("rollexists.html")

@app.route('/student/<int:studentid>/update',methods = ["GET","POST"])
def upda(studentid):
    if request.method == "GET":
        stud = Student.query.filter_by(student_id = studentid).one()
        return render_template("update.html",stud = stud)
    else:
        temp = Enrollments.query.filter_by(estudent_id = studentid).first()
        if temp is not None:
            enroll = Enrollments.query.filter_by(estudent_id = studentid).all()
            for enrollment in enroll:
                db.session.delete(enrollment)
        studa = Student.query.filter_by(student_id = studentid).one()
        studa.first_name = request.form["f_name"]
        studa.last_name = request.form["l_name"]
        courses_taken = request.form.getlist("courses")
        for cour in courses_taken:
            if cour=='course_1':
                studa.courses.append(Course.query.filter_by(course_id = 1).one())
            elif cour=='course_2':
                studa.courses.append(Course.query.filter_by(course_id = 2).one())
            elif cour == 'course_3':
                studa.courses.append(Course.query.filter_by(course_id = 3).one())
            elif cour == 'course_4':
                studa.courses.append(Course.query.filter_by(course_id = 4).one())
        db.session.commit()
        return redirect("/")


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


@app.route('/student/<int:studentid>')
def show(studentid):
    stud = Student.query.filter_by(student_id = studentid).one()
    return render_template("show.html",stud = stud)


api=None


def create_app():
    app = Flask(__name__, template_folder="Templates")
    if os.getenv('ENV', "development") == "production":
      raise Exception("Currently no production config is setup.")
    else:
      print("Staring Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api = Api(app)
    app.app_context().push()
    return app, api


app, api = create_app()
api.add_resource(StudentAPI, "/api/student", "/api/course/<string:student_id>")
api.add_resource(CourseAPI, "/api/course", "/api/course/<string:course_id>")
api.add_resource(EnrollmentAPI, "/api/student/<string:student>/course", "/api/course/<string:student_id>/course/<string:course_id>",)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
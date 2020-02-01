from fuprox import db, ma
from datetime import datetime


# user DB model
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(48), unique=True, nullable=False)
    image_file = db.Column(db.String(200), nullable=False, default="default.jpg")
    password = db.Column(db.String(200),nullable=False)

    def __repr__(self):
        return f"User (' {self.id} '{self.email}' )"

    def __init__(self, email,password):
        self.email = email
        self.password = password

class CustomerSchema(ma.Schema):
    class Meta:
        fields = ("id", "email","password")


# creating a company class
class Company(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(length=50))
    service = db.Column(db.String(length=250))

    def __init__(self,name,service):
        self.name = name
        self.service = service

    def __repr__(self):
        return f"Company {self.name} -> {self.service}"


class CompanySchema(ma.Schema):
    class Meta:
        fields = ("id","name","service")


# creating a branch class
class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=100))
    company = db.Column(db.String(length=11))
    longitude = db.Column(db.String(length=50))
    latitude = db.Column(db.String(length=50))
    opens = db.Column(db.String(length=50))
    closes = db.Column(db.String(length=50))
    service = db.Column(db.String(length=50))
    description = db.Column(db.String(length=50))


    def __init__(self, name, company, longitude, latitude,opens,closes,service,description):
        self.name = name
        self.company = company
        self.longitude = longitude
        self.latitude = latitude
        self.opens = opens
        self.closes = closes
        self.service = service
        self.description = description


# creating branch Schema
class BranchSchema(ma.Schema):
    class Meta:
        fields = ('id','name','company','address','longitude','latitude','opens','closes','service','description')


# creating a user class
# creating a company class
class Service(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(length=50))
    service = db.Column(db.String(length=250))

    def __init__(self,name,service):
        self.name = name
        self.service = service

    def __repr__(self):
        return f"Company {self.name} -> {self.service}"


class ServiceSchema(ma.Schema):
    class Meta:
        fields = ("id","name","service")


# creating a booking ID
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(length=100))
    user_id = db.Column(db.Integer)
    start = db.Column(db.String(length=200))
    # ticket = db.Column(db.String(length=6),nullable=False)
    branch = db.Column(db.Integer)
    institution = db.Column(db.Integer)
    # check if the booking for the user exists from the current time then offer not booking

    def __init__(self,booking_id,user,start,branch,institution):
        self.booking_id = booking_id
        self.user_id = user
        self.start = start
        self.branch = branch
        self.institution = institution


class BookSchema(ma.Schema):
    class Meta:
        fields = ("id","booking_id","user_id","start","branch","institution")




class Help(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(length=100), nullable=False)
    title = db.Column(db.String(length=250), nullable=False)
    solution = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, topic, title, solution):
        self.topic = topic
        self.title = title
        self.solution = solution

class HelpSchema(ma.Schema):
    class Meta:
        fields = ("id","topic","title","solution","date_added")




# class Token(db.Model):
#     id = db.Column
#

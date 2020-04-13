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
        fields = ('id','name','company','address','longitude','latitude','opens','closes','service','description',"")


class Service(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(length=50))
    service = db.Column(db.String(length=250))
    is_medical = db.Column(db.Boolean,default=False)

    def __init__(self, name, service, is_medical):
        self.name = name
        self.service = service
        self.is_medical = is_medical


class ServiceSchema(ma.Schema):
    class Meta:
        fields = ("id","name","service","is_medical")


class OnlineBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    service_name = db.Column(db.String(length=100),nullable=True)
    start = db.Column(db.String(length=200))
    branch_id = db.Column(db.Integer)
    ticket = db.Column(db.String(length=6),nullable=False)
    date_added = db.Column(db.DateTime,default=datetime.now)
    active = db.Column(db.Boolean,default=False,nullable=False)
    next = db.Column(db.Boolean,nullable=False,default=False)
    serviced = db.Column(db.Boolean,nullable=False,default=False)
    teller = db.Column(db.String(200),nullable=False,default=000000)

    def __init__(self,service_name,user_id,start,branch_id,ticket,active,next,serviced,teller):
        self.user_id = user_id
        self.service_name = service_name
        self.start = start
        self.branch_id = branch_id
        self.ticket = ticket
        self.active = active
        self.next = next
        self.serviced = serviced
        self.teller = teller


class OnlineBookingSchema(ma.Schema):
    class Meta:
        fields = ("id","user_id","service_name","start","branch_id","ticket","active","next","serviced")


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



class ServiceOffered(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(length=50))
    teller = db.Column(db.String(100), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.now)
    # date_expires = db.Column(db.DateTime, nullable=False)
    code = db.Column(db.String(length=10), nullable=False)
    icon = db.Column(db.String(length=20))

    def __init__(self, name, branch_id, teller, code, icon):
        self.name = name
        self.branch_id = branch_id
        self.teller = teller
        self.code = code
        self.icon = icon


class ServiceOfferedSchema(ma.Schema):
    class Meta:
        fields = ("id", "branch_id", "name", "teller", "date_added", "code", "icon")


# creating a booking ID
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(length=100), nullable=True)
    start = db.Column(db.String(length=200))
    branch_id = db.Column(db.Integer)
    ticket = db.Column(db.String(length=6), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)
    active = db.Column(db.Boolean, default=False, nullable=False)
    nxt = db.Column(db.Boolean, nullable=False, default=False)
    serviced = db.Column(db.Boolean, nullable=False, default=False)
    teller = db.Column(db.String(200), nullable=False, default=000000)
    kind = db.Column(db.Integer, nullable=False)
    user = db.Column(db.Integer)
    is_instant = db.Column(db.Boolean, default=False)

    def __init__(self, service_name, start, branch_id, ticket, active, nxt, serviced, teller, kind, user,
                 instant):
        self.service_name = service_name
        self.start = start
        self.branch_id = branch_id
        self.ticket = ticket
        self.active = active
        self.nxt = nxt
        self.serviced = serviced
        self.teller = teller
        self.kind = kind
        self.user = user
        self.is_instant = instant


class BookingSchema(ma.Schema):
    class Meta:
        fields = ("id", "service_name", "start", "branch_id", "ticket", "active", "next", "serviced","teller",\
                  "kind","user","is_instant")


class Teller(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.now)
    branch = db.Column(db.Integer)
    service = db.Column(db.String(200))

    def __init__(self, number, branch, service):
        self.number = number
        self.branch = branch
        self.service = service


class TellerSchema(ma.Schema):
    class Meta:
        fields = ("id", "number", "date_added", "branch", "service")


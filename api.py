# from logging import exception

from flask import request,jsonify
from fuprox import db,app
from fuprox.models import (Customer, Branch, Book, CustomerSchema, BranchSchema, Service, ServiceSchema
                            , BookSchema, Company, CompanySchema, Help, HelpSchema, ServiceOffered, ServiceOfferedSchema,
                           OnlineBooking, OnlineBookingSchema)
import secrets
from fuprox import bcrypt

# from fuprox.utilities import user_exists
from fuprox.models import Customer,CustomerSchema
from fuprox import bcrypt
from fuprox.models import Customer,CustomerSchema
from fuprox import bcrypt
from sqlalchemy import desc,asc

# from fuprox.utilities import user_exists

# adding some product schemas
user_schema = CustomerSchema()
users_schema = CustomerSchema(many=True)

# branch schema

branch_schema = BranchSchema()
branches_schema = BranchSchema(many=True)

# service offered schema
service_offered_schema = ServiceOfferedSchema()
services_offered_schema = ServiceOfferedSchema(many=True)

# service schema
service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)

# service schema
book_schema = BookSchema()
books_schema = BookSchema(many=True)

booking_schema = OnlineBookingSchema()
bookings_schema = OnlineBookingSchema(many=True)

#getting companiy schema
company_schema = CompanySchema()
companies_schema = CompanySchema(many=True)


#help
help_schema = HelpSchema()
helps_schema = HelpSchema(many=True)

# service Offered
service_offer_schema = ServiceOfferedSchema()
service_offers_schema = ServiceOfferedSchema(many=True)


@app.route("/user/login",methods=["POST"])
def get_user():
    email = request.json["email"]
    password = request.json["password"]

    if user_exists(email, password):
        name = user_exists(email, password)
    else :
        data = {
            "user": None,
            "msg": "User with that email Exists."
        }

    return name


@app.route("/user/signup", methods=["POST"])
def adduser():
    email = request.json["email"]
    password= request.json["password"]
    # get user data
    user_data = Customer.query.filter_by(email=email).first()
    if not user_data:
        # hashing the password
        hashed_password = bcrypt.generate_password_hash(password)
        user = Customer(email, hashed_password)
        db.session.add(user)
        db.session.commit()
        data = user_schema.jsonify(user)
    else:
        data = {
            "user": None,
            "msg": "User with that email Exists."
        }
    return data


@app.route("/user/logout")
def user_logout():
    # remove the user token from the database
    token = request.json["token"]
    # remove token from db
    pass


@app.route("/branch/get")
def get_all_branches():
    branches = Branch.query.all()
    # loop over the
    res = branches_schema.dump(branches)
    return jsonify({"branches":res})


@app.route("/branch/get/single", methods=["GET","POST"])
def get_user_branches():
    branch_id = request.json["branch_id"]
    # make a database selection
    data = Branch.query.filter_by(id=branch_id).first()
    res = branch_schema.dump(data)
    return jsonify(res)


@app.route("/branch/add",methods=["POST"])
def add_branches():
    name = request.json["name"]
    company = request.json["company"]
    longitude = request.json["longitude"]
    latitude = request.json["latitude"]
    service = request.json["service"]
    opens = request.json["opens"]
    closes = request.json["closes"]
    description = request.json["description"]

    branch = Branch(name,company,longitude,latitude,opens,closes,service,description)
    db.session.add(branch)
    db.session.commit()
    return branch_schema.jsonify(branch)


@app.route("/service/add", methods=["GET","POST"])
def add_service():
    name = request.json["name"]
    description = request.json["description"]
    service = Service(name,description)
    db.session.add(service)
    db.session.commit()

    return service_schema.jsonify(service)


@app.route("/service/get", methods=["GET","POST"])
def get_service():
    services = Service.query.all()
    res = services_schema.dump(services)
    return jsonify(res)

# booking start
# get single booking
@app.route("/book/get", methods=["POST"])
def get_book():
    # get booking id
    booking_id = request.json["booking_id"]
    user_id = request.json["user_id"]
    if user_id_exists(user_id) and get_booking(booking_id):
        user = user_id_exists(user_id)
        booking = get_booking(booking_id)
        if user['id'] == booking["user_id"]:
            # return the ticket
            data = OnlineBooking.query.get(booking_id)
            res = booking_schema.dump(data)
        else :
            res = { 'msg' : "user/booking mismatch"}
    else :
        res = {"msg" : "user/booking mismatch"}
    return jsonify({"booking_data" : res})


@app.route("/book/make",methods=["POST"])
def make_book():
    service_name = request.json["service_name"]
    start = request.json["start"]
    branch_id = request.json["branch_id"]
    user_id = request.json["user_id"]
    booking = create_booking(service_name,user_id,start, branch_id)
    if booking:
        final = generate_ticket(booking["id"])
    else:
        final = {"msg": "Error generating the ticket. Please Try again later."}
    return jsonify(final)


@app.route("/book/get/all", methods=["GET","POST"])
def get_all_bookings():
    user_id = request.json["user_id"]
    # generate_ticket()
    if user_id_exists(user_id):
        res = get_user_bookings(user_id)
        tickets = list()
        for booking in res:
            tickets.append(generate_ticket(booking["id"]))
        res  = tickets
    else:
        res = {"msg": "user does not exist"}, 500

    return jsonify({"booking_data": res})


# get user bookings
@app.route("/book/get/user",methods=["POST"])
def get_user_bookings():
    # geting post data
    user_id = request.json["user_id"]
    # make a database selection
    data = Book.query.filter_by(user_id=user_id).all()
    res = books_schema.dump(data)
    return jsonify({ "booking_data": res})


# booking end

@app.route("/company/get")
def get_companies():
    companies = Company.query.all()
    company_data = companies_schema.dump(companies)
    return jsonify(company_data)

#getting branch by company
@app.route("/branch/by/company",methods=["POST"])
def get_by_branch():
    company = request.json["company"]
    branch = Branch.query.filter_by(company=company).all()
    data = branches_schema.dump(branch)
    return jsonify(data)


@app.route("/branch/by/service",methods=["POST"])
def get_by_service():
    service = request.json["service"]
    branch = Branch.query.filter_by(service=service).all()
    data = branches_schema.dump(branch)
    return jsonify(data)


@app.route("/company/by/id",methods=["POST"])
def company_service():
    service = request.json["id"]
    branch = Company.query.get(service)
    data = company_schema.dump(branch)
    return jsonify(data)


@app.route("/company/by/service",methods=["POST"])
def company_by_service():
    service = request.json["service"]
    branch = Company.query.filter_by(service=service).all()
    data = companies_schema.dump(branch)
    return jsonify(data)


@app.route("/search/<string:term>")
def search(term):
    # getting user specific data
    search = Help.query.filter(Help.solution.contains(term))
    data = helps_schema.dump(search)
    # companies = Company.query.co()
    # data = companies_schema.dump(companies)
    return jsonify(data)


# the search route
@app.route("/app/search", methods=["POST"])
def search_app():
    # data from the terms search
    term = request.json["term"]
    company_lookup = Company.query.filter(Company.name.contains(term)).first()
    company_data = company_schema.dump(company_lookup)
    # getting branch_data from company data
    final_branch_data_company = []
    if company_data :
        company_name = company_data["name"]
        branchdata_from_companyid = Branch.query.filter_by(company=company_name).all();
        branch_data_company = branches_schema.dump(branchdata_from_companyid)
        final_branch_data_company = branch_data_company
    # gettng data by company name
    branch_lookup = Branch.query.filter(Branch.name.contains(term))
    branch_data_branch = branches_schema.dump(branch_lookup)
    final_branch_data_term = branch_data_branch
    data = final_branch_data_term + final_branch_data_company
    return  jsonify(data)

@app.route("/services/get/all",methods=["POST"])
def service_offered():
    branch_id = request.json["branch_id"]
    lookup = ServiceOffered.query.filter_by(branch_id = branch_id).all()
    data = service_offers_schema.dump(lookup)
    return jsonify(data)


# check if the user exists
def user_exists(email,password):
    data = Customer.query.filter_by(email=email).first()
    print(data)
    # checking for the password
    if data:
        if bcrypt.check_password_hash(data.password,password):
            token = secrets.token_hex(48)
            result = {"user_data"  : user_schema.dump(data), "token" : token}
    else :
        result = {
            "user": None,
            "msg": "Bad Username/Password combination"
        }
    return jsonify(result)


def create_booking(service_name,user_id,start,branch_id):
    if service_exists(service_name,branch_id):
        # get the service
        data = service_exists(service_name,branch_id)
        name = data["name"]
        if get_last_ticket(service_name):
            # get last ticket is active next == True
            # get the last booking
            book = get_last_ticket(service_name)
            # if is active we can creat a next
            is_active = book["active"]
            is_serviced = book["serviced"]
            if is_active:
                # last booking active new booking should be next
                last_ticket_number = book["ticket"]
                next_ticket = int(last_ticket_number) + 1
                final = make_booking(name,user_id, start, branch_id, next_ticket, upcoming=True)
            elif is_serviced :
                last_ticket_number = book["ticket"]
                next_ticket = int(last_ticket_number) + 1
                final = make_booking(name, user_id, start, branch_id, next_ticket, active=True)
            else:
                # last booking next so this booking should just be a normal booking
                last_ticket_number = book["ticket"]
                next_ticket = int(last_ticket_number) + 1
                final = make_booking(name,user_id, start, branch_id, next_ticket)
        else:
            # we are making the first booking for this category
            # we are going to make this ticket  active
            next_ticket = 1
            final = make_booking(name, user_id, start, branch_id, next_ticket,active=True)
    else:
        final = {"msg": "Service does not exist"}
    return final


def make_booking(service_name,user_id, start="", branch_id=1, ticket=1, active=False, upcoming=False, serviced=False,teller=000):
    lookup = OnlineBooking(service_name, user_id, start, branch_id, ticket, active, upcoming, serviced, teller)
    db.session.add(lookup)
    db.session.commit()
    return booking_schema.dump(lookup)


def service_exists(name, branch_id):
    lookup = ServiceOffered.query.filter_by(name=name).filter_by(branch_id=branch_id).first()
    data = service_offered_schema.dump(lookup)
    return data

def get_last_ticket(service_name):
    lookup = OnlineBooking.query.filter_by(service_name = service_name).order_by(desc(OnlineBooking.date_added)).first()
    booking_data = booking_schema.dump(lookup)
    return booking_data

def branch_exist(branch_id):
    lookup = Branch.query.get(branch_id)
    branch_data = branch_schema.dump(lookup)
    return branch_data

# assume we are making a booking
def generate_ticket(booking_id):
    # get_ticket code
    booking = get_booking(booking_id)
    if booking:
        branch = branch_exist(booking['branch_id'])
        service = service_exists(booking["service_name"],booking["branch_id"])
        if branch and service :
            code = service["code"]+booking["ticket"]
            branch_name = branch["name"]
            company = branch["company"]
            service_name = service["name"]
            date_added = booking["start"]
            final ={"code" : code, "branch": branch_name, "company": company, "service": service_name,
                    "date": date_added }
        else:
            final = {"msg":"Details not Found"}
    else:
        final = {"msg":"Booking not Found"}
    return final


def get_booking(booking_id):
    lookup = OnlineBooking.query.get(booking_id)
    data = booking_schema.dump(lookup)
    return data

def get_user_bookings(user_id):
    lookup = OnlineBooking.query.filter_by(user_id=user_id).all()
    data = bookings_schema.dump(lookup)
    return data

def user_id_exists(user_id):
    lookup = Customer.query.get(user_id)
    data = user_schema.dump(lookup)
    return data

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=4000)





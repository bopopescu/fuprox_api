# from logging import exception

from flask import request, jsonify
from fuprox import db, app
from fuprox.models import (Customer, Branch, CustomerSchema, BranchSchema, Service, ServiceSchema
, Company, CompanySchema, Help, HelpSchema, ServiceOffered, ServiceOfferedSchema,
                           Booking, BookingSchema, TellerSchema, Teller)
import secrets
from fuprox import bcrypt

# from fuprox.utilities import user_exists
from fuprox.models import Customer, CustomerSchema
from fuprox import bcrypt
from fuprox.models import Customer, CustomerSchema
from fuprox import bcrypt
from sqlalchemy import desc, asc
import logging
import sqlalchemy
import socketio
import requests
import time
import eventlet.wsgi

link = "http://localhost:4000"
# standard Python
sio = socketio.Client()

# from fuprox.utilities import user_exists

# adding some product schemas
user_schema = CustomerSchema()
users_schema = CustomerSchema(many=True)

service_ = ServiceSchema()
service_s = ServiceSchema(many=True)

# branch schema

branch_schema = BranchSchema()
branches_schema = BranchSchema(many=True)

# service offered schema
service_offered_schema = ServiceOfferedSchema()
services_offered_schema = ServiceOfferedSchema(many=True)

# service schema
service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)

booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)

# getting companiy schema
company_schema = CompanySchema()
companies_schema = CompanySchema(many=True)

# help
help_schema = HelpSchema()
helps_schema = HelpSchema(many=True)

# service Offered
service_offer_schema = ServiceOfferedSchema()
service_offers_schema = ServiceOfferedSchema(many=True)

# teller schema
teller_schema = TellerSchema()
tellers_schema = TellerSchema(many=True)


@app.route("/user/login", methods=["POST"])
def get_user():
    email = request.json["email"]
    password = request.json["password"]

    if user_exists(email, password):
        name = user_exists(email, password)
    else:
        data = {
            "user": None,
            "msg": "User with that email Exists."
        }

    return name


@app.route("/user/signup", methods=["POST"])
def adduser():
    email = request.json["email"]
    password = request.json["password"]
    # get user data
    lookup = Customer.query.filter_by(email=email).first()
    user_data = user_schema.dump(lookup)
    if not user_data:
        # hashing the password
        hashed_password = bcrypt.generate_password_hash(password)
        user = Customer(email, hashed_password)
        db.session.add(user)
        db.session.commit()
        data = user_schema.dump(user)
        if data:
            sio.emit("sync_online_user", {"user_data": data})
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
    lst = list()
    # here we are going to make a teller request to the socket
    # sio.emit("teller",{"branch_id":res})
    for item in res:
        final = bool()
        if branch_is_medical(item["id"]):
            final = True
        else:
            final = False

        item["is_medical"] = final
        lst.append(item)
    return jsonify({"branches": lst})


@app.route("/branch/get/single", methods=["GET", "POST"])
def get_user_branches():
    branch_id = request.json["branch_id"]
    # make a database selection
    data = Branch.query.filter_by(id=branch_id).first()
    res = branch_schema.dump(data)
    final = bool()
    if res:
        if branch_is_medical(res["id"]):
            final = True
        else:
            final = False
    res["is_medical"] = final
    return jsonify(res)


@app.route("/branch/add", methods=["POST"])
def add_branches():
    name = request.json["name"]
    company = request.json["company"]
    longitude = request.json["longitude"]
    latitude = request.json["latitude"]
    service = request.json["service"]
    opens = request.json["opens"]
    closes = request.json["closes"]
    description = request.json["description"]

    branch = Branch(name, company, longitude, latitude, opens, closes, service, description)
    db.session.add(branch)
    db.session.commit()
    return branch_schema.jsonify(branch)


@app.route("/service/add", methods=["GET", "POST"])
def add_service():
    name = request.json["name"]
    description = request.json["description"]
    service = Service(name, description)
    db.session.add(service)
    db.session.commit()
    return service_schema.jsonify(service)


@app.route("/service/get", methods=["GET", "POST"])
def get_service():
    services = Service.query.all()
    res = services_schema.dump(services)
    final = [i for n, i in enumerate(res) if i not in res[n + 1:]]
    return jsonify(final)


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
        if user['id'] == booking["user"]:
            # return the ticket
            data = Booking.query.get(booking_id)
            final = booking_schema.dump(data)

            if final:
                name = ServiceOffered.query.filter_by(name=final["service_name"]).first()
                data = service_offer_schema.dump(name)
                res = {
                    "active": final["active"],
                    "branch_id": final["branch_id"],
                    "booking_id": final["id"],
                    "service_name": final["service_name"],
                    "serviced": final["serviced"],
                    "user_id": final["user"],
                    "start": final["start"],
                    "code": data["code"] + final["ticket"]
                }
        else:
            res = {'msg': "user/booking mismatch"}
    else:
        res = {"msg": "user/booking mismatch"}
    return jsonify({"booking_data": res})


@app.route("/book/make", methods=["POST"])
def make_book():
    service_name = request.json["service_name"]
    # start = datetime.now()
    start = request.json["start"]
    branch_id = request.json["branch_id"]
    user_id = request.json["user_id"]
    is_instant = True if request.json["is_instant"] else False
    booking = create_booking(service_name, start, branch_id, is_instant=is_instant, user_id=user_id)
    if booking:
        final = generate_ticket(booking["id"])
        sio.emit("online", {"booking_data": booking})
    else:
        final = {"msg": "Error generating the ticket. Please Try again later."}
    return jsonify(final)


@app.route("/book/get/all", methods=["GET", "POST"])
def get_all_bookings():
    user_id = request.json["user_id"]
    if is_user(user_id):
        res = get_user_bookings(user_id)
        tickets = list()
        for booking in res:
            tickets.append(generate_ticket(booking["id"]))
        res = tickets
    else:
        res = {"msg": "user does not exist"}, 500
    return jsonify({"booking_data": res})


@app.route("/book/get/user", methods=["POST"])
def get_user_bookings_():
    # getting post data
    user_id = request.json["user_id"]
    # make a database selection
    data = Booking.query.filter_by(user=user_id).all()
    res = bookings_schema.dump(data)
    final = list()
    for item in res:
        serv = "0" if item["serviced"] else "1"
        item["serviced"] = serv
        final.append(item)
    return jsonify({"booking_data": final})


# booking end
@app.route("/company/get")
def get_companies():
    companies = Company.query.all()
    company_data = companies_schema.dump(companies)
    return jsonify(company_data)


# getting branch by company
@app.route("/branch/by/company", methods=["POST"])
def get_by_branch():
    company = request.json["company"]
    branch = Branch.query.filter_by(company=company).all()
    data = branches_schema.dump(branch)
    lst = list()
    for item in data:
        final = bool()
        if branch_is_medical(item["id"]):
            final = True
        else:
            final = False
        item["is_medical"] = final
        lst.append(item)
    return jsonify(lst)


@app.route("/branch/by/service", methods=["POST"])
def get_by_service():
    service = request.json["service"]
    branch = Branch.query.filter_by(service=service).all()
    data = branches_schema.dump(branch)
    lst = list()
    for item in data:
        final = bool()
        if branch_is_medical(item["id"]):
            final = True
        else:
            final = False
        item["is_medical"] = final
        lst.append(item)
    return jsonify(data)


@app.route("/company/by/id", methods=["POST"])
def company_service():
    service = request.json["id"]
    branch = Company.query.get(service)
    data = company_schema.dump(branch)
    return jsonify(data)


@app.route("/company/by/service", methods=["POST"])
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
    if company_data:
        company_name = company_data["name"]
        branchdata_from_companyid = Branch.query.filter_by(company=company_name).all();
        branch_data_company = branches_schema.dump(branchdata_from_companyid)
        final_branch_data_company = branch_data_company
    # gettng data by company name
    branch_lookup = Branch.query.filter(Branch.name.contains(term))
    branch_data_branch = branches_schema.dump(branch_lookup)
    final_branch_data_term = branch_data_branch
    # update cunstomer data to add medical
    data = final_branch_data_term + final_branch_data_company
    lst = list()

    for item in data:
        final = bool()
        if branch_is_medical(item["id"]):
            final = True
        else:
            final = False
        med = {"is_medical": final}
        item.update(med)
        lst.append(item)

    return jsonify(lst)


@app.route("/services/get/all", methods=["POST"])
def service_offered():
    branch_id = request.json["branch_id"]
    lookup = ServiceOffered.query.filter_by(branch_id=branch_id).all()
    data = service_offers_schema.dump(lookup)
    final = list()

    for item in range(0,len(data)) :
        if item %2 == 0:
            final.append(data[item])
    return jsonify(final)


@app.route("/ahead/of/you", methods=["POST"])
def ahead_of_you():
    service_name = request.json["service_name"]
    branch_id = request.json["branch_id"]
    lookup = Booking.query.filter_by(service_name=service_name).filter_by(branch_id=branch_id).filter_by(
        serviced=False).all()
    data = len(bookings_schema.dump(lookup)) if len(bookings_schema.dump(lookup)) else 0
    return jsonify({"infront": data})


@app.route("/ahead/of/you/id", methods=["POST"])
def ahead_of_you_id():
    branch_id = request.json["booking_id"]
    return jsonify(ahead_of_you_id(branch_id))


@app.route("/sycn/online/booking", methods=["POST"])
def sync_bookings():
    data = request.json["data"]
    service_name = data["service_name"]
    start = data["start"]
    branch_id = data["branch_id"]
    is_instant = data["instant"]
    user = data["user"]
    ticket = data["ticket"]
    key_ = data["key_"]
    is_active = True if data['active'] == "True" else False
    # print("booking exist",booking_exists(branch_id, service_name, ticket))
    if not booking_exists(branch_id, service_name, ticket):
        final = dict()
        try:
            final = create_booking_online_(service_name,start,branch_id,is_instant,user,kind=ticket,key=key_)
        except sqlalchemy.exc.IntegrityError:
            ("Error! Could not create booking.")
    else:
        final = {"msg": "booking exists"}
    return final


@app.route("/sycn/offline/services", methods=["POST"])
def sync_services():
    '''
    {'key': 'c4901b3161fc41c7d0151803ec5314a72878904d3f1b4a2ff023de35740b741b',
    'code': 'SD', 'date_added': '2020-04-13T22:39:39', 'icon': '4', 'id': 35, 'teller': '',
     'branch_id': 6, 'name': 'Said'}

    :return:
    '''
    name = request.json["name"]
    teller = request.json["teller"]
    branch_id = request.json["branch_id"]
    code = request.json["code"]
    icon_id = request.json["icon"]
    key = request.json["key"]
    try:
        key_data = get_online_by_key(key)
        if key_data:
            service = create_service(name, teller, key_data["id"], code, icon_id)
    except sqlalchemy.exc.IntegrityError:
        print("Error! Could not create service.")
    return service_schema.jsonify(service)


@app.route('/sycn/offline/teller', methods=["POST"])
def sycn_teller():
    data = request.json["data"]
    service = data["service"]
    branch = data["branch"]
    number = data["number"]
    teller = dict()
    try:
        teller = add_teller(number, branch, service)
    except sqlalchemy.exc.IntegrityError:
        print("Error! Could not add the record.")
    return teller


@app.route("/update/ticket",methods=["POST"])
def update_tickets_():
    # get branch by key
    key = request.json["key"]
    service_name = request.json["service_name"]
    # branch_id = request.json["branch_id"]
    ticket = request.json["ticket"]
    branch_data = get_online_by_key(key)
    final = dict()
    if branch_data:
        # online booking
        booking_lookup = Booking.query.filter_by(service_name=service_name).filter_by(branch_id=branch_data["id"]).\
            filter_by(ticket=ticket).first()
        booking_data = booking_schema.dump(booking_lookup)
        if booking_data:
            # make this booking active
            booking_lookup.serviced = True
            db.session.commit()
            final = booking_schema.dump(booking_lookup)

    return final


def get_online_by_key(key):
    lookup = Branch.query.filter_by(key_=key).first()
    lookup_data = branch_schema.dump(lookup)
    return lookup_data


def services_exist(services, branch_id):
    holder = services.split(",")
    for item in holder:
        if not service_exists(item, branch_id):
            return False
    return True


def add_teller(teller_number, branch_id, service_name):
    # here we are going to ad teller details
    if len(service_name.split(",")) > 1:
        if services_exist(service_name, branch_id) and branch_exist(branch_id):
            # get teller by name
            if get_teller(teller_number):
                final = {"msg": "Teller number exists"}, 500
            else:
                lookup = Teller(teller_number, branch_id, service_name)
                db.session.add(lookup)
                db.session.commit()
                final = teller_schema.dump(lookup)
        else:
            final = {"msg": "branch/service name error. Make sure service name and branch name exists. many"}
    else:
        if branch_exist(branch_id) and service_exists(service_name, branch_id):
            # get teller by name
            if get_teller(teller_number):
                final = {"msg": "Teller number exists"}, 500
            else:
                lookup = Teller(teller_number, branch_id, service_name)
                db.session.add(lookup)
                db.session.commit()
                final = teller_schema.dump(lookup)
        else:
            final = {"msg": "branch/service name error. Make sure service name and branch name exists. single"}, 500

    return final


def create_service(name, teller, branch_id, code, icon_id):
    if branch_exist(branch_id):
        final = None
        if service_exists(name, branch_id):
            final = {"msg": "Error service name already exists"}
        else:
            if get_service_code(code, branch_id):
                final = {"msg": "Error Code already exists"}
            else:
                service = ServiceOffered(name, branch_id, teller, code, 1)
                db.session.add(service)
                db.session.commit()
                final = service_schema.dump(service)
    else:
        final = {"msg": "Service/Branch issue"}
    return final


def create_service(name, teller, branch_id, code, icon_id):
    if branch_exist(branch_id):
        final = None
        if service_exists(name, branch_id):
            final = {"msg": "Error service name already exists", "status": None}
        else:
            if get_service_code(code, branch_id):
                final = {"msg": "Error Code already exists", "status": None}
            else:
                # check if icon exists for the branch
                # if icon_exists(icon_id, branch_id):
                # lookup = Icon.query.get(icon_id)
                # data = icon_schema.dump(lookup)
                # if data:
                service = ServiceOffered(name, branch_id, teller, code, 1)
                db.session.add(service)
                db.session.commit()
                final = service_schema.dump(service)
    else:
        final = {"msg": "Service/Branch issue", "status": None}
    return final


# check if the user exists
def user_exists(email, password):
    data = Customer.query.filter_by(email=email).first()
    # checking for the password
    if data:
        if bcrypt.check_password_hash(data.password, password):
            token = secrets.token_hex(48)
            result = {"user_data": user_schema.dump(data), "token": token}
    else:
        result = {
            "user": None,
            "msg": "Bad Username/Password combination"
        }
    return jsonify(result)


def is_user(user_id):
    lookup = Customer.query.get(user_id)
    user_data = user_schema.dump(lookup)
    return user_data


def get_teller(number):
    lookup = Teller.query.filter_by(number=number).first()
    data = teller_schema.dump(lookup)
    return data


def ticket_queue(service_name, branch_id):
    lookup = Booking.query.filter_by(service_name=service_name).filter_by(branch_id=branch_id).order_by(
        desc(Booking.date_added)).first()
    booking_data = booking_schema.dump(lookup)
    return booking_data


def create_booking(service_name, start, branch_id, is_instant, user_id):
    if service_exists(service_name, branch_id):

        if is_user(user_id):
            final = ""
            # get the service
            data = service_exists(service_name, branch_id)
            name = data["name"]
            if ticket_queue(service_name, branch_id):
                # get last ticket is active next == True
                # get the last booking
                book = get_last_ticket(service_name, branch_id)
                # if is active we can creat a next
                is_active = book["active"]
                is_serviced = book["serviced"]
                # last booking next so this booking should just be a normal booking
                last_ticket_number = book["ticket"]
                next_ticket = int(last_ticket_number) + 1
                final = make_booking(name, start, branch_id, next_ticket, instant=is_instant, user=user_id)
            else:
                # we are making the first booking for this category
                # we are going to make this ticket  active
                next_ticket = 1
                final = make_booking(name, start, branch_id, next_ticket, active=True, instant=is_instant, user=user_id)
        else:
            final = None
            logging.info("user does not exist")
    else:
        final = {'msg': None}
        logging.info("service does not exists")
    return final


def create_booking_online(service_name, start, branch_id, ticket, is_instant=False, user_id="", is_active=False):
    data = service_exists(service_name, branch_id)
    final = make_booking(service_name, start, branch_id, ticket, False, is_active, instant=is_instant, user=user_id)
    return final


def update_branch_offline(key):
    lookup = Branch.query.filter_by(key_=key).first()
    lookup_data = branch_schema.dump(lookup)
    return lookup_data



def create_booking_online_(service_name, start, branch_id_, is_instant=False, user=0, kind=0, key=""):
    data_ = update_branch_offline(key)
    branch_id = data_["id"] if data_ else 1
    if branch_is_medical(branch_id):
        if service_exists(service_name, branch_id):
            # get the service
            data = service_exists(service_name, branch_id)
            name = data["name"]
            if ticket_queue(service_name, branch_id):
                book = ticket_queue(service_name, branch_id)
                last_ticket_number = book["ticket"]
                next_ticket = int(last_ticket_number) + 1
                final = make_booking(name, start, branch_id, next_ticket, instant=False, user=user, kind=kind)
            else:
                # we are making the first booking for this category
                # we are going to make this ticket  active
                next_ticket = 1
                final = make_booking(name, start, branch_id, next_ticket, active=False, instant=False, user=user,
                                     kind=kind)
        else:
            final = None
    else:
        if service_exists(service_name, branch_id):
            # get the service
            data = service_exists(service_name, branch_id)
            name = data["name"]
            if ticket_queue(service_name, branch_id):
                book = ticket_queue(service_name, branch_id)
                last_ticket_number = book["ticket"]
                next_ticket = int(last_ticket_number) + 1
                final = make_booking(name, start, branch_id, next_ticket, instant=is_instant, user=user, kind=kind)
            else:
                # we are making the first booking for this category
                # we are going to make this ticket  active
                next_ticket = 1
                final = make_booking(name, start, branch_id, next_ticket, active=False, instant=is_instant, user=user,
                                     kind=kind)
        else:
            final = None

    # print("the final output of the fuction >>>>",final)
    return final



def make_booking(service_name, start="", branch_id=1, ticket=1, active=False, upcoming=False, serviced=False,
                 teller=000, kind="1", user=0000, instant=False):
    final = list()
    branch_data = branch_exist(branch_id)
    if branch_is_medical(branch_id):
        lookup = Booking(service_name, start, branch_id, ticket, active, upcoming, serviced, teller, kind, user, False)
        db.session.add(lookup)
        db.session.commit()
        data_ = dict()
        key_data = {"key": branch_data["key_"]}
        data_.update(key_data)
        data_.update(booking_schema.dump(lookup))
        final = data_

    else:
        lookup = Booking(service_name, start, branch_id, ticket, active, upcoming, serviced, teller, kind, user,
                         instant)
        db.session.add(lookup)
        db.session.commit()
        data_ = dict()
        key_data = {"key": branch_data["key_"]}
        data_.update(key_data)
        data_.update(booking_schema.dump(lookup))
        final = data_
    return final


def service_exists(name, branch_id):
    lookup = ServiceOffered.query.filter_by(name=name).filter_by(branch_id=branch_id).first()
    data = service_offered_schema.dump(lookup)
    return data


def get_last_ticket(service_name, branch_id):
    '''also check last oneline ticket'''
    # here we are going to get the last ticket ofline then make anew one base on thats
    # emit("last_ticket",{"branch_id":branch_id,"service_name": service_name})

    lookup = Booking.query.filter_by(service_name=service_name).order_by(desc(Booking.date_added)).first()
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
        service = service_exists(booking["service_name"], booking["branch_id"])
        if branch and service:
            code = service["code"] + booking["ticket"]
            branch_name = branch["name"]
            company = branch["company"]
            service_name = service["name"]
            date_added = booking["start"]
            booking_id = booking["id"]
            final = {"booking_id": booking_id, "code": code, "branch": branch_name, "company": company,
                     "service": service_name,"date": date_added}
        else:
            final = {"msg": "Details not Found"}
    else:
        final = {"msg": "Booking not Found"}
    return final


def get_booking(booking_id):
    lookup = Booking.query.get(booking_id)
    data = booking_schema.dump(lookup)
    return data


def get_user_bookings(user_id):
    lookup = Booking.query.filter_by(user=user_id).all()
    data = bookings_schema.dump(lookup)
    return data


def user_id_exists(user_id):
    lookup = Customer.query.get(user_id)
    data = user_schema.dump(lookup)
    return data


def branch_is_medical(branch_id):
    branch_lookup = Branch.query.get(branch_id)
    branch_data = branch_schema.dump(branch_lookup)
    if branch_data:
        lookup = Service.query.get(branch_data["service"])
        service_data = service_.dump(lookup)
        if service_data["is_medical"]:
            service_data = True
        else:
            service_data = False
    else:
        service_data = None
    return service_data


def ahead_of_you_id(id):
    booking_id = request.json["booking_id"]
    lookup = Booking.query.get(booking_id)
    lookup_data = booking_schema.dump(lookup)
    if lookup_data:
        booking_lookup_two = Booking.query.filter_by(service_name=lookup_data["service_name"]). \
            filter_by(branch_id=lookup_data["branch_id"]).filter_by(serviced=False). \
            filter(Booking.date_added > lookup_data["start"]).all()
        final_booking_data = bookings_schema.dump(booking_lookup_two)
        final = {"msg": len(final_booking_data)}
    else:
        final = {"msg": None}

    return final


def booking_exists(branch, service, tckt):
    lookup = Booking.query.filter_by(branch_id=branch).filter_by(service_name=service).filter_by(ticket=tckt).first()
    data = booking_schema.dump(lookup)
    return data


def get_service_code(code, branch_id):
    lookup = ServiceOffered.query.filter_by(name=code).filter_by(branch_id=branch_id).first()
    data = service_schema.dump(lookup)
    return data


'''here we are going to reser tickets every midnight'''


@sio.event
def connect():
    print('connection established')


@sio.event
def teller(data):
    sio.emit('teller', {'response': 'my response'})


@sio.event
def disconnect():
    print('disconnected from server')


@sio.on('online_data_')
def online_data(data):
    data = data["booking_data"]
    is_instant = data["is_instant"]
    service_name = data["service_name"]
    user = data["user"]
    active = data["active"]
    ticket = data["ticket"]
    start = data["start"]
    id = data["id"]
    kind = data["kind"]
    serviced = data["serviced"]
    branch_id = data["branch_id"]
    key_ = data["key_"]
    final = {
        "data": {
            "instant": is_instant,
            "service_name": service_name,
            "user": user,
            "active": active,
            "ticket": ticket,
            "start": start,
            "id": id,
            "kind": kind,
            "serviced": serviced,
            "branch_id": branch_id,
            "key_" : key_
        }
    }
    requests.post(f"{link}/sycn/online/booking", json=final)


@sio.on('sync_service_')
def sync_service(data):
    requests.post(f"{link}/sycn/offline/services", json=data)



@sio.on("update_ticket_data")
def update_ticket_data(data):
    requests.post(f"{link}/update/ticket", json=data)

# add_teller_data

@sio.on("add_teller_data")
def add_teller_data(data):
    data = data["teller_data"]
    service = data["service"]
    branch = data['branch']
    number = data["number"]
    id = data["id"]
    date_added = data["date_added"]

    final = {
        "data": {
            "service": service,
            "branch": branch,
            "number": number,
            "id": id,
            "date_added": date_added,
        }
    }
    requests.post(f"{link}/sycn/offline/teller", json=final)


try:
    sio.connect("http://localhost:5000/")
    # sio.connect("http://sockets.fuprox.com/")
except socketio.exceptions.ConnectionError:
    print("Error! Could not connect to the socket server.")
# --
print("my sid", sio.sid)

if __name__ == "__main__":
    # app.run(host="0.0.0.0", debug=True, port=4000)
    eventlet.wsgi.server(eventlet.listen(('', 4000)), app)



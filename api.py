# from logging import exception

from flask import request,jsonify
from fuprox import db,app
from fuprox.models import (Customer,Branch,Book,CustomerSchema,BranchSchema,Service,ServiceSchema
                            ,BookSchema,Company,CompanySchema,Help,HelpSchema)
import secrets
from fuprox import bcrypt
from fuprox.utilities import user_exists

# adding some product schemas
user_schema = CustomerSchema()
users_schema = CustomerSchema(many=True)

# branch schema

branch_schema = BranchSchema()
branches_schema = BranchSchema(many=True)

# service schema

service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)

# service schema
book_schema = BookSchema()
books_schema = BookSchema(many=True)


#getting companiy schema
company_schema = CompanySchema()
companies_schema = CompanySchema(many=True)

#help
help_schema = HelpSchema()
helps_schema = HelpSchema(many=True)
#the help schema
# helps_schema = HelpSchema(many=True)



@app.route("/user/login",methods=["POST"])
def get_user():
    email = request.json["email"]
    password = request.json["password"]

    if user_exists(email, password):
        name = user_exists(email,password)
    else :
        data = {
            "user": None,
            "msg": "User with that email Exists."
        }

    return name


@app.route("/user/signup",methods=["POST"])
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


@app.route("/branch/get/single")
def get_user_branches():
    branch_id = request.json["user_id"]
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


@app.route("/service/add",methods=["GET","POST"])
def add_service():
    name = request.json["name"]
    description = request.json["description"]
    service = Service(name,description)
    db.session.add(service)
    db.session.commit()

    return service_schema.jsonify(service)


@app.route("/service/get",methods=["GET","POST"])
def get_service():
    services = Service.query.all()
    res = services_schema.dump(services)
    return jsonify(res)


@app.route("/book/get",methods=["POST"])
def get_booking():
    # get booking id
    key = request.json["booking_hash"]
    # get all bookings
    data = Book.query.filter_by(booking_id=key).first()
    res = book_schema.dump(data)
    return jsonify({" booking_data " : res})


@app.route("/book/make",methods=["POST"])
def make_booking():
    # get data from the user
    # hash,start,branch,institution
    booking_id = secrets.token_hex(32)
    start = request.json["start"]
    user_id = request.json["user"]
    branch = request.json["branch"]
    institution = request.json["institution"]

    # adding the data to the database
    # booking_id,user,start,branch,institution)
    booking = Book(booking_id,user_id,start,branch,institution)
    db.session.add(booking)
    db.session.commit()

    # should check if user was created successfully
    return book_schema.jsonify(booking)


@app.route("/book/get/all", methods=["GET"])
def get_all_bookings():
    # getting all data
    # we need to get the user data
    # check if he exits
    # if he does add push the data to the user
    booking_data = Book.query.all()
    data = books_schema.dump(booking_data)
    return jsonify({"bookings" : data })


# get user bookings
@app.route("/book/get/user",methods=["POST"])
def get_user_bookings():
    # geting post data
    user_id = request.json["user_id"]
    # make a database selection
    data = Book.query.filter_by(user_id=user_id).all()
    res = books_schema.dump(data)
    return jsonify({ "booking_data": res})



@app.route("/branch/company")
def get_companies():
    companies = Company.query.all()
    company_data = companies_schema.dump(companies)
    return jsonify(company_data)


@app.route("/search/<string:term>")
def search(term):
    # getting user specific data
    search = Help.query.filter(Help.solution.contains(term))
    data = helps_schema.dump(search)
    # companies = Company.query.co()
    # data = companies_schema.dump(companies)
    return jsonify(data)



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=4000)
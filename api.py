from flask import request,jsonify
from fuprox import db,app
from fuprox.models import User,Branch,Book,UserSchema,BranchSchema,Service,ServiceSchema,BookSchema
import secrets


# adding some product schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)

# branch schema

branch_schema = BranchSchema()
branches_schema = BranchSchema(many=True)

# service schema

service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)

# service schema
book_schema = BookSchema()
books_schema = BookSchema(many=True)


@app.route("/user/login",methods=["POST"])
def get_user():
    email = request.json["email"]
    name=""
    if user_exists(email):
        name = user_exists(email)
    return name


@app.route("/user/signup",methods=["POST"])
def adduser():
    email = request.json["email"]
    user = User(email)

    db.session.add(user)
    db.session.commit()
    return user_schema.jsonify(user)


@app.route("/branch/get")
def get_all_branches():
    branches = Branch.query.all()
    res = branches_schema.dump(branches)
    return jsonify({"branches":res})


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
    return jsonify({" booking_data ": res})


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
    #,booking_id,user,start,branch,institution)
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
@app.route("/book/get/user")
def get_user_bookings():
    # geting post data
    user_id = request.json["user_id"]

    # make a database selection
    data = Book.query.filter_by(user_id=2).all()
    res = book_schema.dump(data)

    return jsonify({ "booking_data": res,"passed_data" : user_id})


# check if the user exists
def user_exists(email):
    data = User.query.filter_by(email=email).first()
    result = user_schema.dump(data)
    return jsonify(result)



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=4000)
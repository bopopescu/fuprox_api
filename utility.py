from fuprox.models import Customer, CustomerSchema
from flask import jsonify
user_schema = CustomerSchema()


# check if the user exists
def user_exists(email):
    data = Customer.query.filter_by(email=email).first()
    result = user_schema.dump(data)
    return jsonify(result)
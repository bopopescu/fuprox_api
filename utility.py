from fuprox.models import User, UserSchema
import jsonify
user_schema = UserSchema()


# check if the user exists
def user_exists(email):
    data = User.query.filter_by(email=email).first()
    result = user_schema.dump(data)
    return jsonify(result)
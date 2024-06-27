"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Favorites

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def get_users():
    user = User.query.all()
    user_list = [user.serialize() for user in user]
    return jsonify(user_list), 200

@app.route('/users/favorites', methods=['GET'])
def get_users_favorites():
    current_user_id = request.args.get('user_id')
    favorites = Favorites.query.filter_by(user_id = current_user_id).all()
    favorites_list = [favorites.serialize() for favorites in favorites]
    return jsonify(favorites_list), 200

@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    people_list = [people.serialize() for people in people]
    return jsonify(people_list), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_id(people_id):
    person = People.query.get(people_id)
    if person:
        person_data = person.serialize()
        return jsonify(person_data), 200
    else:
        return jsonify({"error": "Person not found"}), 404

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    planets_list = [planet.serialize() for planet in planets]
    return jsonify(planets_list), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planets_id(planet_id):
    planet = Planets.query.get(planet_id)
    if planet:
        planet_data = planet.serialize()
        return jsonify(planet_data), 200
    else:
        return jsonify({"error": "Planet not found"}), 404

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_planet_to_favorites(planet_id):
    if request.json is None:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    data = request.json
    user_id = data.get('user_id')
    if user_id is None:
        return jsonify({"error": "User ID not provided"}), 400

    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404

    if Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first():
        return jsonify({"error": "Planet already in favorites"}), 400

    favorite = Favorites(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()

    return jsonify({"success": "Planet added to favorites"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_people_to_favorites(people_id):
    if request.json is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.json
    user_id = data.get('user_id')
    if user_id is None:
        return jsonify({"error": "User ID not provided"}), 400

    person = People.query.get(people_id)
    if person is None:
        return jsonify({"error": "Person not found"}), 404

    if Favorites.query.filter_by(user_id=user_id, people_id=people_id).first():
        return jsonify({"error": "Person already in favorites"}), 400

    favorite = Favorites(user_id=user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()

    return jsonify({"success": "Person added to favorites"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_favorite(planet_id):
    if request.json is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.json
    user_id = data.get('user_id')
    favorite = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite is None:
        return jsonify({"error": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"success": "Favorite deleted"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_people_favorite(people_id):
    if request.json is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.json
    user_id = data.get('user_id')
    favorite = Favorites.query.filter_by(user_id=user_id, people_id=people_id).first()
    if favorite is None:
        return jsonify({"error": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"success": "Favorite deleted"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


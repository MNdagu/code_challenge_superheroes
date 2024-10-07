#!/usr/bin/env python3
# app.py
from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    response = jsonify([hero.to_dict() for hero in heroes])
    return make_response(response, 200)

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.filter(Hero.id == id).first()
    
    if hero is None:
        return jsonify({"error": "Hero not found"}), 404
    
    return make_response(jsonify(hero.to_dict()), 200)

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    response = jsonify([power.to_dict() for power in powers])
    return make_response(response, 200)

@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = Power.query.filter(Power.id == id).first()
    
    if power is None:
        return jsonify({"error": "Power not found"}), 404
    
    return make_response(jsonify(power.to_dict()), 200)

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)

    if not power:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()

    if 'description' in data:
        power.description = data['description']

    try:
        db.session.commit()
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400

    return make_response(jsonify({
        "description": power.description,
        "id": power.id,
        "name": power.name
    }), 200)

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    hero_id = data.get('hero_id')
    power_id = data.get('power_id')
    
    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)

    if not hero or not power:
        return jsonify({"error": "Hero or Power not found"}), 404

    new_hero_power = HeroPower(
        strength=data.get('strength'),
        hero_id=hero.id,
        power_id=power.id
    )

    try:
        db.session.add(new_hero_power)
        db.session.commit()
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400

    hero_power_dict = new_hero_power.to_dict()
    hero_power_dict['hero'] = hero.to_dict()
    hero_power_dict['power'] = power.to_dict()

    return make_response(jsonify(hero_power_dict), 201)

if __name__ == '__main__':
    app.run(port=5555, debug=True)

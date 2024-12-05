#!/usr/bin/env python3


from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)


api.add_resource(Plants, '/plants')


class PlantByID(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first().to_dict()

        return make_response(jsonify(plant), 200)
    
    def patch(self, id):
        plant = Plant.query.filter(Plant.id == id).first()
        if not plant:
            return {"message": "Plant not found."}, 404

        data = request.get_json()
        if not data:
            return {"message": "No data provided."}, 400

   
        for attr, value in data.items():
            if hasattr(plant, attr):
                setattr(plant, attr, value)

        db.session.commit()
        return plant.to_dict(), 200

            
    def delete(self, id):
     
      target_plant = Plant.query.filter(Plant.id==id).first()
      if target_plant:


        db.session.delete(target_plant)
        db.session.commit()

        return '', 204
      return make_response({"message": "Plant not found."}, 404)
    
@app.errorhandler(NotFound)
def handle_not_found(e):

    response = make_response(
        "Not Found: The requested resource does not exist.",
        404
    )

    return response
@app.errorhandler(400)
def handle_bad_request(e):
    return make_response({"message": "Bad Request."}, 400)

@app.errorhandler(500)
def handle_internal_error(e):
    return make_response({"message": "Internal Server Error."}, 500)


app.register_error_handler(404, handle_not_found)






api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)

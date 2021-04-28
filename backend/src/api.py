import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def drinks():

    drinks = Drink.query.all()
    drink_short = []
    for i in drinks:
        drink_short.append(i.short())


    return jsonify({
        'success': True,
        'status': 200,
        'drinks': drink_short
    }), 200




@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(payload):


    drinks = Drink.query.all()

    drink_long = []
    for i in drinks:
        drink_long.append(i.long())


    return jsonify({
        'success': True,
        'status': 200,
        'drinks': drink_long
    }), 200




@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):

    try:
        body = request.get_json()
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)


        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        new_drink.insert()

        drink_long = [new_drink.long()]


        return jsonify({
            'success': True,
            'status': 200,
            'drinks': drink_long
        }), 200

    except:
        abort(422)


@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, drink_id):

    body = request.get_json()

    try:
        edited_title = body.get('title', None)
        edited_recipe = body.get('recipe', None)


        drink_to_patch = Drink.query.filter(Drink.id == drink_id).one_or_none()

        drink_to_patch.title = edited_title
        drink_to_patch.recipe = json.dumps(edited_recipe)

        drink_to_patch.update()

        drink_to_patch = [drink_to_patch.long()]

        return jsonify({
            'success': True,
            'status': 200,
            'drinks': drink_to_patch
        })
    except:
        abort(422)




@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):

    drink_to_delete = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink_to_delete is None:
        abort(404)

    try:
        drink_to_delete.delete()

        return jsonify({
            'success':True,
            'status': 200,
            'delete': drink_id
        }), 200
    except:
        abort(422)



# Error Handling



@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404



@app.errorhandler(405)
def method_not_allowed(error):

    return jsonify({
      "success": False,
      "error": 405,
      "message": "method not allowed"
    }), 405


@app.errorhandler(AuthError)
def authentification_error(error):

    status_code = error.status_code
    msg = jsonify(error.error)
    return msg, status_code









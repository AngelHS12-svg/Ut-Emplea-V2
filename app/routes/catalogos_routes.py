import re
import sqlite3
from flask import Blueprint, jsonify, request
from app.utils.postal import postal_places, states, municipalities, cities

catalogos_bp = Blueprint('catalogos', __name__, url_prefix='/api/catalogos')


@catalogos_bp.errorhandler(sqlite3.Error)
def catalog_unavailable(error):
    return jsonify(error='No fue posible consultar el catálogo.'), 503


@catalogos_bp.get('/estados')
def get_states():
    return jsonify(pais='México', estados=states())


@catalogos_bp.get('/municipios')
def get_municipalities():
    state = request.args.get('estado', '')
    if state not in states():
        return jsonify(error='Estado no válido.'), 400
    return jsonify(municipios=municipalities(state))


@catalogos_bp.get('/ciudades')
def get_cities():
    state, municipality = request.args.get('estado', ''), request.args.get('municipio', '')
    if state not in states() or len(municipality) > 150:
        return jsonify(error='Ubicación no válida.'), 400
    return jsonify(ciudades=cities(state, municipality))


@catalogos_bp.get('/codigos-postales/<cp>')
def get_postal_code(cp):
    if not re.fullmatch(r'[0-9]{5}', cp):
        return jsonify(error='El código postal debe tener 5 dígitos.'), 400
    places = postal_places(cp)
    if not places:
        return jsonify(error='Código postal no encontrado en el catálogo.', asentamientos=[]), 404
    return jsonify(pais='México', codigo_postal=cp, asentamientos=places)

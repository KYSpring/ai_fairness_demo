from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/hello', methods=['GET'])
def hello_world():
    return jsonify({
        'message': 'Hello, World!'
    }), 200 
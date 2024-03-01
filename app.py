from flask import Flask, jsonify, request
from datetime import datetime
from .database import RewardsDatabase

app = Flask(__name__)
database = RewardsDatabase()  # our fake "database"!


def error_json_res(
        status='error',
        message='Bad Request',
        details='Invalid input'):
    '''
    Helper function for error json results
    '''
    json = {}
    json['status'] = status
    json['message'] = message
    json['details'] = details
    return jsonify(json)


def dt_to_ts(s, format="%Y-%m-%dT%H:%M:%SZ"):
    '''
    Converts datetime timestamp to UNIX timestamp
    '''
    dt_obj = datetime.strptime(s, format)
    return int(dt_obj.timestamp())


@app.route("/rewards/transactions", methods=['POST'])
def create_transaction():
    # Validate Request

    payer = request.json.get('payer', None)
    if not payer or not isinstance(payer, str):
        return error_json_res(details='payer missing/invalid'), 400

    points = request.json.get('points', None)
    if not points or not isinstance(points, int) or points == 0:
        return error_json_res(details='points missing/invalid'), 400

    timestamp = request.json.get('timestamp', None)
    try:
        # can take either UNIX timestamp or "%Y-%m-%dT%H:%M:%SZ" datetime
        if not isinstance(timestamp, int):
            timestamp = dt_to_ts(timestamp)
        elif timestamp <= 0:
            return error_json_res(details='timezone invalid'), 400
    except Exception as e:
        return error_json_res(details='timezone missing/invalid'), 400

    # Attempt to commit transaction
    success, msg = database.add_transaction(payer, points, timestamp)
    if not success:
        return error_json_res(details=msg), 400

    success_json = {
        "status": "success",
        "message": "Resource created successfully",
        "data": {
            "payer": payer,
            "points": points,
            "timestamp": timestamp
        }
    }
    return jsonify(success_json), 200


@app.route("/rewards/spend", methods=['POST'])
def spend_points():
    # Validate request
    points = request.json.get('points', None)
    if not points or not isinstance(points, int) or points <= 0:
        return error_json_res(), 400

    # Attempt to commit spending points
    success, output = database.spend_points(points)
    if not success:
        return error_json_res(details=output), 400

    return jsonify(output), 200


@app.route("/rewards/balances", methods=['GET'])
def get_balances():
    balance = database.get_balance()
    return jsonify(balance), 200

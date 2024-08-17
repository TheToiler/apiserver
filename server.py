from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configuratie van JWT
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Verander dit naar iets veiliger
jwt = JWTManager(app)

# In-memory gebruikersgegevens (in een echte app gebruik je een database)
users = {
    "user@example.com": generate_password_hash("password")
}

# Endpoint voor inloggen
@app.route('/api/auth/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    user_password_hash = users.get(email)
    if user_password_hash and check_password_hash(user_password_hash, password):
        access_token = create_access_token(identity=email)
        return jsonify({"token": access_token}), 200

    return jsonify({"msg": "Invalid credentials"}), 401

# Beschermde route die alleen toegankelijk is met een geldig token
@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

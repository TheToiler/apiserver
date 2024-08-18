from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from utils import database

app = Flask(__name__)

# Enable CORS
cors = CORS(app)

# Configuratie van JWT
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Verander dit naar iets veiliger
jwt = JWTManager(app)

# In-memory gebruikersgegevens (in een echte app gebruik je een database)
users = {
    "user@example.com": generate_password_hash("password")
}

# In-memory agentgegevens (in een echte app gebruik je een database)
agents = {
    "ditiseenapikey"
}

def apikey_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        agent_apikey = request.headers.get('apikey')
        if  agent_apikey == None:
            print(f'No apikey, request denied!')
            def reponse():
                return jsonify({"msg": "Invalid credentials"}), 401
            return reponse()
        if agents.issubset([agent_apikey]) == False:
            print(f'Send apikey: {agent_apikey}, request denied!')
            def reponse():
                return jsonify({"msg": "Invalid credentials"}), 401
            return reponse()
        return f(*args, **kwargs)
    return decorated_function



#region Agent endpoints

# Endpoint om gegevens op te sturen
@app.route('/api/agent/senddata', methods=['POST'])
@apikey_required
def agent_senddata():
    name = request.json.get('name')
    email = request.json.get('email')
    message = request.json.get('message')
    print(f"Name: {name}, Email: {email}, Message: {message}")
    return jsonify({"msg": "Message received"}), 200

#region Monitor endpoints

@app.route('/api/monitor/login', methods=['POST'])
def monitor_login():
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    user_password_hash = users.get(email)
    if user_password_hash and check_password_hash(user_password_hash, password):
        access_token = create_access_token(identity=email)
        return jsonify({"token": access_token}), 200

    return jsonify({"msg": "Invalid credentials"}), 401

# Endpoint voor inloggen
@app.route('/api/monitor/mailto', methods=['POST'])
def monitor_mailto():
    print('Headers: ', request.headers)
    name = request.json.get('name')
    email = request.json.get('email')
    message = request.json.get('message')
    with open('emailmessages.csv', 'a') as f:
        # print(f"Email: {email}, Password: {password}, Message: {message}")
        f.write(f"Name: {name}, Email: {email}, Message: {message}\n")
    return jsonify({"msg": "Message received"}), 200

# Beschermde route die alleen toegankelijk is met een geldig token
@app.route('/api/monitor/protected', methods=['GET'])
@jwt_required()
def monitor_protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
    
#region Postmane tests

from flask import Flask, jsonify, abort, request, send_from_directory, redirect, session, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from enum import Enum
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity, JWTManager
from werkzeug.utils import secure_filename
import os
import msal
import uuid
import json

app = Flask(__name__, 
static_folder='../client/dist', 
static_url_path='/')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_very_complex_string_here'
db = SQLAlchemy(app)
CORS(app)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

"""
TenantID: 913f18ec-7f26-4c5f-a816-784fe9a58edd
ClientID: a43a60fc-0797-469d-b195-722df39d414a
Secret ID: c8c4b13f-c2e5-443d-92ff-262a100d77c5
Value: 1.N8Q~5DfbaV_CbJtnLm4FUx2Snd_rKRoEzyoacP

redirect URI: localhost:8080
"""

app.secret_key = "your_secret_key_here"

app.config["CLIENT_ID"] = "a43a60fc-0797-469d-b195-722df39d414a"
app.config["CLIENT_SECRET"] = "1.N8Q~5DfbaV_CbJtnLm4FUx2Snd_rKRoEzyoacP"
app.config["AUTHORITY"] = "https://login.microsoftonline.com/913f18ec-7f26-4c5f-a816-784fe9a58edd"
app.config["REDIRECT_PATH"] = "/"
app.config["SCOPE"] = ["User.Read"]

msal_app = msal.PublicClientApplication(
    app.config["CLIENT_ID"],
    authority=app.config["AUTHORITY"],
    #client_credential=app.config["CLIENT_SECRET"],
)

@app.route("/ssologin")
def ssologin():
    print("SSO login bror")
    session["state"] = str(uuid.uuid4())
    auth_url = msal_app.get_authorization_request_url(
        app.config["SCOPE"],
        state=session["state"],
        redirect_uri='http://localhost:8080',
    )
    return redirect(auth_url)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if 'code' in request.args:  # This is the authorization response from Microsoft
        print(f"Got code from Microsoft!")
        code = request.args['code']
        state = request.args['state']
        if session.get("state") == state:  # Validate the state
            print("State is valid!")
            result = msal_app.acquire_token_by_authorization_code(
                code,
                scopes=app.config["SCOPE"],
                redirect_uri='http://localhost:8080' 
            )
            if "access_token" in result:
                oid = result.get('id_token_claims')['oid']
                user = User.query.filter_by(oid=oid).first()

                print(f"{result.get('id_token_claims')}")

                if not user:
                    user = User(oid=oid, liu_id=result.get('id_token_claims')['preferred_username'].split('@')[0], email=result.get('id_token_claims')['preferred_username'], name=result.get('id_token_claims')['name'], year=result.get('id_token_claims')['ageGroup'], is_admin=True)
                    db.session.add(user)
                    db.session.commit()
                    print(f"User created: {user}")
                    
                access_token = create_access_token(identity=user.id)
                response = make_response(redirect(f"http://localhost:8080/#/home"))
                response.set_cookie('access_token', access_token)
                response.set_cookie('user', json.dumps(user.serialize()))
                return response

            else:
                print("Failed to authenticate user.")
        else:
            print("Invalid state.")
    print(f"HELLO!")
    return app.send_static_file('index.html')


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    liu_id = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    program = db.Column(db.String)
    year = db.Column(db.Integer)
    is_admin = db.Column(db.Boolean, default=False)
    num_sold_items = db.Column(db.Integer, default=0)
    num_bought_items = db.Column(db.Integer, default=0)
    #items = db.relationship('Item', backref="user", foreign_keys="Item.user_id")
    sold_items = db.relationship('Item', backref="seller", foreign_keys="Item.seller_id")
    bought_items = db.relationship('Item', backref="buyer", foreign_keys="Item.buyer_id")
    #password_hash = db.Column(db.String, nullable=False)
    image_path = db.Column(db.String, nullable=True)
    oid = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<User {self.id} : {self.name} {self.email}  {self.liu_id} {self.program} {self.year} {self.is_admin} {self.num_sold_items} {self.num_bought_items} >"

    def serialize(self):
        return {
            "id":self.id,
            "name": self.name,
            "email":self.email,
            "liu_id":self.liu_id,
            "program":self.program,
            "year":self.year,
            "is_admin":self.is_admin,
            "num_sold_items":self.num_sold_items,
            "num_bought_items":self.num_bought_items,
            "image_path": request.url_root + self.image_path if self.image_path else None,
            "oid": self.oid if self.oid else ""
        } 


@app.route('/login', methods=['POST', 'OPTIONS'])
def login():

    data = request.get_json()

    user = User.query.filter_by(liu_id=data['liu_id']).first()

    if not user:
        user = User(liu_id=data['liu_id'], is_admin=True, email=f"{data['liu_id']}@student.liu.se")
        db.session.add(user)
        db.session.commit()
        print(f"User created: {user}")

    access_token = create_access_token(identity=user.id)
    response = make_response(redirect(f"http://localhost:8080/#/home"))
    response.set_cookie('access_token', access_token)
    response.set_cookie('user', json.dumps(user.serialize()))
    print(f"RESPONSE: {response.headers}")
    return response

    #TODO: Implement login with username

    """
    data = request.get_json()
    if not data or not data.get('liu_id'):
        return jsonify({'msg': 'Missing liu_id or password'}), 400
    
    user = User.query.filter_by(liu_id=data['liu_id']).first()

    if not user:
        user = User(liu_id=data['liu_id'], is_admin=True)
        db.session.add(user)
        db.session.commit()
        print(f"User created: {user}")

    access_token = create_access_token(identity=user.id)
    response = make_response(redirect(f"http://localhost:8080/#/home"))
    response.set_cookie('access_token', access_token)
    response.set_cookie('user', json.dumps(user.serialize()))
    return response
    """

class Category(Enum):
    Cyklar = 1
    Kurslitteratur = 2
    Böcker = 3
    Biljetter = 4
    Inredning = 5
    Bostad = 6
    Verktyg = 7
    Övrigt = 8

    def serialize(self):
        return {
            'value': self.value,
            'name': self.name
        }

class Condition(Enum):
    Nytt = 1
    Använd_Nyskick = 2
    Använd_Gott_skick = 3
    Använd_Slitet_skick = 4
    
    def serialize(self):
        return {
            'value': self.value,
            'name': self.name
        }

class Area(Enum):
    Linköping = 1
    Norrköping = 2

    def serialize(self):
        return {
            'value': self.value,
            'name': self.name
        }
    
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    description = db.Column(db.String(120))
    price = db.Column(db.Integer)
    category = db.Column(db.Enum(Category), nullable=True)
    condition = db.Column(db.Enum(Condition), nullable=True)
    is_sold = db.Column(db.Boolean, default=False)
    images = relationship("ItemImage", backref="item")
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    area = db.Column(db.Enum(Area), nullable=True)
    date = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<Item {self.id} : {self.title} {self.description} {self.price} {self.category} {self.condition} {self.is_sold} {self.seller_id} {self.buyer_id} {self.images} {self.area} >'

    def serialize(self):
        seller_data = self.seller.serialize() if self.seller else None
        buyer_data = self.buyer.serialize() if self.buyer else None
        return {
            "id":self.id,
            "title": self.title,
            "description":self.description,
            "price":self.price,
            "category": self.category.name if self.category else None,
            "condition":self.condition.name if self.condition else None,
            "is_sold":self.is_sold,
            "images": [image.serialize() for image in self.images],
            "seller_id": self.seller_id,
            "seller": seller_data,
            "buyer": buyer_data,
            "area": self.area.name if self.area else None,
            "date": self.date.isoformat() if self.date else None
        }

class ItemImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(120))
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))
    
    def __repr__(self):
        return f'<ItemImage {self.id} : {self.image_path} {self.item_id}>'

    def serialize(self):
        return {
            "id":self.id,
            "image_path": request.url_root + self.image_path,
            "item_id":self.item_id
        }

@app.route('/users', methods=['GET', 'POST'])
@jwt_required()
def users():
    if request.method == 'GET':
        all_users = User.query.all()
        return jsonify([user.serialize() for user in all_users])
    elif request.method == 'POST':
        data = request.get_json()
        new_user = User(name=data.get('name'), liu_id=data.get("liu_id"), program=data.get("program"), year=data.get("year"))
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.serialize()), 201
    
@app.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_users(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404)
    if request.method == 'GET':
        return jsonify(user.serialize())
    elif request.method == 'PUT':
        data = request.form.to_dict()
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
        if 'num_sold_items' in data:
            user.num_sold_items = data['num_sold_items']
        if 'year' in data:
            user.year = data['year']
        if 'program' in data:
            user.program = data['program']
        if 'name' in data:
            user.name = data['name']
        if 'image' in request.files:
            image = request.files['image']
            filename = secure_filename(image.filename)
            image_path = os.path.join('static/uploads', filename)
            image.save(image_path)
            user.image_path = image_path
            print(f"Image at path: {image_path}")
        db.session.commit()
        print(f"Image path: {user.image_path}")
        return jsonify(user.serialize()), 200
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return '', 200
    
@app.route('/current_user', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        abort(404)
    return jsonify(user.serialize())
    
@app.route('/items', methods=['GET', 'POST'])
@jwt_required()
def items():
    if request.method == 'GET':
        all_items = Item.query.all()
        return jsonify([item.serialize() for item in all_items])
    elif request.method == 'POST':
        data = request.form.to_dict()
        new_item = Item(title=data.get('title'), 
                        description=data.get("description"), 
                        price=data.get("price"), 
                        category=Category[data.get("category")], 
                        condition=Condition[data.get("condition")], 
                        area=Area[data.get("area")],
                        seller_id=get_jwt_identity()
                        )

        db.session.add(new_item)
        db.session.flush()

        if request.files['images']:
            print(f"picture added??")
            for image in request.files.getlist('images'):
                filename = secure_filename(image.filename)
                image_path = os.path.join('static/uploads', filename)
                image.save(image_path)
                new_image = ItemImage(image_path=image_path, item_id=new_item.id)
                db.session.add(new_image)
                print(f"Image at path: {image_path}")

        db.session.commit()
        for image in new_item.images:
            print(f"Image path: {image.image_path}")

        return jsonify(new_item.serialize()), 201
    
@app.route('/static/uploads/<path:filename>')
def serve_static(filename):
    return send_from_directory('static/uploads', filename)

@app.route('/items/<int:item_id>/images', methods=['DELETE'])
@jwt_required()
def remove_images(item_id):
    #TODO: Implement this
    pass

@app.route('/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_items(item_id):
    item = Item.query.get(item_id)
    if item is None:
        abort(404)
    if request.method == 'GET':
        return jsonify(item.serialize())
    elif request.method == 'PUT':
        data = request.form.to_dict()
        if 'title' in data:
            item.title = data['title']
        if 'description' in data:
            item.description = data['description']
        if 'price' in data:
            item.price = data['price']
        if 'category' in data:
            item.category = data['category']
        if 'condition' in data:
            item.condition = data['condition']
        if 'area' in data:
            item.area = data['area']
        if 'is_sold' in data:
            item.is_sold = data['is_sold']
        if 'images' in request.files:
            print(f"picture added??? (not in loop)")
            for image in request.files.getlist('images'):
                print(f"picture added??? (in loop)")
                filename = secure_filename(image.filename)
                image_path = os.path.join('static/uploads', filename)
                image.save(image_path)
                new_image = ItemImage(image_path=image_path, item_id=item.id)
                db.session.add(new_image)
                print(f"Image at path: {image_path}")
            
        db.session.commit()
        return jsonify(item.serialize()), 200
    elif request.method == 'DELETE':
        db.session.delete(item)
        db.session.commit()
        return '', 200

@app.route('/items/<int:item_id>/sell', methods=['PUT'])
@jwt_required()
def sell_item(item_id):
    item = Item.query.get(item_id)
    if item is None:
        abort(404)

    data = request.get_json()
    if 'buyer_id' not in data:
        abort(400, description="buyer_id is required")

    buyer = User.query.filter_by(liu_id=data['buyer_id']).first()    
    if buyer is None:
        abort(404, description="buyer_id is invalid")

    seller = User.query.get(item.seller_id)

    item.buyer = buyer
    item.is_sold = True
    seller.num_sold_items += 1
    buyer.num_bought_items += 1
    db.session.commit()

    # TODO: Send an email to the buyer

    return jsonify(item.serialize()), 200

@app.route('/itemimages/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_item_image(image_id):
    if image_id is None:
        abort(404)
    try:
        os.remove(ItemImage.query.get(image_id).image_path)
    except FileNotFoundError:
        print("File not found")
    image = ItemImage.query.get(image_id)
    db.session.delete(image)
    db.session.commit()
    return '', 200


@app.route('/all_available_items', methods=['GET'])
@jwt_required()
def get_all_available_items():
    available_items = [item.serialize() for item in Item.query.filter_by(is_sold=False).all()]
    return jsonify(available_items), 200

@app.route('/available_items', methods=['GET'])
@jwt_required()
def get_available_items():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        abort(404, description="User not found")
    available_items = [item.serialize() for item in user.sold_items if not item.is_sold]
    return jsonify(available_items), 200

@app.route('/sold_items', methods=['GET'])
@jwt_required()
def get_sold_items():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        abort(404, description="User not found")
    sold_items = [item.serialize() for item in user.sold_items if item.is_sold]
    return jsonify(sold_items), 200

@app.route('/bought_items', methods=['GET'])
@jwt_required()
def get_bought_items():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        abort(404, description="User not found")
    bought_items = [item.serialize() for item in user.bought_items]
    return jsonify(bought_items), 200

"""
@app.route('/sign-up', methods=['POST'])
def signup():
    data = request.get_json()
    user = User.query.filter_by(liu_id=data['liu_id']).first()
    if user:
        return jsonify({'message': 'User already exists'}), 400
    else:
        new_user = User(liu_id=data['liu_id'])
        password = data['password']
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201

    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({"token": access_token, "user": user.serialize()}), 200    
    else:
        return jsonify({'msg': 'Invalid email or password'}), 401
    """

if __name__ == "__main__":
    with app.app_context():
        #db.drop_all() # Drop all tables before creating them, to avoid conflicts
        db.create_all()
    app.run(port=8080)



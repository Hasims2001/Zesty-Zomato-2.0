from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
import datetime
import jwt
from passlib.hash import pbkdf2_sha256 
app = Flask(__name__)
app.secret_key = 'secret'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ZestyZomato.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
SECRET_KEY = 'your_secret_key'
promocode = [
    {'name': 'FLAT5', 'discount': 5, 'mininum': 1200},
    {'name': 'FLAT10', 'discount': 10, 'mininum': 2000}
]

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    availability = db.Column(db.String(10), nullable=False)
    store =  db.Column(db.String(10), nullable=False)
    def __init__(self, name, price, availability, store): 
        self.name = name
        self.price = price
        self.availability = availability  
        self.store = store

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items= db.Column(db.String(500), nullable=False)
    totalBill= db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    store = db.Column(db.String(255), nullable=False)
    promocode = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    
    def __init__(self,items, totalBill, name, email, date,store, promocode, status): 
        self.items = items
        self.totalBill = totalBill
        self.name = name
        self.email = email
        self.date = date
        self.store = store
        self.promocode = promocode  
        self.status = status  


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(255), unique=True, nullable=False)
    password= db.Column(db.String(255), nullable=False)
    token= db.Column(db.String(500))
    role = db.Column(db.String(255), nullable=False)
    def __init__(self, name, password, token, role):
        self.name = name
        self.password = password
        self.token = token
        self.role = role


with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def welcome():
    return jsonify({'message': "Welcome to Zesty Zomato"})


@app.route("/login", methods=['POST'])
def loginUser():
    data = request.get_json()
    allUsers = Users.query.all()
    for user in allUsers:
        if(user.name == data['name'] and pbkdf2_sha256.verify(data['password'], user.password)):
            token = jwt.encode({"user": {'name': user.name, 'role': user.role}}, SECRET_KEY, algorithm='HS256')
            user.token = token
            db.session.commit()
            return jsonify({'issue': False, 'token': token,  'message': "login success"})
    
    return jsonify({'issue': True, 'message': 'Invalid user data'})


@app.route('/register', methods=['POST'])
def registerUser():
    data = request.get_json()
    users = Users.query.all()
    
    for user in users:
        if(user.name == data['name']):
            return jsonify({'issue': True,  'message': "name is already present in database"})

    hashed = pbkdf2_sha256.using(rounds=10, salt_size=16).hash(data['password'])
    new_user = Users(name=data['name'], password=hashed, token="", role=data['role'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'issue': False, 'message': 'register success'})


@app.route("/menu", methods=['GET', "POST"])
def MenuUpdates(): 
    # post request
    if(request.method == 'POST'):
        try:
            dish = request.get_json()
            token = request.headers.get('Authorization')
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_data = decoded_token['user']
            if(user_data['role'] == 'admin' and dish['name'] and dish['price'] and dish['availability'] and dish['store']):
                new_dish = Menu(name=dish['name'], price=dish['price'], availability=dish['availability'], store=dish['store'])
                db.session.add(new_dish)
                db.session.commit()

                return jsonify({'issue': False,'message': "dish added"})
            else:
                return jsonify({'issue': True, 'message': "Some data is missing"})
        except jwt.ExpiredSignatureError:
            return jsonify({'issue': True,'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'issue': True,'message': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'issue': True, 'message': e})


    # get request
    allMenu = Menu.query.all()
    Menu_list = []

    for dish in allMenu:
        dish_info = {
            
            'id': dish.id,
            'name': dish.name,
            'price': dish.price,
            'availability': dish.availability,
            'store': dish.store
        }
        Menu_list.append(dish_info)

    return jsonify({'message': "Menu", "Menu": Menu_list})


@app.route("/dish/<int:dish_id>", methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def paramMenu(dish_id):
    # dish = Menu.query.filter_by(id=1).first()
    # dish = Menu.query.get(dish_id)
    dish = db.session.get(Menu, dish_id)
    if(dish):
        try:
            if(request.method == 'GET'):
                dish_dict = {
                    'id': dish.id,
                    'name': dish.name,
                    'price': dish.price,
                    'availability': dish.availability,
                    'store': dish.store
                }

                return jsonify({'message': 'Single Dish', 'Dish': dish_dict})
            
            token = request.headers.get('Authorization')
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_data = decoded_token['user']
            if(user_data['role'] == 'admin'):
                if(request.method == 'DELETE'):
                    db.session.delete(dish)
                    db.session.commit()
                    return jsonify({'message': f'Dish with ID {dish_id} has been deleted'})
                
                data = request.get_json()
                if 'price' in data:
                    dish.price = data['price']
                if 'availability' in data:
                    dish.availability = data['availability']
                if 'store' in data:
                    dish.store = data['store']
                db.session.commit()
                return jsonify({'message': f'Dish with ID {dish_id} has been updated'})
            else:
                return jsonify({'issue': True, 'message': 'authorization is required'})
            
        except jwt.ExpiredSignatureError:
            return jsonify({'issue': True,'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'issue': True,'message': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'issue': True, 'message': e})
    else:
        return jsonify({'message': 'Dish not found'}) 


@app.route('/order', methods=['GET','POST'])
def orders():
    if(request.method == "POST"):
        data = request.get_json()
        try:
            allMenu = Menu.query.all()
            Menu_list = {}
            for dish in allMenu:
                dish_info = {
                    'id': dish.id,
                    'name': dish.name,
                    'price': dish.price,
                    'availability': dish.availability,
                    'store': dish.store
                }
                Menu_list.update({dish.name: dish_info})
            total = 0
            items = ""
            orders = data['items']
            
            for i in orders:
                if(Menu_list[i['name']]['availability'] == 'Yes' and Menu_list[i['name']]['store'] == data['store']):
                    items += i['name'] + ", "
                    total += i['price']
                else:
                    return jsonify({'issue': True, 'message': f"Item {i['name']} is not available at {data['store']}"})
            temp = datetime.date.today()
            today = temp.strftime('%d/%m/%y')
            flag = False
            for each in promocode:
                if(each['name'] == data['promocode'] and total >= each['minimum']):
                    flag = True
                    total = (total*each['discount'])/100
            
            if(flag == False and data['promocode'] != ""):
                return jsonify({'issue': True, 'message': 'promocode is invalid'})
            
            new_order = Orders(items=items, totalBill=total, name=data['name'], email=data['email'], date=today,store=data['store'], promocode=data['promocode'], status="received")

            db.session.add(new_order)
            db.session.commit()
            return jsonify({'message': "order added", 'order': {"items":items, "totalBill":total, "name":data['name'], "email":data['email'], "date":today,"store":data['store'], "promocode":data['promocode'], "status":"received"}})
        except Exception as e:
            return jsonify({'issue': True, 'message': f'something is wrong at {str(e)}'})


     # Get request    
    allOrders = Orders.query.all()
    order_list = []

    for order in allOrders:
        order_info = {
            'id': order.id,
            "items" : order.items,
            "totalBill" : order.totalBill,
            "name" : order.name,
            "email" : order.email,
            "date" : order.date,
            "store" : order.store,
            "promocode" : order.promocode  ,
            "status" : order.status  ,
        }
        order_list.append(order_info)

    return jsonify({'message': "All orders", "orders": order_list})


@app.route('/order/<int:id>', methods=['GET', 'PUT', "PATCH", "DELETE"])
def paramOrders(id):
    order = db.session.get(Orders, id)
    if(order):
        if(request.method == 'GET'):
            order_dict = {
                'id': order.id,
                'items': order.items,
                "totalBill" : order.totalBill,
                "name" : order.name,
                "email" : order.email,
                "date" : order.date,
                "store" : order.store,
                "promocode" : order.promocode,
                "status" : order.status,

            }
            return jsonify({'message': "Single Order", "order": order_dict})
        
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_data = decoded_token['user']
        if(user_data['role'] == 'admin' or user_data['role'] == 'staff'):
            
            if(request.method == 'DELETE'):

                db.session.delete(order)
                db.session.commit()
                return jsonify({'message': f'Order with ID {id} has been deleted'})
            
            
            data = request.get_json()
            data_json = json.dumps(data)
            data_dict = json.loads(data_json)
        
            if 'items' in data_dict:
                items = ""
                for i in data_dict['items']:
                    items += i['name'] + ", "
                order.items = items
            if 'totalBill' in data_dict:
                order.totalBill = data_dict['totalBill']
            if 'email' in data_dict:
                order.email = data_dict['email']
            if 'name' in data_dict:
                order.name = data_dict['name']
            if 'date' in data_dict:
                order.date = data_dict['date']
            if 'store' in data_dict:
                order.store = data_dict['store']
            if 'status' in data_dict:
                order.status = data_dict['status']
            db.session.commit()
            return jsonify({'message': f'Order with ID {id} has been updated'})
        else:
            return jsonify({'issue': True, 'message': 'Authorization is required'}) 
    else:
        return jsonify({'issue': True,'message': 'Order not found'}) 


@app.route('/order/filter/<string:state>', methods=['GET'])
def getReadyOrders(state):
    try:
        allOrders = Orders.query.all()
        order_list = []
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_data = decoded_token['user']
        if(user_data['role'] == 'admin'):
            for order in allOrders:
                if(order.status == state):
                    order_info = {
                        'id': order.id,
                        "items" : order.items,
                        "totalBill" : order.totalBill,
                        "name" : order.name,
                        "email" : order.email,
                        "date" : order.date,
                        "store" : order.store,
                        "promocode" : order.promocode  ,
                        "status" : order.status  ,
                    }
                    order_list.append(order_info)
                if(len(order_list) == 0):
                    return jsonify({'message': 'Order not found'}) 
                else:
                    return  jsonify({'issue': False, 'message':f'filtered orders where status is {state}', 'order': order_list})
        else:
            return jsonify({'issue': True,'message': 'Authorization is required'}) 

    except jwt.ExpiredSignatureError:
            return jsonify({'issue': True,'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
            return jsonify({'issue': True,'message': 'Invalid token'}), 401
    except Exception as e:
            return jsonify({'issue': True, 'message': e})


@app.route("/analysis", methods=['GET'])
def getAnalysis():
    try:
        token = request.headers.get('Authorization')
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_data = decoded_token['user']
        if(user_data['role'] == 'admin'):
            delivered_orders = Orders.query.filter_by(status="Delivered").all()
            revenue = 0
            topItems = {}
            for each in delivered_orders:
                revenue += each.totalBill
                items = each.items.split(",")
                for i in items:
                    if(i != " "):
                        i = i.strip()
                        if i in topItems:
                            topItems[i] += 1
                        else:
                            topItems[i] = 1
                        
            
            return jsonify({'issue': False, 'message': "Analysis", 'revenue': revenue, 'Top-Items': topItems})

        else:
            return jsonify({'issue': True,'message': 'Authorization is required'}) 
    except Exception as e:
            return jsonify({'issue': True, 'message': str(e)})


if __name__ == '__main__':
    app.run(debug=True)

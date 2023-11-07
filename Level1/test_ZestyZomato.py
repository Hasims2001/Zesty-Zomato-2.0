import unittest
from ZestyZomato import app
from flask import Flask
import json

class ZomatoTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    # def test_welcome(self):
    #     response = self.app.get('/')
    #     data = json.loads(response.data)
    #     self.assertEqual(data['message'], 'Welcome to Zesty Zomato')
    
    # def test_dishes(self):
    #     # testing post and get
    #     newDish = {"name": "non veg", "price": 350, "availability": "Yes", "store":"Ahemdabad, Gujarat"}
    #     response = self.app.post("/menu", json=newDish)
    #     data = json.loads(response.data)
    #     self.assertEqual(data['message'], 'dish added')

    #     response = self.app.get('/menu')
    #     data = json.loads(response.data)
    #     self.assertEqual(data['message'], 'Menu') 
    
    # def test_dish(self):
    #     # testing put/patch, get, delete
    #     updateDish  = {"price": 1000, "availability": "Yes", "store":"Ahemdabad, Gujarat"}
    #     response = self.app.patch("/dish/13", json=updateDish)
    #     data = json.loads(response.data)
    #     self.assertEqual(data['message'], 'Dish with ID 13 has been updated')

    #     res = self.app.get('/dish/13')
    #     data = json.loads(res.data)
    #     self.assertEqual(data['message'], "Single Dish")
    #     self.assertEqual(data['Dish']['price'],  1000)


    #     res = self.app.delete('/dish/13')
    #     data  = json.loads(res.data)
    #     self.assertEqual(data['message'], 'Dish with ID 13 has been deleted')


    # def test_edge_case(self):
    #     res = self.app.get('/dish/0')
    #     data = json.loads(res.data)
    #     self.assertEqual(data['message'], "Dish not found")


    # def test_orders(self):
    #   #testing post
    #     new_order ={
    #     "name": "alx",
    #     "email": "alx@gmail.com",
    #     "items": [
    #         {
    #     "name": "Veg kadai",
    #     "price": 450
    #     },{
    #     "name": "Pancakes",
    #     "price": 90
    #     }],
    #     "promocode": "",
    #     "store": "Ahemdabad, Gujarat"
    # }
                
    #     res = self.app.post('/order', json=new_order)
    #     data = json.loads(res.data)
    #     self.assertEqual(data['message'], 'order added')
    #     self.assertEqual(data['order']['status'], 'received')

    # def test_order(self):
        # testing get, patch, delete
        # res = self.app.patch('/order/3', json={'name': "xyz"})
        # data = json.loads(res.data)
        # self.assertEqual(data['message'], f"Order with ID 3 has been updated")
        

        # res = self.app.get('/order/3')
        # data = json.loads(res.data)
        # self.assertEqual(data['message'], 'Single Order')
        # self.assertEqual(data['order']['name'], "xyz")
        

        # res = self.app.delete('/order/3')
        # data = json.loads(res.data)
        # self.assertEqual(data['message'], "Order with ID 3 has been deleted")


        # res = self.app.get('/order/3')
        # data = json.loads(res.data)
        # self.assertEqual(data['message'], 'Order not found')

    def test_order_filter(self):
        res = self.app.get("/order/filter/ready")
        data = json.loads(res.data)
        self.assertEqual(data['message'], "filtered orders where status is ready")
    
    def test_order_filter_edgecase(self):
        res = self.app.get('/order/filter/Invalid')
        data = json.loads(res.data)
        self.assertEqual(data['message'], "Order not found")

if __name__ == '__main__':
    unittest.main()

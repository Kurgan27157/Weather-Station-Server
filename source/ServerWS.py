from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps

base = create_engine('sqlite:///Weather.db')

app = Flask(__name__)
api = Api(app)

class All_Dates(Resource):
	def get(self, sensor):

		conn = base.connect()

		query = conn.execute("SELECT timestamp FROM '{table}'".format(table=sensor))
		return {'dates': [i[0] for i in query.cursor.fetchall()]}

class Sensors(Resource):
    def get(self,sensor,time1,time2, limit):
    	conn = base.connect()
    	query = conn.execute("SELECT * FROM '{table}' WHERE (timestamp>='{start}' and timestamp<='{end}') ORDER BY timestamp DESC Limit '{lim}'".format(table=sensor,start=time1, end=time2,lim=limit))
        result =  {sensor:[dict(zip(tuple (query.keys()) ,i)) for i in query.cursor ]}
        return result

       
api.add_resource(Sensors, '/Sensors/<sensor>/<time1>/<time2>/<limit>')
api.add_resource(All_Dates, '/All_Dates/<sensor>')

if __name__ == '__main__':
    app.run(host="0.0.0.0")


from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps

base = create_engine('sqlite:///Weather.db')

app = Flask(__name__)
api = Api(app)


class AllDates(Resource):

    def get(self, sensor):
        """
        :param sensor:
        :return: json object with all dates from DB
        """
        conn = base.connect()
        query = conn.execute("SELECT timestamp FROM '{table}'".format(table=sensor))
        return {'dates': [i[0] for i in query.cursor.fetchall()]}


class Sensors(Resource):

    def get(self, sensor, time1, time2, limit):
        """

        :param sensor:
        :param time1:
        :param time2:
        :param limit:
        :return: json object with values from choosen sensor and choosen time
        """
        conn = base.connect()
        query = conn.execute(" SELECT * FROM ' {table} ' WHERE (timestamp >= ' {start} '\
                              and timestamp <= ' {end} ') ORDER BY timestamp DESC Limit ' {lim} '"\
                              .format(table=sensor, start=time1, end=time2,lim=limit))
        result = {sensor: [dict(zip(tuple(query.keys()), i)) for i in query.cursor]}
        return result

api.add_resource(Sensors, '/Sensors/<sensor>/<time1>/<time2>/<limit>')
api.add_resource(All_Dates, '/All_Dates/<sensor>')

if __name__ == '__main__':
    app.run(host="0.0.0.0")


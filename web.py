import os
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Table, MetaData, select
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r'/*': {"origins": "https://mohsenagi.github.io"}})
DATABASE_URL = os.environ['DATABASE_URL']

engine = create_engine(DATABASE_URL, connect_args={'sslmode':'require'}) # ssl mode is required for heroku postgre db server
connection = engine.connect()
metadata = MetaData()
city = Table('city', metadata, autoload=True, autoload_with=engine) # Reflecting Database Objects

def josonify_sql(sql_result):
    a = []
    for row in sql_result:
        d = {}
        # row.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in row.items():
            try:
                jsonify(value)
                d[column] = value
            except:
                d[column] = float(value)
        a.append(d)
    return jsonify(a)

@app.route("/")
def home():
	return "My Server"

@app.route("/add", methods = ['POST'])
def add():
    content = request.get_json()
    connection.execute(city.insert(), content) # content should have the same keys as db columns
    result = connection.execute('select * from city where id = ( select max(id) from city)')
    return josonify_sql(result), 200

@app.route("/clear", methods = ['POST','GET'])
def clear():
    connection.execute(city.delete())
    return jsonify({}), 200

@app.route("/all", methods = ['POST','GET'])
def all():
    result = connection.execute(select([city]))
    return josonify_sql(result), 200

@app.route("/update", methods = ['POST'])
def update():
    content = request.get_json()
    if 'key' not in content:
        return jsonify({"msg":"There must be a 'key' attribute"}), 400
    key = content['key']
    content.pop('key')
    connection.execute(city.update().where(city.c.id == key), content)
    return jsonify({}), 200

@app.route("/delete", methods = ['POST'])
def delete():
    content = request.get_json()
    if 'key' not in content:
        return jsonify({"msg":"There must be a 'key' attribute"}), 400
    key = content['key']
    connection.execute(city.delete().where(city.c.id == key))
    return jsonify({}), 200

if __name__ == '__main__':
    app.run()
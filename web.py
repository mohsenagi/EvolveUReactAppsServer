import os
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Table, MetaData, select

app = Flask(__name__)
DATABASE_URL = os.environ['DATABASE_URL']

engine = create_engine(DATABASE_URL, sslmode='require')
connection = engine.connect()
metadata = MetaData()
city = Table('city', metadata, autoload=True, autoload_with=engine) # Reflecting Database Objects

@app.route("/")
def home():
	return "My Server"

@app.route("/add", methods = ['POST'])
def add():
    content = request.get_json()
    connection.execute(city.insert(), content) # content should have the same keys as db columns
    return jsonify({}), 200

@app.route("/clear", methods = ['POST','GET'])
def clear():
    connection.execute(city.delete())
    return jsonify({}), 200

@app.route("/all", methods = ['POST','GET'])
def all():
    result = connection.execute(select([city]))
    a = []
    for row in result:
        d = {}
        # row.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in row.items():
            try:
                jsonify(value)
                d[column] = value
            except:
                d[column] = float(value)
        a.append(d)
    return jsonify(a), 200

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
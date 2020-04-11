import os
from flask import Flask, jsonify, request
import psycopg2
from flask_cors import CORS
from decimal import Decimal

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://mohsenagi.github.io", "http://localhost:3000"]}}) # all routes are accessible only from this address
os.environ['DATABASE_URL'] = "postgres://ltxbaneafvkfyg:21161a47b691f8e9ed63e21654c71cc1f800900a34d2a6d3aa3b9e1aa38c61c8@ec2-54-197-34-207.compute-1.amazonaws.com:5432/ddi6ch5pjrkivt"
DATABASE_URL = os.environ['DATABASE_URL']

def jsonify_sql(header, sql_result):
    a = []
    for row in sql_result:
        d = {}
        for i in range(0, len(header)):
            if type(row[i]) is Decimal:
                d[header[i][0]] = float(row[i])
            else:
                d[header[i][0]] = row[i]
        a.append(d)
    return jsonify(a)

def execute_sql(sql, data=[], returning=False):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(sql, data)
    if returning==True:
        sql_result = cur.fetchall()
        json_result = jsonify_sql(cur.description, sql_result)
    else:
        json_result = jsonify({})
    conn.commit()
    cur.close()
    conn.close()
    return json_result

@app.route("/")
def home():
	return "My Server"

@app.route("/add", methods = ['POST'])
def add():
    content = request.get_json()
    sql = "INSERT INTO city VALUES (DEFAULT, %s, %s, %s, %s) RETURNING id;"
    data = [content['Name'], content['Latitude'], content['Longitude'], content['Population']]
    json_result = execute_sql(sql, data, returning=True)
    # json_result = execute_sql(sql="SELECT * FROM city WHERE id = (SELECT max(id) FROM city);", returning=True)
    return json_result, 200

@app.route("/clear", methods = ['POST'])
def clear():
    json_result = execute_sql(sql='DELETE FROM city;')
    return json_result, 200

@app.route("/all", methods = ['GET'])
def all():
    json_result = execute_sql(sql='SELECT * FROM city;', returning=True)
    return json_result, 200

@app.route("/update", methods = ['POST'])
def update():
    content = request.get_json()
    if 'key' not in content:
        return jsonify({"msg":"There must be a 'key' attribute"}), 400
    sql = 'UPDATE city SET ("Name", "Latitude", "Longitude", "Population")=(%s, %s, %s, %s) WHERE id=%s;'
    data = [content['Name'], content['Latitude'], content['Longitude'], content['Population'], content['key']]
    json_result = execute_sql(sql, data)
    return json_result, 200

@app.route("/delete", methods = ['POST'])
def delete():
    content = request.get_json()
    if 'key' not in content:
        return jsonify({"msg":"There must be a 'key' attribute"}), 400
    sql = 'DELETE FROM city WHERE id=%s;'
    data = [content['key']]
    json_result = execute_sql(sql, data)
    return json_result, 200

if __name__ == '__main__':
    app.run(debug=True)
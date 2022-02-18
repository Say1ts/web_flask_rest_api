from flask import Flask, jsonify
import data_handler

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

data = data_handler.load_data()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/geonameid/<int:geonameid>', methods=['GET'])
def show_info_geonameid(geonameid):
    return jsonify(data_handler.show_info_by_geonameid(geonameid, data))


@app.route('/page/<int:page>&count=<int:divider>', methods=['GET'])
def show_page(page, divider):
    return jsonify(data_handler.show_info_page(page, divider, data))


@app.route('/compare/<name_1>&<name_2>', methods=['GET'])
def compare_two_towns(name_1, name_2):
    return jsonify(data_handler.show_info_for_two_towns(name_1, name_2, data))


@app.route('/guess_town_name/<name>', methods=['GET'])
def guess_town(name):
    return jsonify(data_handler.show_guessed_town_name(name, data))


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(data_handler.show_not_found())


if __name__ == '__main__':
    app.run(port=8000)

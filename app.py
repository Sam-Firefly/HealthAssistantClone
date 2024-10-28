from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def generate_response(query: str) -> str:
    return f"这是机器人的回复：{query}"

@app.route('/api/response', methods=['POST'])
def get_response():
    query = request.json.get('message', '')
    response = generate_response(query)
    return jsonify({'reply': response})

if __name__ == '__main__':
    app.run(debug=True)
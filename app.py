from flask import Flask, request, jsonify
from flask_cors import CORS
from llm.server_v1 import HealthAssistantServer, init_logging

app = Flask(__name__)
CORS(app)
global server


def generate_response(query: str) -> str:
    if query == "stop":
        server.stop()
        return ""

    return server.generate(query)


@app.route('/api/response', methods=['POST'])
def get_response():
    query = request.json.get('message', '')
    response = generate_response(query)
    return jsonify({'reply': response})


if __name__ == '__main__':
    init_logging()
    server = HealthAssistantServer()
    app.run(debug=False)

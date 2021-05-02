from flask import Flask, request, jsonify
from Pop3Client import Pop3Client

app = Flask(__name__)


@app.route("/email", methods=["GET"])
def send_message():
    msg_from = request.args.get("from")
    if not msg_from:
        return "Missing argument: from", 400

    inet_addr, port = msg_from.split(":")
    try:
        pop3client = Pop3Client(inet_addr, int(port), enforce_banner=False, banner_wait_time=1, delete_after_retrieve=True)
    except ConnectionRefusedError:
        return f"POP3 Service Unavailable - {inet_addr}:{port}"
    result, mails = pop3client.fetch_message()
    if result == "OK":
        return jsonify(mails)
    else:
        return "internal error:"+result, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

from flask import Flask, request
from SmtpClient import SmtpClient

app = Flask(__name__)


@app.route("/email", methods=["GET"])
def send_message():
    msg_from = request.args.get("from")
    msg_to = request.args.get("to")
    msg = request.args.get("message")
    if not (msg_from and msg_to and msg):
        return "Missing at least one argument of from/to/message", 400
    inet_addr, port = msg_from.split(":")
    try:
        smtp_client = SmtpClient(inet_addr, int(port))
    except ConnectionRefusedError:
        return f"SMTP Service Unavailable - {inet_addr}:{port}", 500

    result, explain = smtp_client.send_message({"msg_from": msg_from, "msg_to": [msg_to], "msg": msg})
    if result == 200:
        return "Message sent successfully"
    else:
        return f"failed to send message: {explain}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)

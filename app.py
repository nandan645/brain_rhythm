from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/neural-clocks")
def neural_clocks():
    return render_template("neural_clocks.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

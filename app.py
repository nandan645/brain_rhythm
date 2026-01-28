from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/neural-clocks")
def neural_clocks():
    return render_template("neural_clocks.html")

@app.route("/human-study")
def human_study():
    return render_template("human_study.html")

@app.route("/quantum-computer")
def quantum_computer():
    return render_template("quantum_computer.html")

@app.route("/medical/cancer")
def cancer():
    return render_template("cancer.html")

@app.route("/medical/schizophrenia")
def schizophrenia():
    return render_template("schizophrenia.html")

@app.route("/medical/alzheimers")
def alzheimers():
    return render_template("alzheimers.html")

@app.route("/medical/thrombosis")
def thrombosis():
    return render_template("thrombosis.html")

@app.route("/proteins")
def protein():
    return render_template("protein.html")

@app.route("/proteins/circuit")
def circuit():
    return render_template("circuit.html")

@app.route("/proteins/vortex-synthesis")
def vortex_synthesis():
    return render_template("vortex_synthesis.html")

@app.route("/proteins/water")
def water():
    return render_template("water.html")

@app.route("/proteins/e-pi-phi")
def e_pi_phi():
    return render_template("e_pi_phi.html")

@app.route("/proteins/up-down-conversion")
def up_down_conversion():
    return render_template("up_down_conversion.html")

@app.route("/conference/matrisneha")
def matrisneha():
    return render_template("matrisneha.html")

@app.route("/conference/garima")
def garima():
    return render_template("garima.html")

@app.route("/conference/surobane")
def surobane():
    return render_template("surobane.html")

if __name__ == "__main__":
    app.run()

# gunicorn app:app --bind 0.0.0.0:8080 --workers 13 --threads 4

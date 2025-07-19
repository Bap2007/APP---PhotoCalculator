from flask import Flask, render_template, request 
import os

app = Flask(__name__)

def calculate_exposure(f1, iso1, t1, f2=None, iso2=None, t2=None):
    ev_test = t1 * (iso1 / (f1 ** 2))
    result, final_values = "", {}

    if t2 is None and f2 and iso2:
        t2 = ev_test * (f2 ** 2) / iso2
        t2 = round(t2)
        minutes = t2 // 60
        seconds = t2 % 60
        result = f"Shutter speed needed: {minutes}min{seconds}s"
        final_values = {"f": f2, "iso": iso2, "t": t2}
    elif iso2 is None and f2 and t2:
        iso2 = ev_test * (f2 ** 2) / t2
        result = f"ISO needed: {round(iso2)}"
        final_values = {"f": f2, "iso": iso2, "t": t2}
    elif f2 is None and iso2 and t2:
        f2_squared = t2 * iso2 / ev_test
        f2 = f2_squared ** 0.5
        result = f"Aperture needed: f/{round(f2, 1)}"
        final_values = {"f": f2, "iso": iso2, "t": t2}
    else:
        result = "Please leave exactly one target setting blank."
    return result, final_values

def generate_advice(settings):
    if not settings:
        return ""

    advice = []

    f = settings.get("f")
    iso = settings.get("iso")
    t = settings.get("t")

    if iso:
        if iso > 3200:
            advice.append(
                "ISO above 3200 can introduce significant noise, especially on high-resolution sensors. "
                "Use dark frame subtraction or noise reduction if shooting with a full-frame camera."
            )
        elif iso < 400:
            advice.append(
                "ISO below 400 may reduce noise but will require longer exposures or wider apertures."
            )

    if f:
        if f < 2.8:
            advice.append(
                "Using a wide aperture (e.g., f/2.0) allows more light but reduces depth of field. "
                "Ensure your lens performs well wide open to avoid coma and aberrations at the edges."
            )
        elif f > 8:
            advice.append(
                "Using a very small aperture (e.g., f/11+) in astrophotography isn't recommended. "
                "It limits light too much and can introduce diffraction, reducing sharpness."
            )

    if t:
        if t > 20:
            advice.append(
                "Long exposures above 20 seconds without tracking may cause star trails. "
                "Use the 500 rule or a star tracker to maintain pinpoint stars."
            )
        elif t < 1:
            advice.append(
                "Very short exposures may underexpose faint stars or the Milky Way. "
                "Use high ISO and a fast lens to compensate."
            )

    return "<br>".join(advice)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    advice = ""
    if request.method == "POST":
        try:
            f1 = float(request.form["f1"])
            iso1 = float(request.form["iso1"])
            t1 = float(request.form["t1"])

            f2 = request.form["f2"]
            iso2 = request.form["iso2"]
            t2 = request.form["t2"]

            f2 = float(f2) if f2 else None
            iso2 = float(iso2) if iso2 else None
            t2 = float(t2) if t2 else None

            result, settings = calculate_exposure(f1, iso1, t1, f2, iso2, t2)
            advice = generate_advice(settings)
        except Exception as e:
            result = f"Error: {e}"
    return render_template("index.html", result=result, advice=advice)


port = int(os.environ.get("PORT", 10000))  # Use assigned port or default to 10000

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
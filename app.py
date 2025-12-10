from flask import Flask, render_template, request
import random
import os
import json
from datetime import datetime

app = Flask(__name__)

# Paths for JSON storage
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
COIN_FILE = os.path.join(DATA_DIR, "coin_flips.json")


def ensure_data_file():
    """Make sure data directory and coin_flips.json exist and are a JSON list."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(COIN_FILE):
        with open(COIN_FILE, "w") as f:
            json.dump([], f, indent=4)


def load_runs():
    """Load previous coin flip runs from JSON."""
    ensure_data_file()
    try:
        with open(COIN_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except json.JSONDecodeError:
        # If somehow corrupted, treat as empty list
        return []


def save_runs(runs):
    """Save list of runs to JSON."""
    ensure_data_file()
    with open(COIN_FILE, "w") as f:
        json.dump(runs, f, indent=4)


@app.route("/")
def index():
    """Home page showing how many simulations have been run."""
    runs = load_runs()
    total_runs = len(runs)
    return render_template("index.html", total_runs=total_runs)


@app.route("/coin", methods=["GET", "POST"])
def coin():
    error = None
    results = None

    if request.method == "POST":
        num_flips_str = (request.form.get("num_flips") or "").strip()

        try:
            num_flips = int(num_flips_str)
        except ValueError:
            error = "Please enter a valid whole number."
            return render_template("page1.html", error=error, results=results)

        if num_flips < 1 or num_flips > 20:
            error = "Number of flips must be between 1 and 20."
            return render_template("page1.html", error=error, results=results)

        # Do the simulation
        flips = [random.choice(["Heads", "Tails"]) for _ in range(num_flips)]
        heads = flips.count("Heads")
        tails = flips.count("Tails")

        results = {
            "num_flips": num_flips,
            "flips": flips,
            "heads": heads,
            "tails": tails,
        }

        # Save run to JSON
        runs = load_runs()
        runs.append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "num_flips": num_flips,
                "flips": flips,
                "heads": heads,
                "tails": tails,
            }
        )
        save_runs(runs)

    return render_template("page1.html", error=error, results=results)


if __name__ == "__main__":
    app.run(debug=True)

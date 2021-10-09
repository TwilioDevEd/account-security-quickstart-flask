#!/usr/bin/env python3
from twofa import app, init_db


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
    # app.run(debug=True, host='0.0.0.0', port=8080)

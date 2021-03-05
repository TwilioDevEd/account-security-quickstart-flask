from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from .config import config_classes
from .database import db, migrate

app = Flask(__name__)

# load the instance config
environment = app.config.get('ENV', 'production')
app.config.from_object(config_classes[environment])

db.init_app(app)
migrate.init_app(app, db)

csrf = CSRFProtect(app)

# from .database import init_db  # noqa: F401, E402
# from .models import User  # noqa: E402

login_manager = LoginManager()
login_manager.init_app(app)

import twofa.models  # noqa: F401, E402

from .models import User  # noqa: E402
login_manager.user_loader(User.load_user)


from . import views  # noqa: F401, E402

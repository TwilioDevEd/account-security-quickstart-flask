from flask import Flask
from flask_dotenv import DotEnv
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from .config import Config

app = Flask(__name__)
app.config.from_object(Config)
env = DotEnv(app)

csrf = CSRFProtect(app)

from .database import init_db  # noqa: F401, E402
from .models import User  # noqa: E402

login_manager = LoginManager()
login_manager.user_loader(User.load_user)
login_manager.init_app(app)

from . import views  # noqa: F401, E402

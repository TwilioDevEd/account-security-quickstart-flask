import flask

from authy.api import AuthyApiClient
from flask_login import login_required, login_user, logout_user, current_user

from . import app, login_manager
from .database import db_session
from .decorators import twofa_required
from .forms import LoginForm, RegistrationForm, TokenVerificationForm
from .models import User


authy_api = AuthyApiClient(app.config.get('ACCOUNT_SECURITY_API_KEY'))


@app.route('/protected')
@login_required
@twofa_required
def protected():
    return flask.render_template('protected.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user, remember=True)
        form.user.is_authenticated = True
        db_session.add(form.user)
        db_session.commit()
        next = flask.request.args.get('next')
        return flask.redirect(next or flask.url_for('protected'))
    return flask.render_template('login.html', form=form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    current_user.is_authenticated = False
    db_session.add(current_user)
    db_session.commit()
    flask.session['authy'] = False
    logout_user()
    return flask.redirect('/login')


@app.route('/', methods=['GET', 'POST'])
def index():
    return flask.redirect('/login')


login_manager.unauthorized_handler(index)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        authy_user = authy_api.users.create(
            form.email.data,
            form.phone_number.data,
            form.country_code.data,
        )
        if authy_user.ok():
            user = User(
                form.username.data,
                form.email.data,
                form.password.data,
                authy_user.id,
                is_authenticated=True
            )
            user.authy_id = authy_user.id
            db_session.add(user)
            db_session.commit()
            login_user(user, remember=True)
            return flask.redirect('/protected')
        else:
            form.errors['non_field'] = []
            for key, value in authy_user.errors():
                form.errors['non_field'].append(
                    '{key}: {value}'.format(key=key, value=value)
                )
    return flask.render_template('register.html', form=form)


@app.route('/2fa', methods=['GET', 'POST'])
@login_required
def twofa():
    form = TokenVerificationForm(current_user.authy_id)
    if form.validate_on_submit():
        flask.session['authy'] = True
        return flask.redirect('/protected')
    return flask.render_template('2fa.html', form=form)


@app.route('/token/sms', methods=['POST'])
@login_required
def token_sms():
    sms = authy_api.users.request_sms(current_user.authy_id, {'force': True})
    if sms.ok():
        return flask.Response('SMS request successful', status=200)
    else:
        return flask.Response('SMS request failed', status=503)


@app.route('/token/voice', methods=['POST'])
@login_required
def token_voice():
    call = authy_api.users.request_call(current_user.authy_id, {'force': True})
    if call.ok():
        return flask.Response('Call request successful', status=200)
    else:
        return flask.Response('Call request failed', status=503)


@app.route('/token/onetouch', methods=['POST'])
@login_required
def token_onetouch():
    details = {
        'Authy ID': current_user.authy_id,
        'Username': current_user.username,
        'Reason': 'Demo by Account Security'
    }

    hidden_details = {
        'test': 'This is a'
    }

    response = authy_api.one_touch.send_request(
        int(current_user.authy_id),
        message='Login requested for Account Security account.',
        seconds_to_expire=120,
        details=details,
        hidden_details=hidden_details
    )
    if response.ok():
        flask.session['onetouch_uuid'] = response.get_uuid()
        return flask.Response('OneTouch request successfull', status=200)
    else:
        return flask.Response('OneTouch request failed', status=503)


@app.route('/onetouch-status', methods=['POST'])
@login_required
def onetouch_status():
    uuid = flask.session['onetouch_uuid']
    approval_status = authy_api.one_touch.get_approval_status(uuid)
    if approval_status.ok():
        if approval_status['approval_request']['status'] == 'approved':
            flask.session['authy'] = True
        return flask.Response(
            approval_status['approval_request']['status'],
            status=200
        )
    else:
        return flask.Response(approval_status.errros(), status=503)

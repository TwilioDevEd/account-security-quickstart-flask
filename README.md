<a href="https://www.twilio.com">
  <img src="https://static0.twilio.com/marketing/bundles/marketing/img/logos/wordmark-red.svg" alt="Twilio" width="250" />
</a>

# Twilio Account Security Quickstart - Two-Factor Authentication and Phone Verification

[![Build Status](https://github.com/TwilioDevEd/account-security-quickstart-flask/workflows/Flask/badge.svg)](https://github.com/TwilioDevEd/account-security-quickstart-flask/actions?query=workflow%3AFlask)

A simple Python and Flask implementation of a website that uses Twilio Account Security services to protect all assets within a folder. Additionally, it shows a Phone Verification implementation.

It uses four channels for delivery, SMS, Voice, Soft Tokens, and Push Notifications. You should have the [Authy App](https://authy.com/download/) installed to try Soft Token and Push Notification support.

#### Two-Factor Authentication Demo
- URL path "/protected" is protected with both user session and Twilio Two-Factor Authentication
- One Time Passwords (SMS and Voice)
- SoftTokens
- Push Notifications (via polling)

#### Phone Verification
- Phone Verification
- SMS or Voice Call

### Setup
This project is built using the [Flask](http://flask.pocoo.org/) web framework. It runs on Python 2.7+ and Python 3.4+.

1. To run the app locally, first clone this repository and `cd` into it.

1. Create and activate a new python3 virtual environment.

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

1. Install the requirements using pip.

    ```bash
    pip install -r requirements.txt
    ```

1. Copy the `.env.example` file to `.env`, and edit it to add your Application API Key.
   Can get/create one [here](https://www.twilio.com/console/authy/applications).

   ```
   ACCOUNT_SECURITY_API_KEY=<your API key>
   ```

1. Create Flask application variables for development
   
   ```bash
   export FLASK_APP=twofa 
   export FLASK_ENV=development
   ```

1. Run the migrations.

   ```bash
   flask db upgrade
   ```

1. Start the development server.

    ```bash
    flask run
    ```

## Meta

* No warranty expressed or implied. Software is as is. Diggity.
* [MIT License](LICENSE)
* Lovingly crafted by Twilio Developer Education.
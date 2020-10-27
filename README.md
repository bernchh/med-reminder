# Welcome to the med-reminder App!

This project allows you to schedule and receive reminders to take your medication via SMS. The app was developed for Twilio App Bootcamp and is written in Python using [Flask](http://flask.pocoo.org/) and [RQ](https://python-rq.org/).

## Setting Up

We assume that before you begin, you will have [Python](http://www.python.org/) and [pip](http://www.pip-installer.org/en/latest/) installed on your system and available at the command line.

Before you can run this project, you will need to set three system environment variables at .env.  These are:

* `TWILIO_ACCOUNT_SID` : [Get it from your Twilio Console](https://www.twilio.com/console).
* `TWILIO_AUTH_TOKEN` : Same as above.
* `TWILIO_PHONE_NUMBER` : A Twilio number that you own, that can be used for making calls and sending messages.  You can find a list of phone numbers you control (and buy another one, if necessary) [in the console](https://www.twilio.com/console/phone-numbers/incoming).

The next step is to make a .env (note the leading dot) file where we will store the environmental variables that will serve as configuration for our project. You will need to replace all the characters after the `=` with values from your Twilio account:
```
    TWILIO_ACCOUNT_SID=SID_HERE
    TWILIO_AUTH_TOKEN=TOKEN_HERE
    TWILIO_PHONE_NUMBER=+16518675309
```

An example is provided at .env.config.example.

## Installing Services

You will need to have an instance of [Redis](https://redis.io/topics/quickstart) installed and running. It is also recommended to have [Ngrok](https://ngrok.com/download) installed to expose the Flask web app for testing.
    
Type below to install Redis and Ngrok on macOS:
```
    brew update
    brew install redis
    brew cask install ngrok
```

## Running the application

1. Clone this repository. Navigate to the folder with the source code on your machine in a terminal window.

1. From there we recommend creating a [virtualenv](https://docs.python.org/3/library/venv.html) and activating it to avoid installing dependencies globally on your computer.

    `virtualenv -p med-reminder env`
    
    `source env/bin/activate`

1. Install dependencies:

    `pip install -r requirements.txt`

1. Start Redis:

    `redis-server /usr/local/etc/redis.conf`

1. Spin up RQ worker to take on jobs:

    `rq worker --with-scheduler`

1. Run the web app:

    `python app.py`

1. Open the app in your [browser](http://localhost:8080/).

## Begin Sending Reminders

1. Expose your web app with ngrok in order to receive Twilio SMS requests.

    `ngrok http 8080`
    
1. Copy the ngrok public url shown in your terminal. It should look similar to the example below. 

        Session Status                online
        Version                       2.3.35
        Web Interface                 http://127.0.0.1:4040
        Forwarding                    http://92832de0.ngrok.io -> localhost:8080
        Forwarding                    https://92832de0.ngrok.io -> localhost:8080
        
        Connnections                  ttl     opn     rt1     rt5     p50     p90
                                      0       0       0.00    0.00    0.00    0.00

1. Go to the [Twilio Console](https://www.twilio.com/console/phone-numbers/incoming) to configure your Twilio phone number to make a request to your public url when a message comes in.

1. SMS to the Twilio phone number you have specified and watch the magic happen!

```
Commands Available:
1. List
2. Remind <medicine> <dosage per day (1-5)> <how many days>. E.g. Remind Paracetamol 2 3
3. Delete <medicine>
```

## Also Recommended

* [Redis Commander](https://github.com/joeferner/redis-commander), an open-source web management tool to manage Redis

* [RQ dashboard](https://github.com/Parallels/rq-dashboard), a lightweight webbased monitor frontend for RQ

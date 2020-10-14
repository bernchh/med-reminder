from flask import Flask, request, Response
from twilio.twiml.messaging_response import Message, MessagingResponse

import reminder

app = Flask('med-reminder')


@app.route("/", methods=['GET', 'POST'])
def default():
    response = MessagingResponse()

    try:
        req = request.form['Body'].lower()
        reqArr = req.split(' ')

        phone_number = request.form['From']

        if (req == 'list'):
            response.message(reminder.show_reminder(phone_number))
        elif (reqArr[0] == 'remind'):
            try:
                medicine = reqArr[1].capitalize()
                dosage = int(reqArr[2])
                day = int(reqArr[3])

                if (dosage < 0 or dosage > 5 or day < 0):
                    raise Exception('Invalid dosage or day specified.')

                response.message(reminder.save_reminder(
                    phone_number, medicine, dosage, day))
            except:
                print('An exception has occurred.')
                response.message(
                    "Sorry! I couldn't understand your request. Please try again.")
        elif (reqArr[0] == 'delete'):
            try:
                response.message(reminder.delete_reminder(
                    phone_number, reqArr[1].capitalize()))
            except:
                print('An exception has occurred.')
                response.message(
                    "Sorry! I couldn't understand your request. Please try again.")
        else:
            raise Exception("Invalid request")
    except:
        response.message(
            'Commands Available:\n1. List\n2. Remind <medicine> <times to take per day (1 to 5)> <how many days>\nE.g. Remind Paracetamol 2 7.')

    print(response)
    return str(response)


app.run(debug=True, host='0.0.0.0', port=8080)

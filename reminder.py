from datetime import datetime, timedelta
import redis, os
from rq import Queue, cancel_job
from rq.registry import ScheduledJobRegistry

from sms import send_text_reminder

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
r = redis.from_url(redis_url)
queue = Queue(connection=r)


def save_reminder(phone_number, medicine, dosage, day):
    try:
        # Clear old reminders if any
        delete_reminder(phone_number, medicine)
        # Create new scheduled jobs to send sms
        schedule_reminder(phone_number, medicine, int(dosage), int(day))
        # Create reminder list to manage jobs
        r.hmset('reminder:' + phone_number + ':' + medicine,
                {'dosage': int(dosage), 'day': int(day)})
        return 'Reminder saved.'
    except:
        return 'Failed to save reminder.'


def show_reminder(phone_number):
    try:
        reminders = r.keys('reminder:' + phone_number + ':*')

        if (len(reminders) == 0):
            return 'You have no upcoming reminders.'

        msg = "Reply 'Delete <medicine>' to delete a reminder:\n\n"
        for i in reminders:
            msg += 'Delete %s \n' % i.decode('utf-8').split(':')[2]

        return msg
    except:
        return 'Failed to read reminder.'


# User requested to delete reminder. Also delete the scheduled sms jobs.
def delete_reminder(phone_number, medicine):

    try:

        reminders = r.keys('reminder:' + phone_number + ':' + medicine)
        if (len(reminders) == 0):
            raise Exception("Invalid Medicine.")
        # Delete jobs
        delete_sms_job(phone_number, medicine)
        # Delete medicine from reminder list
        r.hdel('reminder:' + phone_number + ':' + medicine, *['dosage', 'day'])

        return medicine + ' deleted.'
    except:
        return 'Failed to delete reminder.'


# Schedule the reminder to be sent as multiple sms jobs
# Follow schedule as recommended here:
# https://professionals.ufhealth.org/files/2011/11/1007-drugs-therapy-bulletin.pdf
def schedule_reminder(phone_number, medicine, dosage, day):
    try:
        job_id = (phone_number + ':' + medicine)
        cumulative_dosage = dosage * day
        time_now = datetime.now()

        if (dosage == 1):
            schedule = [9]
        if (dosage == 2):
            schedule = [9, 21]
        if (dosage == 3):
            schedule = [9, 14, 21]
        if (dosage == 4):
            schedule = [9, 14, 17, 21]
        if (dosage == 5):
            schedule = [5, 9, 13, 17, 21]

        schedule_next_reminder_recusion(
            schedule, cumulative_dosage, time_now, phone_number, medicine, job_id)

        print('done.')
    except:
        print('An exception has occurred scheduling the tasks.')


def schedule_next_reminder_recusion(schedule, remaining_dosage, time_now, phone_number, medicine, job_id):
    if remaining_dosage > 0:
        for scheduled_hour in schedule:

            if (time_now.hour <= scheduled_hour):

                # Set reminder time to the scheduled datetime
                datetime_to_schedule = datetime(
                    time_now.year, time_now.month, time_now.day) + timedelta(hours=scheduled_hour)

                print('remaining dosage: ' + str(remaining_dosage))
                print('scheduling for ' + str(datetime_to_schedule) +
                      ' | job_id is ' + (str(job_id) + ':' + str(remaining_dosage)))

                create_sms_job(datetime_to_schedule, phone_number, medicine, job_id=(
                    job_id + ':' + str(remaining_dosage)))
                remaining_dosage -= 1

        time_now = time_now + timedelta(days=1)
        schedule_next_reminder_recusion(
            schedule, remaining_dosage, time_now, phone_number, medicine, job_id)
    else:
        # Lastly, schedule a job to clear reminder list of this sequence after last sms is sent
        datetime_to_schedule = datetime(time_now.year, time_now.month, time_now.day) - timedelta(
            days=1) + timedelta(hours=schedule[-1]) + timedelta(minutes=1)

        print('scheduling delete job at ' + str(datetime_to_schedule))
        queue.enqueue_at(time_now, delete_reminder,
                         phone_number, medicine, job_id=job_id+':0')


# Delete all jobs with the matching key of phone_number and medicine
def delete_sms_job(phone_number, medicine):
    try:
        registry = queue.scheduled_job_registry

        print('Number of jobs in registry %s' % registry.count)

        for job_id in registry.get_job_ids():
            if ((phone_number + ':' + medicine) in job_id):
                registry.remove(job_id, delete_job=True)

        print('Number of jobs in registry %s' % registry.count)
        print('done.')
    except:
        print('An exception has occurred deleting sms tasks.')


# Enqueue each individual sms task into rq
def create_sms_job(datetime, phone_number, medicine, job_id):
    try:
        job = queue.enqueue_at(datetime, send_text_reminder,
                               phone_number, medicine, job_id=job_id)
        print(job)
        print('done.')
    except:
        print('An exception has occurred creating sms task.')

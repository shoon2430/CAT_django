from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
import time


class Scheduler:
    def __init__(self):
        self.sched = BackgroundScheduler()
        self.sched.start()
        self.job_id = ''

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        self.sched.shutdown()

    def kill_scheduler(self, job_id):
        try:
            self.sched.remove_job(job_id)
        except JobLookupError as err:
            print("fail to stop Scheduler: {err}".format(err=err))
            return

    # type, job_id, USER, function
    def scheduler(self, type, job_id, function, schedulerData):

        USER = schedulerData['USER']
        ticker = schedulerData['ticker']
        second = schedulerData['second']

        print("{type} Scheduler Start".format(type=type))
        if type == 'interval':
            self.sched.add_job(function, type, seconds=10, id=job_id, args=(type, job_id, USER, ticker))
        elif type == 'cron':
            self.sched.add_job(function, type,
                                                 #day_of_week='mon-fri',
                                                 hour='0',
                                                 minute='0',
                                                 second=second,
                                                 id=job_id, args=(type, job_id, USER, ticker))







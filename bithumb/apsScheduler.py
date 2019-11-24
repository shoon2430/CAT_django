from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler

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

        USER=""
        ticker=""
        second=""

        if len(schedulerData) != 0:
            USER = schedulerData['USER']
            ticker = schedulerData['ticker']
            second = schedulerData['second']

        print("{type} Scheduler Setting OK.".format(type=type))
        print("------------------------------")
        if type == 'BV': #변동성돌파
            #print("=== 변동성 돌파 ===")
            self.sched.add_job(function, 'cron',
                               # day_of_week='mon-fri',
                               #hour='0',
                               #minute='0',
                               #second=second,
                               second='*/10',
                               id=job_id, args=(type, job_id, USER, ticker))
        elif type == 'BB': #볼린저밴드
            #print("=== 볼린저 밴드 ===")
            self.sched.add_job(function, 'cron', #minute='*/5',
                                                 #second=second,
                                                 second='*/10',
                                                 id=job_id, args=(type, job_id, USER, ticker))
        elif type == 'ST': #단기투자
            #print("=== 단기 투자 ===")
            self.sched.add_job(function, 'cron', second=second,
                                                 id=job_id, args=(type, job_id, USER, ticker))
        if type == 'SAVE': #데이터 수집
            print("데이터수집 스케쥴러 실행")
            self.sched.add_job(function, 'cron',
                               second='*/3',
                               id=job_id)

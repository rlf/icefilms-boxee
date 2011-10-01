import threading
try: import mc
except: mc = False
import traceback
'''
Boxee Job Manager
An easily extensible threaded job manager that works in Boxee.

Written by /rob, 9 March 2011

Usage:
A common requirement of Boxee apps is to run some code at an interval without blocking the thread in which Boxee apps execute most of
their code.  To address this increasingly common requirement, I put together this interface to create your own arbitrarily defined jobs
and had them off to a "Job Manager" that runs in its own thread, letting your GUI onclick events and the like run without waiting for it
to return.

The most commonly needed job is for a webservice to be called every n seconds while video plays.  To use the JobManager in this instance,
simply create your job by extending the BoxeeJob class, instantiate the JobManager, add your custom Job to the manager, and start it
before executing mc.GetPlayer().Play().

Examples:

Instantiate object:
myJobManager = BoxeeJobManager()

Process job queue every 30 seconds (instead of default 10):
myJobManager = BoxeeJobManager(30)

Add job to Job Manager:

myJob = BoxeeJob()
myJobManager.addJob(myJob)

Start Job Manager:
myJobManager.start()

Stop Job Manager:
myJobManager.stop()

Extending the Job Object:
The job object is your primary interface for creating and executing Jobs with the Job Manager.  Here is an easy hello world example where
the string "Hello, world!" is printed to your Boxee debug log every ten seconds.

import mc
import jobmanager
class HelloWorldJob(jobmanager.BoxeeJob):
    # Add your own variables to constructor.
    def __init__(self, message, interval):
        self.message = message
        self.interval = interval
        # Be sure to always inherit the constructor from the base BoxeeJob class.
        jobmanager.BoxeeJob.__init__(self, "HelloWorld", interval)

    def process(self):
        # This is the base function that is always called for every job and the one you should extend.
        mc.LogDebug(self.message)
'''


'''
Job Manager Object
'''
class BoxeeJobManager(threading.Thread):
    def __init__(self, interval=10, limit=18000):
        self.jobs = {}
        self.elapsed = 0
        self.fault = False
        self.timer = threading.Event()
        self.interval = interval
        self.limit = limit
        threading.Thread.__init__(self)
        self.log("Initialized.")
        #self.joblock = threading.Lock()

    def stop(self):
        self.log("Stop command received.")
        self.fault = True
        return self.fault

    def run(self):
        # Main loop
        while self.fault is False:
            self.timer.wait(self.interval)
            self.elapsed = self.elapsed + self.interval
            try:
                self.process()
            except Exception, e:
                traceback.print_exc(10)
                self.stop()
                raise JobError("Encountered running job queue.", e)
            self.check()
            # Hard limit on length of Job Manager (default five hours)
            if self.elapsed >= self.limit:
                self.stop()

    def process(self):
        # Process job quue
        if self.jobs:
            #self.joblock.acquire()
            try:
                for job in self.jobs.values():
                    if job.elapsed >= job.interval:
                        self.log("Processing job: %s" % (job.name))
                        try:
                            job.process()
                            job.elapsed = 0
                        except Exception, e:
                            print "Encountered an error in %s, continuing the other jobs" % job.name
                            traceback.print_exc(10)
                            self.remove_job(job)
                    else:
                        job.elapsed = job.elapsed + self.interval
                        self.log("Skipping job: %s" % (job.name))
            finally:
                #self.joblock.release()
                pass

    def remove_job(self, boxee_job):
        #self.joblock.acquire()
        try:
            self.log("Removing job: %s" % boxee_job.name)
            if self.jobs.has_key(boxee_job.name):
                del self.jobs[boxee_job.name]
        finally:
            #self.joblock.release()
            pass

    def add_job(self, boxee_job):
        self.log("Adding new job: %s" % (boxee_job.name))
        self.jobs[boxee_job.name] = boxee_job
        return True

    def check(self):
        # Extend this function to run your own check to see if loop should keep running.
        return

    def log(self, message):
        msg = "BoxeeJobManager: %s" % (str(message))
        if mc:
            mc.LogDebug(msg)
        else:
            print msg

    def error(self, message):
        msg = "BoxeeJobManager: %s" % (str(message))
        if mc:
            mc.LogError(msg)
        else:
            print msg


'''
Object for Jobs

Extend this object and pass to JobManager object to queue up the job.
'''
class BoxeeJob(object):
    def __init__(self, name, interval=10):
        self.name = name
        self.interval = interval
        self.elapsed = 0

    def run(self):
        # Error-safe wrapper for user-defined job logic
        try:
            self.process()
        except Exception, e:
            raise JobError("%s failed:" % (job.name), e)

    def process(self):
        '''
        Main function launched with each job.
        '''
        return

    def log(self, message):
        msg = "BoxeeJob %s: %s" % (self.name, str(message))
        if mc:
            mc.LogDebug(msg)
        else:
            print msg

    def error(self, message):
        msg = "BoxeeJob %s: %s" % (self.name, str(message))
        if mc:
            mc.LogError(msg)
        else:
            print msg

'''
Boxee Job Manager Exception
'''
class JobError(Exception):
    def __init__(self, message, e):
        self.message = message
        self.e = e
        Exception.__init__(self, message, e)

    def __repr__(self):
        return "BoxeeJobManager: %s! %s" % (self.message, str(self.e))
    
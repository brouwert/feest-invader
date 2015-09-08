import logging
import threading

from model import SubclassResponsibility
from threads import CountingEvent

__author__ = 'Arjen'


def effect_runner_continuous(effect, schedule, stop, done):
    while not stop.is_set():
        effect.tick()
    done.signal()

    logging.info("Continuous runner done")


def effect_runner_iterations(effect, schedule, stop, done):
    logging.info("Starting iterations runner")

    n = effect.ticks_per_iteration() * schedule.iterations()

    while not stop.is_set() and n != 0:
        n -= 1
        effect.tick()

    stop.set()
    done.signal()

    logging.info("Iterations runner done")


class Planner(object):
    def __init__(self, schedule):
        self._schedule = schedule
        self._stop_event = threading.Event()

        self._done_counter = None
        self._threads = []

    def execute(self, effects, done_event):
        # Spawn player threads
        self._done_counter = CountingEvent(done_event, len(effects))
        self._threads = self.create_threads(effects)

        # Start the threads
        for thread in self._threads:
            thread.start()

    def create_threads(self, effects):
        return [
            threading.Thread(target=self.scheduler_for(index),
                             args=(effect, self._schedule, self._stop_event, self._done_counter))
            for (index, effect) in enumerate(effects)]

    def stop(self):
        if self._stop_event is None:
            return

        logging.info("Stopping effects ...")
        self._stop_event.set()
        for t in self._threads:
            t.join()

        logging.info("All effects stopped")
        self._stop_event = None

    def scheduler_for(self, index):
        raise SubclassResponsibility()


class IterationPlanner(Planner):
    def scheduler_for(self, n):
        if n == 0:
            return effect_runner_iterations
        else:
            return effect_runner_continuous


class SchedulePlannerCreator:
    def visit(self, schedule):
        return schedule.accept(self)

    def visitScheduleIterations(self, s):
        return IterationPlanner(s)


def for_schedule(schedule):
    return SchedulePlannerCreator().visit(schedule)

##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import multiprocessing
import csv
import traceback
import os
import logging
import signal
import sys

from erp5.utils.test_browser.browser import Browser

MAXIMUM_ERROR_COUNTER = 10
RESULT_NUMBER_BEFORE_FLUSHING = 100

class BenchmarkProcess(multiprocessing.Process):
  def __init__(self, exit_msg_queue, result_klass, argument_namespace,
               nb_users, user_index, *args, **kwargs):
    self._exit_msg_queue = exit_msg_queue
    self._result_klass = result_klass
    self._argument_namespace = argument_namespace
    self._nb_users = nb_users
    self._user_index = user_index

    # Initialized when running the test
    self._browser = None
    self._current_repeat = 1
    self._error_counter = 0

    super(BenchmarkProcess, self).__init__(*args, **kwargs)

  def stopGracefully(self, *args, **kwargs):
    raise StopIteration("Interrupted by user or because of an error from "
                        "another process, flushing remaining results...")

  def getBrowser(self, log_file):
    info_list = tuple(self._argument_namespace.url) + \
        tuple(self._argument_namespace.user_tuple[self._user_index])

    return Browser(*info_list,
                   is_debug=self._argument_namespace.enable_debug,
                   log_file=log_file,
                   is_legacy_listbox=self._argument_namespace.is_legacy_listbox)

  def runBenchmarkSuiteList(self, result):
    for target_idx, target in enumerate(self._argument_namespace.benchmark_suite_list):
      self._logger.debug("EXECUTE: %s" % target)
      result.enterSuite(target.__name__)

      try:
        target(result, self._browser)
      except BaseException, e:
        if isinstance(e, StopIteration):
          raise

        msg = "%s: %s" % (target, traceback.format_exc())

        if (self._argument_namespace.enable_debug and isinstance(e, Exception)):
          try:
            msg += self._browser.normalized_contents
          except:
            pass

        if (self._current_repeat == 1 or
            self._error_counter == MAXIMUM_ERROR_COUNTER):
          raise RuntimeError(msg)

        self._error_counter += 1
        self._logger.warning(msg)

      for stat in result.getCurrentSuiteStatList():
        mean = stat.mean

        self._logger.info("%s: min=%.3f, mean=%.3f (+/- %.3f), max=%.3f" % \
                            (stat.full_label,
                             stat.minimum,
                             mean,
                             stat.standard_deviation,
                             stat.maximum))

        if (self._argument_namespace.max_global_average and
            mean > self._argument_namespace.max_global_average):
          raise RuntimeError("Stopping as mean is greater than maximum "
                             "global average")

      result.exitSuite()

    result.iterationFinished()

  def run(self):
    result_instance = self._result_klass(self._argument_namespace,
                                         self._nb_users,
                                         self._user_index)

    self._logger = result_instance.getLogger()

    # Ensure the data are flushed before exiting, handled by Result class 
    # __exit__ block
    signal.signal(signal.SIGTERM, self.stopGracefully)
 
    # Ignore KeyboardInterrupt as it is handled by the parent process
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    exit_status = 0
    exit_msg = None

    try:
      with result_instance as result:
        self._browser = self.getBrowser(result_instance.log_file)

        while self._current_repeat != (self._argument_namespace.repeat + 1):
          self._logger.info("Iteration: %d" % self._current_repeat)
          self.runBenchmarkSuiteList(result)
          self._current_repeat += 1

          if self._current_repeat == RESULT_NUMBER_BEFORE_FLUSHING:
            result.flush()

    except StopIteration, e:
      self._logger.error(e)

    except BaseException, e:
      exit_msg = e
      exit_status = 1

    self._exit_msg_queue.put(exit_msg)
    sys.exit(exit_status)

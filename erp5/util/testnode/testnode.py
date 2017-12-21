##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
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
import os
import sys
import json
import time
import shutil
import logging
from slapos.slap.slap import ConnectionError

from .ProcessManager import SubprocessError, ProcessManager, CancellationError
from subprocess import CalledProcessError
from .Updater import Updater
from .NodeTestSuite import NodeTestSuite, SlapOSInstance
from .ScalabilityTestRunner import ScalabilityTestRunner
from .UnitTestRunner import UnitTestRunner
from .Utils import deunicodeData
from .. import taskdistribution

MAX_LOG_TIME = 15 # time in days we should keep logs that we can see through
                  # httd
MAX_TEMP_TIME = 0.01 # time in days we should keep temp files

PROFILE_PATH_KEY = 'profile_path'

class DummyLogger(object):
  def __init__(self, func):
    for name in ('trace', 'debug', 'info', 'warn', 'warning', 'error',
      'critical', 'fatal'):
       setattr(self, name, func)

test_type_registry = {
  'UnitTest': UnitTestRunner,
  'ScalabilityTest': ScalabilityTestRunner,
}

class TestNode(object):

  def __init__(self, log, config, max_log_time=MAX_LOG_TIME,
               max_temp_time=MAX_TEMP_TIME):
    self.testnode_log = log
    self.log = log
    self.config = config or {}
    self.process_manager = ProcessManager(log)
    self.working_directory = config['working_directory']
    self.node_test_suite_dict = {}
    self.file_handler = None
    self.max_log_time = max_log_time
    self.max_temp_time = max_temp_time
    self.url_access = "https://[0::0]:0123" # Ipv6 + port of the node

  def purgeOldTestSuite(self, test_suite_data):
    reference_set = set(os.listdir(self.working_directory))
    reference_set.difference_update(x['test_suite_reference']
                                    for x in test_suite_data)
    for reference in reference_set:
      fpath = os.path.join(self.working_directory, reference)
      self.node_test_suite_dict.pop(reference, None)
      self.log("testnode.purgeOldTestSuite, DELETING : %r", fpath)
      if os.path.isdir(fpath):
        shutil.rmtree(fpath)
      else:
        os.remove(fpath)
  
  def getNodeTestSuite(self, reference):
    try:
      node_test_suite = self.node_test_suite_dict[reference]
    except KeyError:
      node_test_suite = self.node_test_suite_dict[reference] = \
        NodeTestSuite(reference, self.working_directory)
      config = self.config
      node_test_suite.edit(log_directory=config['log_directory'])
    return node_test_suite

  def constructProfile(self, node_test_suite, test_type, use_relative_path=False):
    assert len(node_test_suite.vcs_repository_list), "we must have at least one repository"
    software_config_path = None
    profile_content_list = []
    revision_dict = dict(node_test_suite.revision_list)
    for vcs_repository in node_test_suite.vcs_repository_list:
      buildout_section_id = vcs_repository.get('buildout_section_id')
      repository_path = vcs_repository['repository_path']
      try:
        profile_path = vcs_repository[PROFILE_PATH_KEY]
      except KeyError:
        pass
      else:
        if software_config_path is not None:
          raise ValueError(PROFILE_PATH_KEY + ' defined more than once')

        # Absolute path to relative path
        software_config_path = os.path.join(repository_path, profile_path)
        if use_relative_path :
          from_path = os.path.join(self.working_directory,
                                    node_test_suite.reference)
          software_config_path = os.path.relpath(software_config_path, from_path)

      # Construct sections
      if not(buildout_section_id is None):
        # Absolute path to relative
        if use_relative_path:
          from_path = os.path.join(self.working_directory,
                                    node_test_suite.reference)
          repository_path = os.path.relpath(repository_path, from_path)

        # XXX: Like in run(), code depending on specific test type must be
        #      moved to the test type classes. In particular, the use of a
        #      replacement pattern ('<obfuscated_url>') is ugly: buildout
        #      has cleaner ways to do that.
        if test_type=="ScalabilityTest":
          # <obfuscated_url> word is modified by in runner.prepareSlapOSForTestSuite()
          profile_content_list.append("""
[%(buildout_section_id)s]
repository = <obfuscated_url>/%(buildout_section_id)s/%(buildout_section_id)s.git
revision = %(revision)s
ignore-ssl-certificate = true
develop = false
shared = true
""" %     {'buildout_section_id': buildout_section_id,
          'revision': revision_dict[buildout_section_id][1]})
        else:
          profile_content_list.append("""
[%(buildout_section_id)s]
repository = %(repository_path)s
branch = %(branch)s
revision =
develop = false
shared = true
""" %     {'buildout_section_id': buildout_section_id,
          'repository_path' : repository_path,
          'branch' : vcs_repository.get('branch','master')})
    if software_config_path is None:
      raise ValueError(PROFILE_PATH_KEY + ' not defined')
    profile_content_list.sort()
    # Write file
    with open(node_test_suite.custom_profile_path, 'w') as f:
      f.write("[buildout]\nextends = %s\n%s" % (
        software_config_path,
        ''.join(profile_content_list)))

  def updateRevisionList(self, node_test_suite):
    config = self.config
    log = self.log
    revision_list = []
    try:
      for vcs_repository in node_test_suite.vcs_repository_list:
        repository_path = vcs_repository['repository_path']
        repository_id = vcs_repository['repository_id']
        branch = vcs_repository.get('branch')
        # Make sure we have local repository
        updater = Updater(repository_path, git_binary=config['git_binary'],
           branch=branch, log=log, process_manager=self.process_manager,
           working_directory=node_test_suite.working_directory,
           url=vcs_repository["url"])
        updater.checkout()
        revision_list.append((repository_id, updater.getRevision()))
    except SubprocessError:
      log("Error while getting repository, ignoring this test suite",
          exc_info=1)
      return False
    node_test_suite.revision_list = revision_list
    return True

  def registerSuiteLog(self, test_result, node_test_suite):
    """
      Create a log dedicated for the test suite,
      and register the url to master node.
    """
    suite_log_path, folder_id = node_test_suite.createSuiteLog()
    self._initializeSuiteLog(suite_log_path)
    # TODO make the path into url
    test_result.reportStatus('LOG url', "%s/%s" % (self.config.get('httpd_url'),
                             folder_id), '')
    self.log("going to switch to log %r", suite_log_path)
    self.process_manager.log = self.log = self.suite_log
    return suite_log_path

  def _initializeSuiteLog(self, suite_log_path):
    # remove previous handlers
    logger = logging.getLogger('testsuite')
    if self.file_handler is not None:
      logger.removeHandler(self.file_handler)
    # and replace it with new handler
    logger_format = '%(asctime)s %(name)-13s: %(levelname)-8s %(message)s'
    formatter = logging.Formatter(logger_format)
    logging.basicConfig(level=logging.INFO, format=logger_format)
    self.file_handler = logging.FileHandler(filename=suite_log_path)
    self.file_handler.setFormatter(formatter)
    logger.addHandler(self.file_handler)
    logger.info('Activated logfile %r output', suite_log_path)
    self.suite_log = logger.info

  def checkRevision(self, test_result, node_test_suite):
    if node_test_suite.revision == test_result.revision:
      return
    log = self.log
    log('Disagreement on tested revision, checking out: %r != %r',
        node_test_suite.revision, test_result.revision)
    updater_kw = dict(git_binary=self.config['git_binary'], log=log,
                      process_manager=self.process_manager)
    revision_list = []
    for i, revision in enumerate(test_result.revision.split(',')):
      vcs_repository = node_test_suite.vcs_repository_list[i]
      repository_path = vcs_repository['repository_path']
      count, revision = revision.split('=')[1].split('-')
      revision_list.append((vcs_repository['repository_id'],
                            (int(count), revision)))
      # other testnodes on other boxes are already ready to test another
      # revision
      updater = Updater(repository_path, revision=revision, **updater_kw)
      updater.checkout()
      updater.git_update_server_info()
      updater.git_create_repository_link()
    node_test_suite.revision_list = revision_list

  def _cleanupLog(self):
    log_directory = self.config['log_directory']
    prune_time = time.time() - 86400 * self.max_log_time
    for log_folder in os.listdir(log_directory):
      folder_path = os.path.join(log_directory, log_folder)
      if os.path.isdir(folder_path):
        if os.stat(folder_path).st_mtime < prune_time:
          self.log("deleting log directory %r", folder_path)
          shutil.rmtree(folder_path)

  def _cleanupTemporaryFiles(self):
    """
    buildout seems letting files under /tmp. To avoid regular error of
    missing disk space, remove old logs
    """
    temp_directory = self.config["system_temp_folder"]
    user_id = os.geteuid()
    prune_time = time.time() - 86400 * self.max_temp_time
    for temp_folder in os.listdir(temp_directory):
      folder_path = os.path.join(temp_directory, temp_folder)
      if (temp_folder.startswith("tmp") or
          temp_folder.startswith("buildout")):
        try:
          stat = os.stat(folder_path)
          if stat.st_uid == user_id and stat.st_mtime < prune_time:
            self.log("deleting temp directory %r", folder_path)
            if os.path.isdir(folder_path):
              shutil.rmtree(folder_path)
            else:
              os.remove(folder_path)
        except OSError:
          self.log("_cleanupTemporaryFiles exception", exc_info=1)

  def cleanUp(self):
    self.log('Testnode.cleanUp')
    self.process_manager.killPreviousRun()
    self._cleanupLog()
    self._cleanupTemporaryFiles()

  def run(self):
    log = self.log
    config = self.config
    portal_url = config['test_suite_master_url']
    test_node_slapos = SlapOSInstance(config['slapos_directory'])
    try:
      while True:
        test_result = None
        try:
          node_test_suite = None
          self.log = self.process_manager.log = self.testnode_log
          self.cleanUp()
          begin = time.time()
          taskdistributor = taskdistribution.TaskDistributor(
            portal_url, logger=DummyLogger(log))
          self.test_suite_portal = taskdistributor # XXX ScalabilityTest
          node_configuration = taskdistributor.subscribeNode(
            node_title=config['test_node_title'],
            computer_guid=config['computer_id'])
          if type(node_configuration) is str:
            # Backward compatiblity
            node_configuration = json.loads(node_configuration)
          if node_configuration is not None and \
              'process_timeout' in node_configuration \
              and node_configuration['process_timeout'] is not None:
            process_timeout = node_configuration['process_timeout']
            log('Received and using process timeout from master: %i',
              process_timeout)
            self.process_manager.max_timeout = process_timeout
          test_suite_data = taskdistributor.startTestSuite(
            node_title=config['test_node_title'],
            computer_guid=config['computer_id'])
          if type(test_suite_data) is str:
            # Backward compatiblity
            test_suite_data = json.loads(test_suite_data)
          test_suite_data = deunicodeData(test_suite_data)
          log("Got following test suite data from master : %r",
              test_suite_data)
          try:
            my_test_type = taskdistributor.getTestType()
          except Exception:
            log("testnode, error during requesting getTestType() method"
                " from the distributor.")
            raise
          # Select runner according to the test type
          try:
            runner_class = test_type_registry[my_test_type]
          except KeyError:
            log("testnode, Runner type %s not implemented.", my_test_type)
            raise NotImplementedError
          runner = runner_class(self)
          log("Type of current test is %s", my_test_type)
          # master testnode gets test_suites, slaves get nothing
          runner.prepareSlapOSForTestNode(test_node_slapos)
          # Clean-up test suites
          self.purgeOldTestSuite(test_suite_data)
          for test_suite in test_suite_data:
            node_test_suite = self.getNodeTestSuite(
               test_suite.pop("test_suite_reference"))
            node_test_suite.edit(**test_suite)

            # XXX: temporary hack to prevent empty test_suite
            if not hasattr(node_test_suite, 'test_suite'):
              node_test_suite.edit(test_suite='')
            # kill processes from previous loop if any
            self.process_manager.killPreviousRun()
            if not self.updateRevisionList(node_test_suite):
              continue
            test_result = taskdistributor.createTestResult(
                     node_test_suite.revision, [],
                     config['test_node_title'], False,
                     node_test_suite.test_suite_title,
                     node_test_suite.project_title)
            log("testnode, test_result : %r", test_result)
            if test_result is not None:
              self.registerSuiteLog(test_result, node_test_suite)
              self.checkRevision(test_result,node_test_suite)
              node_test_suite.edit(test_result=test_result)
              # get cluster configuration for this test suite, this is needed to
              # know slapos parameters to user for creating instances
              log("Getting configuration from test suite %s",
                  node_test_suite.test_suite_title)
              generated_config = taskdistributor.generateConfiguration(
                node_test_suite.test_suite_title)
              json_data = json.loads(generated_config)
              cluster_configuration = deunicodeData(json_data['configuration_list'][0])
              node_test_suite.edit(cluster_configuration=cluster_configuration)
              # Now prepare the installation of SlapOS and create instance
              self.constructProfile(node_test_suite, my_test_type,
                                    runner.getRelativePathUsage())
              status_dict = runner.prepareSlapOSForTestSuite(node_test_suite)
              # Give some time so computer partitions may start
              # as partitions can be of any kind we have and likely will never have
              # a reliable way to check if they are up or not ...
              time.sleep(20)
              # XXX: Do not switch according to the test type. IOW, the
              #      following code must be moved to the test type class.
              if my_test_type == 'UnitTest':
                runner.runTestSuite(node_test_suite, portal_url)
              elif my_test_type == 'ScalabilityTest':
                error_message = None
                # A problem is appeared during runTestSuite
                if status_dict['status_code'] == 1:
                  error_message = "Software installation too long or error(s) are present during SR install."
                else:
                  status_dict = runner.runTestSuite(node_test_suite, portal_url)
                  # A problem is appeared during runTestSuite
                  if status_dict['status_code'] == 1:
                    error_message = status_dict['error_message']

                # If an error is appeared
                if error_message:
                  test_result.reportFailure(
                      stdout=error_message
                  )
                  self.log(error_message)
                  raise ValueError(error_message)
              else:
                raise NotImplementedError
              # break the loop to get latest priorities from master
              break
            self.cleanUp()
        except (SubprocessError, CalledProcessError, ConnectionError) as e:
          log("", exc_info=1)
          if test_result is not None:
            status_dict = getattr(e, "status_dict", None) or {
              'stderr': "%s: %s" % (e.__class__.__name__, e)}
            test_result.reportFailure(
              command=status_dict.get('command'),
              stdout=status_dict.get('stdout'),
              stderr=status_dict.get('stderr'),
            )
          continue
        except ValueError as e:
          # This could at least happens if runTestSuite is not found
          log("", exc_info=1)
          if node_test_suite is not None:
            node_test_suite.retry_software_count += 1
          if test_result is not None:
            test_result.reportFailure(
              command='', stdout='',
              stderr="ValueError was raised : %s" % (e,),
            )
        except CancellationError:
          log("", exc_info=1)
          self.process_manager.under_cancellation = False
          node_test_suite.retry = True
          continue
        self.cleanUp()
        sleep_time = 120 - (time.time() - begin)
        if sleep_time > 0:
          log("End of processing, going to sleep %s", sleep_time)
          time.sleep(sleep_time)
    except Exception:
      log("", exc_info=1)
    except:
      log("", exc_info=1)
      raise
    finally:
      # Nice way to kill *everything* generated by run process -- process
      # groups working only in POSIX compilant systems
      # Exceptions are swallowed during cleanup phase
      log("GENERAL EXCEPTION, QUITING")
      self.cleanUp()
      log("GENERAL EXCEPTION, QUITING, cleanup finished")

#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) 2010-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.  A copy of the GNU General Public License is
# also available at http://www.gnu.org/copyleft/gpl.html.

import sys
import os
import os.path
import signal
import logging
from imagefactory.ApplicationConfiguration import ApplicationConfiguration
from imagefactory.qmfagent.ImageFactoryAgent import *
from imagefactory.BuildDispatcher import BuildDispatcher
from imagefactory.ImageWarehouse import ImageWarehouse
from imagefactory.Singleton import Singleton

class Application(Singleton):

    def qmf_agent():
        doc = "The qmf_agent property."
        def fget(self):
            return self._qmf_agent
        def fset(self, value):
            self._qmf_agent = value
        def fdel(self):
            del self._qmf_agent
        return locals()
    qmf_agent = property(**qmf_agent())

    def _singleton_init(self):
        super(Application, self)._singleton_init()
        self.log = logging.getLogger('%s.%s' % (__name__, self.__class__.__name__))
        self.daemon = False
        self.pid_file_path = "/var/run/imagefactory.pid"
        signal.signal(signal.SIGTERM, self.signal_handler)
        self.app_config = ApplicationConfiguration().configuration

        # by setting TMPDIR here we make sure that libguestfs
        # (imagefactory -> oz -> libguestfs) uses the temporary directory of
        # the user's choosing
        os.putenv('TMPDIR', self.app_config['tmpdir'])

    def __init__(self):
        pass

    def setup_logging(self):
        if (self.app_config['foreground']):
            logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(name)s pid(%(process)d) Message: %(message)s')
        else:
            logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(name)s pid(%(process)d) Message: %(message)s', filename='/var/log/imagefactory.log')
        if (self.app_config['debug']):
            logging.getLogger('').setLevel(logging.DEBUG)
        elif (self.app_config['verbose']):
            logging.getLogger('').setLevel(logging.INFO)

    def signal_handler(self, signum, stack):
        """docstring for sigterm_handler"""
        if (signum == signal.SIGTERM):
            logging.warn('caught signal SIGTERM, stopping...')

            if (self.qmf_agent):
                self.qmf_agent.shutdown()
                try:
                    os.remove(self.pid_file_path)
                except Exception, e:
                    self.log.warning(str(e))

            sys.exit(0)

    # TODO: (redmine 273) - add code here to set the user:group we're running as and drop privileges
    def daemonize(self): #based on Python recipe 278731
        UMASK = 0
        WORKING_DIRECTORY = '/'
        IO_REDIRECT = os.devnull

        try:
            pid = os.fork()
        except OSError, e:
            raise Exception, "%s [%d]" % (e.strerror, e.errno)

        if (pid == 0):
            os.setsid()
            signal.signal(signal.SIGHUP, signal.SIG_IGN)
            try:
                pid = os.fork()
            except OSError, e:
                raise Exception, "%s [%d]" % (e.strerror, e.errno)

            if (pid == 0):
                os.chdir(WORKING_DIRECTORY)
                os.umask(UMASK)
            else:
                os._exit(0)
        else:
            os._exit(0)

        for file_descriptor in range(0, 2): # close stdin, stdout, stderr
            try:
                os.close(file_descriptor)
            except OSError:
                pass # The file descriptor wasn't open to begin with, just ignore

        os.open(IO_REDIRECT, os.O_RDWR)
        os.dup2(0, 1)
        os.dup2(0, 2)

        return(True)

    def main(self):
        if (self.app_config['qmf']):
            if (not self.app_config['foreground']):
                self.daemon = self.daemonize()

            self.setup_logging()
            if(self.daemon):
                try:
                    with open(self.pid_file_path, "w") as pidfile:
                        pidfile.write("%s\n" % (str(os.getpid()), ))
                        pidfile.close()
                except Exception, e:
                    logging.warning(str(e))
                logging.info("Launched as daemon...")
            elif(self.app_config['foreground']):
                logging.info("Launching in foreground...")
            else:
                logging.warning("Failed to launch as daemon...")

            self.qmf_agent = ImageFactoryAgent(self.app_config['qpidd'])
            self.qmf_agent.run()

        else:
            self.app_config['foreground'] = True
            self.setup_logging()

            if self.app_config['target_image'] and self.app_config['target'] and self.app_config['provider']:
                if len(self.app_config['target']) != 1:
                    print("Expect a single target, but '%s' supplied" % (self.app_config['target'],))
                    sys.exit(1)
                if len(self.app_config['provider']) != 1:
                    print("Expect a single provider, but '%s' supplied" % (self.app_config['provider'],))
                    sys.exit(1)
                image_ids = BuildDispatcher().import_image(self.app_config['image'], None, self.app_config['target_image'], self.app_config['image_desc'], self.app_config['target'][0], self.app_config['provider'][0])
                print("Imported target image ID %s as image %s" % (self.app_config['target_image'], image_ids[0]))
            elif (self.app_config['template'] and self.app_config['target']) or (self.app_config['image'] and not self.app_config['provider']):
                dispatchers = BuildDispatcher().build_image_for_targets(self.app_config['image'], None, self.app_config['template'], self.app_config['target'])
                for dispatcher in dispatchers:
                    print("Building build %s of image %s to target %s" % (dispatcher.build_id, dispatcher.image_id, dispatcher.target))

            elif (self.app_config['image'] and self.app_config['provider'] and self.app_config['credentials']):
                credentials = self.app_config['credentials']
                if(os.path.exists(credentials)):
                    credentials_file = open(credentials, "r")
                    file_contents = credentials_file.read()
                    credentials_file.close()
                    credentials = file_contents

                if(not (("<provider_credentials>" in file_contents.lower()) and ("</provider_credentials>" in file_contents.lower()))):
                    print("Unexpected content or formatting of credentials...")
                    sys.exit(1)

                dispatchers = BuildDispatcher().push_image_to_providers(self.app_config['image'], None, self.app_config['provider'], credentials)
                for dispatcher in dispatchers:
                    print("Pushing build %s of image %s to provider %s" % (dispatcher.build_id, dispatcher.image_id, dispatcher.provider))

if __name__ == "__main__":
    application = Application()
    sys.exit(application.main())

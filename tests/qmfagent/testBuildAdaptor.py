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


import unittest
import logging
from imagefactory.qmfagent.BuildAdaptor import BuildAdaptor

class TestBuildAdaptor(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.NOTSET, format='%(asctime)s %(levelname)s %(name)s pid(%(process)d) Message: %(message)s', filename='/tmp/imagefactory-unittests.log')

    def tearDown(self):
        pass

    def testQMFSchemaDefinition(self):
        expected_schema_properties = ("image", "build", "status", "percent_complete", "image_id")
        expected_schema_methods = dict(abort=(), instance_states=("class_name", "states"))
        for schema_property in BuildAdaptor.qmf_schema.getProperties():
            self.assertIn(schema_property.getName(), expected_schema_properties)
        for schema_method in BuildAdaptor.qmf_schema.getMethods():
            self.assertIn(schema_method.getName(), expected_schema_methods)
            arguments = expected_schema_methods[schema_method.getName()]
            for schema_property in schema_method.getArguments():
                self.assertIn(schema_property.getName(), arguments)

if __name__ == '__main__':
	unittest.main()

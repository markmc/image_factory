#
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

import zope.interface
from zope.interface import Interface
from zope.interface import Attribute
from zope.interface import Invalid


def conforms_to_interface_invariant(obj):
    """Invariant method testing for mandatory aspects of the interface.
    Returns 'Invalid' exception if the implementing object does not conform."""
    try:
        getattr(obj, "template")
        getattr(obj, "target")
        getattr(obj, "target_id")
        getattr(obj, "provider")
        getattr(obj, "new_image_id")
        getattr(obj, "image")
        getattr(obj, "status")
        getattr(obj, "percent_complete")
        getattr(obj, "output_descriptor")
        getattr(obj, "delegate")
        getattr(obj, "build_image")
        getattr(obj, "abort")
        getattr(obj, "push_image")
    except AttributeError, e:
        raise Invalid(e)


class IBuilder(Interface):
    """The Builder interface provides guidance on attributes and methods
    that expected by Image Factory for objects that serve to build OS images."""
    # set the invariant checks
    zope.interface.invariant(conforms_to_interface_invariant)
    # attributes
    template = Attribute("""Template object created using the template string passed to the initializer. This string can be a UUID, URL, or XML document.""")
    target = Attribute("""The target backend the image is being built for.""")
    target_id = Attribute("""The unique handle or representation of the Replicated Image in the provider instance. For Amazon this will be an AMI. It's unclear what this might be on other providers.""")
    provider = Attribute("""Where the image is to be deployed / launched. (eg. ec2-us-west)""")
    new_image_id = Attribute("""A Universal Unique Identifier for the newly created target or provider image.""")
    image = Attribute("""Reference to the image file being built.""")
    status = Attribute("""Status of the image build process.""")
    percent_complete = Attribute("""Completion percentage for an image build in progress.""")
    output_descriptor = Attribute("""ICICLE document describing what was actually installed in the image.""")
    delegate = Attribute("""Object conforming to the BuilderDelegate interface.""")
    # methods
    def build_image(build_id=None):
        """Tell the builder to start building the image."""

    def abort():
        """Tell the builder to stop building the image."""

    def push_image(target_image_id, provider, credentials):
        """Deploy an image to the cloud provider."""

# -*- coding: utf-8 -*-
# util.py
#
# (c) 2014 Aparajita Fishman and licensed under the MIT license.
# URL: http://github.com/aparajita
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

"""This module provides utility methods."""

import sublime
import os
import os.path
import re


METHOD_NAME_RE = re.compile(r'^[-+]\s*\(\w+\)(\w+:?)(.*)')
METHOD_PARAM_RE = re.compile(r'(\w+:)')
PACKAGE = 'Cappuccino'


def copy_resource(srcpath, dstpath, overwrite=True):
    """
    Copy a resource within a package to Packages/User.

    Both paths should be relative paths whose first
    component is the package name. The directory separator
    should always be /.

    If the resource already exists in Packages/User and the
    source resource is not newer, nothing is done. If the source
    resource is newer, the existing User resource is overwritten
    if overwrite is True.

    If the resource is copied successfully or already exists,
    return True.

    This method works with loose packages
    and .sublime-packages.

    """

    # Try loading the resource
    resource = sublime.load_resource('Packages/' + srcpath)

    if not resource:
        print('{}: resource \"{}\" not found'.format(PACKAGE, srcpath))
        return False

    # Get a real file path to the resource in Packages/User
    package_name = srcpath.split('/')[0]
    dst_resource = os.path.join(sublime.packages_path(), 'User', dstpath)

    if os.path.exists(dst_resource):
        if not overwrite:
            return True

        # The resource already exists, see if the source version is newer.
        # If the source package is a .sublime-package, compare its mod time
        # with the resource.
        src_resource = os.path.join(sublime.installed_packages_path(), package_name + '.sublime-package')
        src_mtime = 0

        if os.path.exists(src_resource):
            src_mtime = os.stat(src_resource).st_mtime
        else:
            src_resource = os.path.join(sublime.packages_path(), srcpath)

            if os.path.exists(src_resource):
                src_mtime = os.stat(src_resource).st_mtime

        dst_mtime = os.stat(dst_resource).st_mtime
        should_copy = src_mtime > dst_mtime
    else:
        should_copy = True

    if should_copy:
        dstdir = os.path.dirname(dst_resource)

        if not os.path.exists(dstdir):
            os.makedirs(dstdir)

        with open(dst_resource, 'w') as f:
            f.write(resource)

        print('{}: copied resource to {}'.format(PACKAGE, dst_resource))

    return True


def get_method_name(view, pt, multiline=True):
    """Given a point within a method, return the method name."""
    declaration = find_declaration_with_scope(view, 'meta.method-declaration.js.objj', pt, multiline=multiline)
    match = METHOD_NAME_RE.match(declaration)

    if match:
        name = match.group(1) + ''.join(METHOD_PARAM_RE.findall(match.group(2)))
    else:
        name = ''

    return name


def find_declaration_with_scope(view, scope, pt, multiline=True):
    """Given a point, return the closest region that contains the given scope."""

    # Go to the beginning of the line if we are not already there.
    line = view.line(pt)

    if line.begin() != pt:
        pt = view.find_by_class(pt, False, sublime.CLASS_LINE_START)

    # Continue upwards by line until we reach the given scope.
    start = end = None
    original_pt = pt

    while start is None and pt > 0:
        scopes = view.scope_name(pt).split()

        if scope in scopes:
            end = view.find_by_class(pt, True, sublime.CLASS_LINE_END)

            if multiline:
                # Continue up until we are no longer in the scope, in case
                # the declaration spans several lines.
                while True:
                    pt2 = view.find_by_class(pt, False, sublime.CLASS_LINE_START)
                    scopes = view.scope_name(pt2).split()

                    if scope not in scopes:
                        start = pt
                        break
                    else:
                        pt = pt2

                # If the declaration start is the start of the line where
                # we started searching, search down in case the declaration spans
                # multiple lines.
                if start == original_pt:
                    pt = start

                    while True:
                        pt = view.find_by_class(pt, True, sublime.CLASS_LINE_START)
                        scopes = view.scope_name(pt).split()

                        if scope not in scopes:
                            end = pt - 1
                            break
            else:
                start = pt
        else:
            pt = view.find_by_class(pt, False, sublime.CLASS_LINE_START)

    if start is not None:
        region = sublime.Region(start, end)
        return re.sub(r'[\n\r]', ' ', view.substr(region))
    else:
        return ''


def get_container_and_method(view, container, pt):
    """Given a point within an @implementation or @protocol, return the container name, method name and error."""

    # First step is to see if we are within a method.
    if container == 'implementation':
        method_scope = 'meta.method-with-body.js.objj'
    else:
        method_scope = 'meta.method-declaration.js.objj'

    if method_scope in view.scope_name(pt).split():
        # Assume protocol method declarations are on a single line.
        method = get_method_name(view, pt, multiline=container == 'implementation')
    else:
        method = None

    # Now find the container declaration and extract the name.
    declaration = find_declaration_with_scope(view, 'meta.{}.declaration.js.objj'.format(container), pt)
    match = re.match(r'^\s*@{}\s*(\w+)'.format(container), declaration)

    if match:
        name = match.group(1)
    else:
        return None, None, 'No {} name could be found.'.format(container)

    return name, method, None

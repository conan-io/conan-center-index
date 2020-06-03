#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import print_function
import argparse
import sys
import subprocess
import json
import os
import re
from shutil import copy

conanfile_template = """from conans import tools
import os
from conanfile_base import {baseclass}

class {classname}Conan({baseclass}):
    basename = "{name}"
    name = basename.lower()
    version = "{version}"
    tags = ("conan", "{name}")
    description = '{description}'
    exports = ["conanfile_base.py", "patches/*.patch"]
    _patches = {patches}

    {requires}

    def source(self):
        url = "https://www.x.org/archive/individual/{namespace}/{name}-{version}.tar.gz"
        tools.get(url, sha256="{sha256}")
        for p in self._patches:
            tools.patch(".", "patches/%s" % p)
        extracted_dir = "{name}-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package_info(self):
        super({classname}Conan, self).package_info()
        {system_libs}
"""

current_dir = os.path.abspath(os.path.dirname(__file__))
libraries = json.load(open(os.path.join(current_dir, "x11.json")))


def find(name):
    for info in libraries:
        if info["name"] == name:
            return info
    raise Exception("not found %s" % name)


def gen(args):
    for info in libraries:
        name = info["name"]
        package_dir = os.path.join(current_dir, name.lower())
        os.makedirs(package_dir)
        filename = os.path.join(package_dir, "conanfile.py")
        print("generating %s..." % filename)
        classname = name.replace("-", "")
        with open(filename, "w") as f:
            if "requires" in info:
                requires = []
                for require in info["requires"]:
                    if "@" in require:
                        requires.append('"%s"' % require)
                    else:
                        requires.append('"%s/%s"' % (require.lower(), find(require)["version"]))
                requires = ", ".join(requires)
                requires = "requires = (" + requires + ")"
            else:
                requires = ""
            header_only = "header-only" in info and info["header-only"]
            system_libs = ""
            if "system_libs" in info:
                system_libs = ['"%s"' % lib for lib in info["system_libs"]]
                system_libs = "self.cpp_info.system_libs.extend([%s])" % ", ".join(system_libs)
            patches = info["patches"] if "patches" in info else "[]"
            baseclass = "BaseHeaderOnly" if header_only else "BaseLib"
            namespace = info["namespace"] if "namespace" in info else "lib"
            content = conanfile_template.format(sha256=info["sha256"],
                                                version=info["version"],
                                                description=info["description"],
                                                namespace=namespace,
                                                requires=requires,
                                                name=name,
                                                baseclass=baseclass,
                                                system_libs=system_libs,
                                                classname=classname,
                                                patches=patches)
            f.write(content)

            copy(os.path.join(current_dir, "conanfile_base.py"), package_dir)

            for patch in patches:
                patch_file = os.path.join(current_dir, "patches", patch)
                if os.path.exists(patch_file):
                    patches_dir = os.path.join(package_dir, "patches")
                    if not os.path.exists(patches_dir):
                        os.makedirs(patches_dir)
                    copy(patch_file, patches_dir)


def create(args):
    for info in libraries:
        name = info["name"]
        filename = "conanfile-%s.py" % name.lower()
        subprocess.check_call(["conan", "create", filename, "%s/%s" % (get_username(), get_channel_name()), "-k"])


def groups(args):
    def in_groups(require, groups):
        for group in groups:
            if require in group:
                return True
        return False

    def all_requires_in_groups(requires, groups):
        for require in requires:
            if "@" not in require:
                if not in_groups(require, groups):
                    return False
        return True

    def create_json_file(dict_groups):
        file_object = open("groups.json", 'w')
        json.dump(dict_groups, file_object)

    remain = libraries
    groups = []
    dict_groups = {}
    while remain:
        current_group = []
        for info in remain:
            requires = info["requires"] if "requires" in info else []
            if all_requires_in_groups(requires, groups):
                current_group.append(info["name"])
        groups.append(current_group)
        remain = [r for r in remain if r["name"] not in current_group]
    index = 0
    for group in groups:
        print("group %s: %s" % (index, group))
        dict_groups[index] = group
        index = index + 1

    create_json_file(dict_groups)


def main(args):
    parser = argparse.ArgumentParser(description='utility script to manage conan X11 package')
    subparsers = parser.add_subparsers()
    sp_gen = subparsers.add_parser('gen', help='generate conanfiles')
    # sp_create = subparsers.add_parser('create', help='invoke conan create on conanfiles')
    # sp_groups = subparsers.add_parser('groups', help='report groups')
    sp_gen.set_defaults(func=gen)
    # sp_create.set_defaults(func=create)
    # sp_groups.set_defaults(func=groups)
    args = parser.parse_args(args)
    args.func(args)


if __name__ == '__main__':
    main(sys.argv[1:])


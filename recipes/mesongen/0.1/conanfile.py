# Copyright © 2021-2021
#         Alexis A. D. COLIN,
#         Antoine VUGLIANO,
#         Gaëtan CHAMPARNAUD,
#         Geoffrey L. TOURON,
#         Grégoire A. P. BADIN

# This file is part of mesongen.

# mesongen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# mesongen is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with mesongen.  If not, see <https://www.gnu.org/licenses/>.

from conans.model import Generator
from conans import ConanFile
from conans.model.conan_generator import GeneratorComponentsMixin


class meson(GeneratorComponentsMixin, Generator):
    name = "meson"

    @property
    def filename(self):
        return "meson.build"

    @property
    def content(self):
        sections = ["_conan_compiler = meson.get_compiler('cpp')"]

        for depname, cpp_info in reversed(self.deps_build_info.dependencies):
            if depname == 'mesongen':
                continue
            self._validate_components(cpp_info)
            public_deps = self.get_public_deps(cpp_info)
            deps_names = [self._get_require_name(*it)[1] for it in public_deps]

            if cpp_info.components:
                components = self._get_components(depname, cpp_info)
                comp_gennames = [comp_genname for comp_genname, _, _ in components]
                if depname not in comp_gennames:
                    sections.append(self.formatMesonDependency(depname, cpp_info, comp_gennames, deps_names))
            else:
                sections.append(self.formatMesonDependency(depname, cpp_info, [], deps_names))

        return "\n\n".join(sections)

    def join(self, args, indent_count = 1):
        if not args:
            return ""
        elif len(args) == 1:
            return args[0]
        else:
            indent = (indent_count + 1) * "    "
            return ",".join([f"\n{indent}{a}" for a in args]) + "\n" + (indent_count * "    ")

    def formatMesonDependency(self, dep_name, deps_cpp_info, system_libs, requires):
        name = dep_name.replace("-", "_")
        include_paths = ["'%s'" % p.replace('\\', '\\\\') for p in deps_cpp_info.include_paths]
        lib_paths = ["'%s'" % p.replace('\\', '\\\\') for p in deps_cpp_info.lib_paths]

        libs = [f"_conan_compiler.find_library('{p}', dirs: [{self.join(lib_paths, 2)}])" for p in deps_cpp_info.libs]
        system_libs = [f"dependency('{lib}')" for lib in system_libs]
        requires = [f"{p}_conan_dep" for p in requires]

        defines = [f"'-D{p}'" for p in deps_cpp_info.defines]
        cppflags = [f"'{p}'" for p in deps_cpp_info.cppflags]

        exelinkflags = [f"'{p}'" for p in deps_cpp_info.exelinkflags]

        cflags = [f"'{p}'" for p in deps_cpp_info.cflags]
        sharedlinkflags = [f"'{p}'" for p in deps_cpp_info.sharedlinkflags]

        return f"""\
{name}_conan_dep = declare_dependency(
    include_directories: [{self.join(include_paths)}],
    dependencies: [{self.join(libs + requires + system_libs)}],
    compile_args: [{self.join(cppflags + defines)}],
    link_args: [{self.join(exelinkflags + sharedlinkflags)}]
    # not handled by generator:
    # conan_cflags = [{self.join(cflags)}]
)"""


class MesonGeneratorPackage(ConanFile):
    name = "mesongen"
    version = "0.1"
    license = "GPLv3"
    description = "Custom generator for Meson 0.58"
    url = "https://framagit.org/perdumondrapeau/mesongen"


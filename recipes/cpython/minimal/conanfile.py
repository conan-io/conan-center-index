import os
import textwrap

from conan import ConanFile
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.4.0"


class CPythonConan(ConanFile):
    name = "cpython"
    description = "Python is a programming language that lets you work quickly and integrate systems more effectively."
    license = "Python-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.python.org"
    topics = ("python", "cpython", "language", "script")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    short_paths = True
    languages = ["C"]
    implements = ["auto_shared_fpic"]

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Macos":
            raise ConanInvalidConfiguration("This package is only available for Macos")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "Misc", "python-config.sh.in"),
                        'prefix="@prefix@"', 'prefix="$PYTHON_ROOT"')

    def generate(self):
        VirtualRunEnv(self).generate(scope="build")
        tc = AutotoolsToolchain(self, prefix=self.package_folder)
        # Not necessary, just cleans up the output
        tc.update_configure_args({"--enable-static": None, "--disable-static": None})
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args += [
            "--with-pydebug={}".format(yes_no(self.settings.build_type == "Debug")),
            "--disable-test-modules",
        ]
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()
        pkgdeps = PkgConfigDeps(self)
        pkgdeps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        # FIXME: See https://github.com/python/cpython/issues/109796, this workaround is mentioned there
        autotools.make(target="sharedinstall", args=["DESTDIR="])
        autotools.install(args=["DESTDIR="])
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # Rewrite shebangs of python scripts
        self.rewrite_shebangs()
        # Create python plain symlink
        if not os.path.exists(self._cpython_symlink):
            os.symlink(f"python{self._version_suffix}", self._cpython_symlink)
        fix_apple_shared_install_name(self)

        self._write_cmake_findpython_wrapper_file()

    def package_info(self):
        py_version = Version(self.version)
        # python component: "Build a C extension for Python"
        self.cpp_info.components["python"].includedirs.append(
            os.path.join("include", f"python{self._version_suffix}{self._abi_suffix}")
        )
        libdir = "lib"
        self.cpp_info.components["python"].defines.append("Py_ENABLE_SHARED" if self.options.shared else "Py_NO_ENABLE_SHARED")
        self.cpp_info.components["python"].set_property("pkg_config_name", f"python-{py_version.major}.{py_version.minor}")
        self.cpp_info.components["python"].set_property("pkg_config_aliases", [f"python{py_version.major}"])
        self.cpp_info.components["python"].libdirs = []

        # embed component: "Embed Python into an application"
        self.cpp_info.components["embed"].libs = [self._lib_name]
        self.cpp_info.components["embed"].libdirs = [libdir]
        self.cpp_info.components["embed"].includedirs = []
        self.cpp_info.components["embed"].set_property("pkg_config_name", f"python-{py_version.major}.{py_version.minor}-embed")
        self.cpp_info.components["embed"].set_property("pkg_config_aliases", [f"python{py_version.major}-embed"])
        self.cpp_info.components["embed"].requires = ["python"]

        # Transparent integration with CMake's FindPython(3)
        self.cpp_info.set_property("cmake_file_name", "Python3")
        self.cpp_info.set_property("cmake_module_file_name", "Python")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_build_modules", [os.path.join(self._cmake_module_path, "use_conan_python.cmake")])
        self.cpp_info.builddirs = [self._cmake_module_path]

        python = self._cpython_interpreter_path
        self.conf_info.define("user.cpython:python", python)

        self.conf_info.define("user.cpython:pythonhome", self.package_folder)
        self.conf_info.define("user.cpython:module_requires_pythonhome", True)

        python_root = self.package_folder
        self.conf_info.define("user.cpython:python_root", python_root)

    @property
    def _version_suffix(self):
        v = Version(self.version)
        return f"{v.major}.{v.minor}"

    def rewrite_shebangs(self):
        for filename in os.listdir(os.path.join(self.package_folder, "bin")):
            filepath = os.path.join(self.package_folder, "bin", filename)
            if not os.path.isfile(filepath) or os.path.islink(filepath):
                continue
            with open(filepath, "rb") as fn:
                firstline = fn.readline(1024)
                if not(firstline.startswith(b"#!") and b"/python" in firstline and b"/bin/sh" not in firstline):
                    continue
                text = fn.read()
            self.output.info(f"Rewriting shebang of {filename}")
            with open(filepath, "wb") as fn:
                fn.write(textwrap.dedent(f"""\
                    #!/bin/sh
                    ''':'
                    __file__="$0"
                    while [ -L "$__file__" ]; do
                        __file__="$(dirname "$__file__")/$(readlink "$__file__")"
                    done
                    exec "$(dirname "$__file__")/python{self._version_suffix}" "$0" "$@"
                    '''
                    """).encode())
                fn.write(text)


    @property
    def _exact_lib_name(self):
        if not self.options.shared:
            extension = "a"
        elif is_apple_os(self):
            extension = "dylib"
        else:
            extension = "so"
        return f"lib{self._lib_name}.{extension}"

    @property
    def _cmake_module_path(self):
        return os.path.join("lib", "cmake")

    def _write_cmake_findpython_wrapper_file(self):
        template = textwrap.dedent("""
        if (DEFINED Python3_VERSION_STRING)
            set(_CONAN_PYTHON_SUFFIX "3")
        else()
            set(_CONAN_PYTHON_SUFFIX "")
        endif()
        set(Python${_CONAN_PYTHON_SUFFIX}_EXECUTABLE @PYTHON_EXECUTABLE@)
        set(Python${_CONAN_PYTHON_SUFFIX}_LIBRARY @PYTHON_LIBRARY@)

        # Fails if these are set beforehand
        unset(Python${_CONAN_PYTHON_SUFFIX}_INCLUDE_DIRS)
        unset(Python${_CONAN_PYTHON_SUFFIX}_INCLUDE_DIR)

        include(${CMAKE_ROOT}/Modules/FindPython${_CONAN_PYTHON_SUFFIX}.cmake)

        # Sanity check: The former comes from FindPython(3), the latter comes from the injected find module
        if(NOT Python${_CONAN_PYTHON_SUFFIX}_VERSION STREQUAL Python${_CONAN_PYTHON_SUFFIX}_VERSION_STRING)
            message(FATAL_ERROR "CMake detected wrong cpython version - this is likely a bug with the cpython Conan package")
        endif()

        if (TARGET Python${_CONAN_PYTHON_SUFFIX}::Module)
            set_target_properties(Python${_CONAN_PYTHON_SUFFIX}::Module PROPERTIES INTERFACE_LINK_LIBRARIES cpython::python)
        endif()
        if (TARGET Python${_CONAN_PYTHON_SUFFIX}::SABIModule)
            set_target_properties(Python${_CONAN_PYTHON_SUFFIX}::SABIModule PROPERTIES INTERFACE_LINK_LIBRARIES cpython::python)
        endif()
        if (TARGET Python${_CONAN_PYTHON_SUFFIX}::Python)
            set_target_properties(Python${_CONAN_PYTHON_SUFFIX}::Python PROPERTIES INTERFACE_LINK_LIBRARIES cpython::embed)
        endif()
        """)

        # In order for the package to be relocatable, these variables must be relative to the installed CMake file
        python_exe = "${CMAKE_CURRENT_LIST_DIR}/../../bin/" + self._cpython_interpreter_name
        python_library = "${CMAKE_CURRENT_LIST_DIR}/../" + self._exact_lib_name

        cmake_file = os.path.join(self.package_folder, self._cmake_module_path, "use_conan_python.cmake")
        content = template.replace("@PYTHON_EXECUTABLE@", python_exe).replace("@PYTHON_LIBRARY@", python_library)
        save(self, cmake_file, content)

    @property
    def _cpython_symlink(self):
        return os.path.join(self.package_folder, "bin", "python")

    @property
    def _cpython_interpreter_name(self):
        return "python" + self._version_suffix

    @property
    def _cpython_interpreter_path(self):
        return os.path.join(self.package_folder, "bin", self._cpython_interpreter_name)

    @property
    def _abi_suffix(self):
        return "d" if self.settings.build_type == "Debug" else ""

    @property
    def _lib_name(self):
        return f"python{self._version_suffix}{self._abi_suffix}"

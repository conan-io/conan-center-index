from conan.tools.build import cross_building
from conan.tools.files import rename, rmdir, get
from conan.tools.files.patches import apply_conandata_patches
from conan.tools.microsoft import msvc_runtime_flag
from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conans import tools
from conan.tools.scm import Version

import glob
import os
import re
import sys
import shlex
import shutil
import yaml

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

required_conan_version = ">=1.47.0"


# When adding (or removing) an option, also add this option to the list in
# `rebuild-dependencies.yml` and re-run that script.
CONFIGURE_OPTIONS = (
    "atomic",
    "chrono",
    "container",
    "context",
    "contract",
    "coroutine",
    "date_time",
    "exception",
    "fiber",
    "filesystem",
    "graph",
    "graph_parallel",
    "iostreams",
    "json",
    "locale",
    "log",
    "math",
    "mpi",
    "nowide",
    "program_options",
    "python",
    "random",
    "regex",
    "serialization",
    "stacktrace",
    "system",
    "test",
    "thread",
    "timer",
    "type_erasure",
    "wave",
)


class BoostConan(ConanFile):
    name = "boost"
    settings = "os", "arch", "compiler", "build_type"
    description = "Boost provides free peer-reviewed portable C++ source libraries"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.boost.org"
    license = "BSL-1.0"
    topics = ("libraries", "cpp")

    _options = None

    options = {
        "shared": [True, False],
        "header_only": [True, False],
        "error_code_header_only": [True, False],
        "system_no_deprecated": [True, False],
        "asio_no_deprecated": [True, False],
        "filesystem_no_deprecated": [True, False],
        "filesystem_version": [None, "3", "4"],
        "fPIC": [True, False],
        "layout": ["system", "versioned", "tagged", "b2-default"],
        "magic_autolink": [True, False],  # enables BOOST_ALL_NO_LIB
        "diagnostic_definitions": [True, False],  # enables BOOST_LIB_DIAGNOSTIC
        "python_executable": "ANY",  # system default python installation is used, if None
        "python_version": "ANY",  # major.minor; computed automatically, if None
        "namespace": "ANY",  # custom boost namespace for bcp, e.g. myboost
        "namespace_alias": [True, False],  # enable namespace alias for bcp, boost=myboost
        "multithreading": [True, False],  # enables multithreading support
        "numa": [True, False],
        "zlib": [True, False],
        "bzip2": [True, False],
        "lzma": [True, False],
        "zstd": [True, False],
        "segmented_stacks": [True, False],
        "debug_level": list(range(0, 14)),
        "pch": [True, False],
        "extra_b2_flags": "ANY",  # custom b2 flags
        "i18n_backend": ["iconv", "icu", None, "deprecated"],
        "i18n_backend_iconv": ["libc", "libiconv", "off"],
        "i18n_backend_icu": [True, False],
        "visibility": ["global", "protected", "hidden"],
        "addr2line_location": "ANY",
        "with_stacktrace_backtrace": [True, False],
        "buildid": "ANY",
        "python_buildid": "ANY",
        "system_use_utf8": [True, False],
    }
    options.update({f"without_{_name}": [True, False] for _name in CONFIGURE_OPTIONS})

    default_options = {
        "shared": False,
        "header_only": False,
        "error_code_header_only": False,
        "system_no_deprecated": False,
        "asio_no_deprecated": False,
        "filesystem_no_deprecated": False,
        "filesystem_version": None,
        "fPIC": True,
        "layout": "system",
        "magic_autolink": False,
        "diagnostic_definitions": False,
        "python_executable": "None",
        "python_version": "None",
        "namespace": "boost",
        "namespace_alias": False,
        "multithreading": True,
        "numa": True,
        "zlib": True,
        "bzip2": True,
        "lzma": False,
        "zstd": False,
        "segmented_stacks": False,
        "debug_level": 0,
        "pch": True,
        "extra_b2_flags": "None",
        "i18n_backend": "deprecated",
        "i18n_backend_iconv": "libc",
        "i18n_backend_icu": False,
        "visibility": "hidden",
        "addr2line_location": "/usr/bin/addr2line",
        "with_stacktrace_backtrace": True,
        "buildid": None,
        "python_buildid": None,
        "system_use_utf8": False,
    }
    default_options.update({f"without_{_name}": False for _name in CONFIGURE_OPTIONS})
    default_options.update({f"without_{_name}": True for _name in ("graph_parallel", "mpi", "python")})

    short_paths = True
    no_copy_source = True
    _cached_dependencies = None

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def export(self):
        self.copy(self._dependency_filename, src="dependencies", dst="dependencies")

    @property
    def _min_compiler_version_default_cxx11(self):
        # Minimum compiler version having c++ standard >= 11
        if self.settings.compiler == "apple-clang":
            # For now, assume apple-clang will enable c++11 in the distant future
            return 99
        return {
            "gcc": 6,
            "clang": 6,
            "Visual Studio": 14,  # guess
        }.get(str(self.settings.compiler))

    @property
    def _min_compiler_version_nowide(self):
        # Nowide needs c++11 + swappable std::fstream
        return {
            "gcc": 5,
            "clang": 5,
            "Visual Studio": 14,  # guess
        }.get(str(self.settings.compiler))

    @property
    def _dependency_filename(self):
        return f"dependencies-{self.version}.yml"

    @property
    def _dependencies(self):
        if self._cached_dependencies is None:
            dependencies_filepath = os.path.join(self.recipe_folder, "dependencies", self._dependency_filename)
            if not os.path.isfile(dependencies_filepath):
                raise ConanException(f"Cannot find {dependencies_filepath}")
            with open(dependencies_filepath, encoding='utf-8') as f:
                self._cached_dependencies = yaml.safe_load(f)
        return self._cached_dependencies

    def _all_dependent_modules(self, name):
        dependencies = {name}
        while True:
            new_dependencies = set()
            for dependency in dependencies:
                new_dependencies.update(set(self._dependencies["dependencies"][dependency]))
                new_dependencies.update(dependencies)
            if len(new_dependencies) > len(dependencies):
                dependencies = new_dependencies
            else:
                break
        return dependencies

    def _all_super_modules(self, name):
        dependencies = {name}
        while True:
            new_dependencies = set(dependencies)
            for module in self._dependencies["dependencies"]:
                if dependencies.intersection(set(self._dependencies["dependencies"][module])):
                    new_dependencies.add(module)
            if len(new_dependencies) > len(dependencies):
                dependencies = new_dependencies
            else:
                break
        return dependencies

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _bcp_dir(self):
        return "custom-boost"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _is_clang_cl(self):
        return self.settings.os == "Windows" and self.settings.compiler == "clang"

    @property
    def _zip_bzip2_requires_needed(self):
        return not self.options.without_iostreams and not self.options.header_only

    @property
    def _python_executable(self):
        """
        obtain full path to the python interpreter executable
        :return: path to the python interpreter executable, either set by option, or system default
        """
        exe = self.options.python_executable if self.options.python_executable else sys.executable
        return str(exe).replace("\\", "/")

    @property
    def _is_windows_platform(self):
        return self.settings.os in ["Windows", "WindowsStore", "WindowsCE"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        # Test whether all config_options from the yml are available in CONFIGURE_OPTIONS
        for opt_name in self._configure_options:
            if f"without_{opt_name}" not in self.options:
                raise ConanException(f"{self._dependency_filename} has the configure options {opt_name} which is not available in conanfile.py")

        # stacktrace_backtrace not supported on Windows
        if self.settings.os == "Windows":
            del self.options.with_stacktrace_backtrace

        # nowide requires a c++11-able compiler + movable std::fstream: change default to not build on compiler with too old default c++ standard or too low compiler.cppstd
        # json requires a c++11-able compiler: change default to not build on compiler with too old default c++ standard or too low compiler.cppstd
        if self.settings.compiler.cppstd:
            if not tools.valid_min_cppstd(self, 11):
                self.options.without_fiber = True
                self.options.without_nowide = True
                self.options.without_json = True
        else:
            version_cxx11_standard_json = self._min_compiler_version_default_cxx11
            if version_cxx11_standard_json:
                if Version(self.settings.compiler.version) < version_cxx11_standard_json:
                    self.options.without_fiber = True
                    self.options.without_json = True
                    self.options.without_nowide = True
            else:
                self.options.without_fiber = True
                self.options.without_json = True
                self.options.without_nowide = True

        # iconv is off by default on Windows and Solaris
        if self._is_windows_platform or self.settings.os == "SunOS":
            self.options.i18n_backend_iconv = "off"
        elif tools.is_apple_os(self.settings.os):
            self.options.i18n_backend_iconv = "libiconv"
        elif self.settings.os == "Android":
            # bionic provides iconv since API level 28
            api_level = self.settings.get_safe("os.api_level")
            if api_level and Version(api_level) < "28":
                self.options.i18n_backend_iconv = "libiconv"

        # Remove options not supported by this version of boost
        for dep_name in CONFIGURE_OPTIONS:
            if dep_name not in self._configure_options:
                delattr(self.options, f"without_{dep_name}")

        if Version(self.version) >= "1.76.0":
            # Starting from 1.76.0, Boost.Math requires a c++11 capable compiler
            # ==> disable it by default for older compilers or c++ standards

            def disable_math():
                super_modules = self._all_super_modules("math")
                for smod in super_modules:
                    try:
                        setattr(self.options, f"without_{smod}", True)
                    except ConanException:
                        pass

            if self.settings.compiler.cppstd:
                if not tools.valid_min_cppstd(self, 11):
                    disable_math()
            else:
                min_compiler_version = self._min_compiler_version_default_cxx11
                if min_compiler_version is None:
                    self.output.warn("Assuming the compiler supports c++11 by default")
                elif Version(self.settings.compiler.version) < min_compiler_version:
                    disable_math()

        if Version(self.version) >= "1.79.0":
            # Starting from 1.79.0, Boost.Wave requires a c++11 capable compiler
            # ==> disable it by default for older compilers or c++ standards

            def disable_wave():
                super_modules = self._all_super_modules("wave")
                for smod in super_modules:
                    try:
                        setattr(self.options, f"without_{smod}", True)
                    except ConanException:
                        pass

            if self.settings.compiler.cppstd:
                if not tools.valid_min_cppstd(self, 11):
                    disable_wave()
            else:
                min_compiler_version = self._min_compiler_version_default_cxx11
                if min_compiler_version is None:
                    self.output.warn("Assuming the compiler supports c++11 by default")
                elif Version(self.settings.compiler.version) < min_compiler_version:
                    disable_wave()

    @property
    def _configure_options(self):
        return self._dependencies["configure_options"]

    @property
    def _fPIC(self):
        return self.options.get_safe("fPIC", self.default_options["fPIC"])

    @property
    def _shared(self):
        return self.options.get_safe("shared", self.default_options["shared"])

    @property
    def _stacktrace_addr2line_available(self):
        if (self.settings.os in ["iOS", "watchOS", "tvOS"] or self.settings.get_safe("os.subsystem") == "catalyst"):
             # sandboxed environment - cannot launch external processes (like addr2line), system() function is forbidden
            return False
        return not self.options.header_only and not self.options.without_stacktrace and self.settings.os != "Windows"

    def configure(self):
        if self.options.header_only:
            del self.options.shared
            del self.options.fPIC
        elif self.options.shared:
            del self.options.fPIC

        if self.options.i18n_backend != "deprecated":
            self.output.warn("i18n_backend option is deprecated, do not use anymore.")
            if self.options.i18n_backend == "iconv":
                self.options.i18n_backend_iconv = "libiconv"
                self.options.i18n_backend_icu = False
            if self.options.i18n_backend == "icu":
                self.options.i18n_backend_iconv = "off"
                self.options.i18n_backend_icu = True
            if self.options.i18n_backend == "None":
                self.options.i18n_backend_iconv = "off"
                self.options.i18n_backend_icu = False
        if self.options.without_locale:
            del self.options.i18n_backend_iconv
            del self.options.i18n_backend_icu

        if not self.options.without_python:
            if not self.options.python_version:
                self.options.python_version = self._detect_python_version()
                self.options.python_executable = self._python_executable
        else:
            del self.options.python_buildid

        if not self._stacktrace_addr2line_available:
            del self.options.addr2line_location

        if self.options.get_safe("without_stacktrace", True):
            del self.options.with_stacktrace_backtrace

        if self.options.layout == "b2-default":
            self.options.layout = "versioned" if self.settings.os == "Windows" else "system"

        if self.options.without_fiber:
            del self.options.numa

    def validate(self):
        if not self.options.multithreading:
            # * For the reason 'thread' is deactivate look at https://stackoverflow.com/a/20991533
            #   Look also on the comments of the answer for more details
            # * Although the 'context' and 'atomic' library does not mention anything about threading,
            #   when being build the compiler uses the -pthread flag, which makes it quite dangerous
            for lib in ["locale", "coroutine", "wave", "type_erasure", "fiber", "thread", "context", "atomic"]:
                if not self.options.get_safe(f"without_{lib}"):
                    raise ConanInvalidConfiguration(f"Boost '{lib}' library requires multi threading")

        if self._is_msvc and self._shared and "MT" in msvc_runtime_flag(self):
            raise ConanInvalidConfiguration("Boost can not be built as shared library with MT runtime.")

        if not self.options.without_locale and self.options.i18n_backend_iconv == "off" and \
           not self.options.i18n_backend_icu and not self._is_windows_platform:
            raise ConanInvalidConfiguration(
                "Boost.Locale library needs either iconv or ICU library to be built on non windows platforms"
            )

        if self._stacktrace_addr2line_available:
            if not os.path.isabs(str(self.options.addr2line_location)):
                raise ConanInvalidConfiguration("addr2line_location must be an absolute path to addr2line")

        # Check, when a boost module is enabled, whether the boost modules it depends on are enabled as well.
        for mod_name, mod_deps in self._dependencies["dependencies"].items():
            if not self.options.get_safe(f"without_{mod_name}", True):
                for mod_dep in mod_deps:
                    if self.options.get_safe(f"without_{mod_dep}", False):
                        raise ConanInvalidConfiguration(f"{mod_name} requires {mod_deps}: {mod_dep} is disabled")

        if not self.options.get_safe("without_nowide", True):
            # nowide require a c++11-able compiler with movable std::fstream
            mincompiler_version = self._min_compiler_version_nowide
            if mincompiler_version:
                if Version(self.settings.compiler.version) < mincompiler_version:
                    raise ConanInvalidConfiguration("This compiler is too old to build Boost.nowide.")

            if self.settings.compiler.cppstd:
                tools.check_min_cppstd(self, 11)
            else:
                version_cxx11_standard = self._min_compiler_version_default_cxx11
                if version_cxx11_standard:
                    if Version(self.settings.compiler.version) < version_cxx11_standard:
                        raise ConanInvalidConfiguration("Boost.{fiber,json} require a c++11 compiler (please set compiler.cppstd or use a newer compiler)")
                else:
                    self.output.warn("I don't know what the default c++ standard of this compiler is. I suppose it supports c++11 by default.\n"
                                     "This might cause some boost libraries not being built and conan components to fail.")

        if not all((self.options.without_fiber, self.options.get_safe("without_json", True))):
            # fiber/json require a c++11-able compiler.
            if self.settings.compiler.cppstd:
                tools.check_min_cppstd(self, 11)
            else:
                version_cxx11_standard = self._min_compiler_version_default_cxx11
                if version_cxx11_standard:
                    if Version(self.settings.compiler.version) < version_cxx11_standard:
                        raise ConanInvalidConfiguration("Boost.{fiber,json} requires a c++11 compiler (please set compiler.cppstd or use a newer compiler)")
                else:
                    self.output.warn("I don't know what the default c++ standard of this compiler is. I suppose it supports c++11 by default.\n"
                                     "This might cause some boost libraries not being built and conan components to fail.")

        if Version(self.version) >= "1.76.0":
            # Starting from 1.76.0, Boost.Math requires a compiler with c++ standard 11 or higher
            if not self.options.without_math:
                if self.settings.compiler.cppstd:
                    tools.check_min_cppstd(self, 11)
                else:
                    min_compiler_version = self._min_compiler_version_default_cxx11
                    if min_compiler_version is not None:
                        if Version(self.settings.compiler.version) < min_compiler_version:
                            raise ConanInvalidConfiguration("Boost.Math requires (boost:)cppstd>=11 (current one is lower)")

        if Version(self.version) >= "1.79.0":
            # Starting from 1.79.0, Boost.Wave requires a compiler with c++ standard 11 or higher
            if not self.options.without_wave:
                if self.settings.compiler.cppstd:
                    tools.check_min_cppstd(self, 11)
                else:
                    min_compiler_version = self._min_compiler_version_default_cxx11
                    if min_compiler_version is not None:
                        if Version(self.settings.compiler.version) < min_compiler_version:
                            raise ConanInvalidConfiguration("Boost.Wave requires (boost:)cppstd>=11 (current one is lower)")

    def _with_dependency(self, dependency):
        """
        Return true when dependency is required according to the dependencies-x.y.z.yml file
        """
        for name, reqs in self._dependencies["requirements"].items():
            if dependency in reqs:
                if not self.options.get_safe(f"without_{name}", True):
                    return True
        return False

    @property
    def _with_zlib(self):
        return not self.options.header_only and self._with_dependency("zlib") and self.options.zlib

    @property
    def _with_bzip2(self):
        return not self.options.header_only and self._with_dependency("bzip2") and self.options.bzip2

    @property
    def _with_lzma(self):
        return not self.options.header_only and self._with_dependency("lzma") and self.options.lzma

    @property
    def _with_zstd(self):
        return not self.options.header_only and self._with_dependency("zstd") and self.options.zstd

    @property
    def _with_icu(self):
        return not self.options.header_only and self._with_dependency("icu") and self.options.get_safe("i18n_backend_icu")

    @property
    def _with_iconv(self):
        return not self.options.header_only and self._with_dependency("iconv") and self.options.get_safe("i18n_backend_iconv") == "libiconv"

    @property
    def _with_stacktrace_backtrace(self):
        return not self.options.header_only and self.options.get_safe("with_stacktrace_backtrace", False)

    def requirements(self):
        if self._with_zlib:
            self.requires("zlib/1.2.12")
        if self._with_bzip2:
            self.requires("bzip2/1.0.8")
        if self._with_lzma:
            self.requires("xz_utils/5.2.5")
        if self._with_zstd:
            self.requires("zstd/1.5.2")
        if self._with_stacktrace_backtrace:
            self.requires("libbacktrace/cci.20210118")

        if self._with_icu:
            self.requires("icu/71.1")
        if self._with_iconv:
            self.requires("libiconv/1.17")

    def package_id(self):
        del self.info.options.i18n_backend

        if self.options.header_only:
            self.info.header_only()
            self.info.options.header_only = True
        else:
            del self.info.options.debug_level
            del self.info.options.filesystem_version
            del self.info.options.pch
            del self.info.options.python_executable  # PATH to the interpreter is not important, only version matters
            if self.options.without_python:
                del self.info.options.python_version
            else:
                self.info.options.python_version = self._python_version

    def build_requirements(self):
        if not self.options.header_only:
            self.build_requires("b2/4.9.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)
        apply_conandata_patches(self)

    ##################### BUILDING METHODS ###########################

    def _run_python_script(self, script):
        """
        execute python one-liner script and return its output
        :param script: string containing python script to be executed
        :return: output of the python script execution, or None, if script has failed
        """
        output = StringIO()
        command = f'"{self._python_executable}" -c "{script}"'
        self.output.info(f"running {command}")
        try:
            self.run(command=command, output=output)
        except ConanException:
            self.output.info("(failed)")
            return None
        output = output.getvalue()
        # Conan is broken when run_to_output = True
        if "\n-----------------\n" in output:
            output = output.split("\n-----------------\n", 1)[1]
        output = output.strip()
        return output if output != "None" else None

    def _get_python_path(self, name):
        """
        obtain path entry for the python installation
        :param name: name of the python config entry for path to be queried (such as "include", "platinclude", etc.)
        :return: path entry from the sysconfig
        """
        # https://docs.python.org/3/library/sysconfig.html
        # https://docs.python.org/2.7/library/sysconfig.html
        return self._run_python_script("from __future__ import print_function; "
                                       "import sysconfig; "
                                       f"print(sysconfig.get_path('{name}'))")

    def _get_python_sc_var(self, name):
        """
        obtain value of python sysconfig variable
        :param name: name of variable to be queried (such as LIBRARY or LDLIBRARY)
        :return: value of python sysconfig variable
        """
        return self._run_python_script("from __future__ import print_function; "
                                       "import sysconfig; "
                                       f"print(sysconfig.get_config_var('{name}'))")

    def _get_python_du_var(self, name):
        """
        obtain value of python distutils sysconfig variable
        (sometimes sysconfig returns empty values, while python.sysconfig provides correct values)
        :param name: name of variable to be queried (such as LIBRARY or LDLIBRARY)
        :return: value of python sysconfig variable
        """
        return self._run_python_script("from __future__ import print_function; "
                                       "import distutils.sysconfig as du_sysconfig; "
                                       f"print(du_sysconfig.get_config_var('{name}'))")

    def _get_python_var(self, name):
        """
        obtain value of python variable, either by sysconfig, or by distutils.sysconfig
        :param name: name of variable to be queried (such as LIBRARY or LDLIBRARY)
        :return: value of python sysconfig variable

        NOTE: distutils is deprecated and breaks the recipe since Python 3.10
        """
        python_version_parts = self.info.options.python_version.split('.')
        python_major = int(python_version_parts[0])
        python_minor = int(python_version_parts[1])
        if(python_major >= 3 and python_minor >= 10):
            return self._get_python_sc_var(name)

        return self._get_python_sc_var(name) or self._get_python_du_var(name)

    def _detect_python_version(self):
        """
        obtain version of python interpreter
        :return: python interpreter version, in format major.minor
        """
        return self._run_python_script("from __future__ import print_function; "
                                       "import sys; "
                                       "print('{}.{}'.format(sys.version_info[0], sys.version_info[1]))")


    @property
    def _python_version(self):
        version = self._detect_python_version()
        if self.options.python_version and version != self.options.python_version:
            raise ConanInvalidConfiguration(f"detected python version {version} doesn't match conan option {self.options.python_version}")
        return version

    @property
    def _python_inc(self):
        """
        obtain the result of the "sysconfig.get_python_inc()" call
        :return: result of the "sysconfig.get_python_inc()" execution
        """
        return self._run_python_script("from __future__ import print_function; "
                                       "import sysconfig; "
                                       "print(sysconfig.get_python_inc())")

    @property
    def _python_abiflags(self):
        """
        obtain python ABI flags, see https://www.python.org/dev/peps/pep-3149/ for the details
        :return: the value of python ABI flags
        """
        return self._run_python_script("from __future__ import print_function; "
                                       "import sys; "
                                       "print(getattr(sys, 'abiflags', ''))")

    @property
    def _python_includes(self):
        """
        attempt to find directory containing Python.h header file
        :return: the directory with python includes
        """
        include = self._get_python_path("include")
        plat_include = self._get_python_path("platinclude")
        include_py = self._get_python_var("INCLUDEPY")
        include_dir = self._get_python_var("INCLUDEDIR")
        python_inc = self._python_inc

        candidates = [include,
                      plat_include,
                      include_py,
                      include_dir,
                      python_inc]
        for candidate in candidates:
            if candidate:
                python_h = os.path.join(candidate, 'Python.h')
                self.output.info(f"checking {python_h}")
                if os.path.isfile(python_h):
                    self.output.info(f"found Python.h: {python_h}")
                    return candidate.replace("\\", "/")
        raise Exception("couldn't locate Python.h - make sure you have installed python development files")

    @property
    def _python_library_dir(self):
        """
        attempt to find python development library
        :return: the full path to the python library to be linked with
        """
        library = self._get_python_var("LIBRARY")
        ldlibrary = self._get_python_var("LDLIBRARY")
        libdir = self._get_python_var("LIBDIR")
        multiarch = self._get_python_var("MULTIARCH")
        masd = self._get_python_var("multiarchsubdir")
        with_dyld = self._get_python_var("WITH_DYLD")
        if libdir and multiarch and masd:
            if masd.startswith(os.sep):
                masd = masd[len(os.sep):]
            libdir = os.path.join(libdir, masd)

        if not libdir:
            libdest = self._get_python_var("LIBDEST")
            libdir = os.path.join(os.path.dirname(libdest), "libs")

        candidates = [ldlibrary, library]
        library_prefixes = [""] if self._is_msvc else ["", "lib"]
        library_suffixes = [".lib"] if self._is_msvc else [".so", ".dll.a", ".a"]
        if with_dyld:
            library_suffixes.insert(0, ".dylib")

        python_version = self._python_version
        python_version_no_dot = python_version.replace(".", "")
        versions = ["", python_version, python_version_no_dot]
        abiflags = self._python_abiflags

        for prefix in library_prefixes:
            for suffix in library_suffixes:
                for version in versions:
                    candidates.append(f"{prefix}python{version}{abiflags}{suffix}")

        for candidate in candidates:
            if candidate:
                python_lib = os.path.join(libdir, candidate)
                self.output.info(f"checking {python_lib}")
                if os.path.isfile(python_lib):
                    self.output.info(f"found python library: {python_lib}")
                    return libdir.replace("\\", "/")
        raise ConanInvalidConfiguration("couldn't locate python libraries - make sure you have installed python development files")

    def _clean(self):
        src = os.path.join(self.source_folder, self._source_subfolder)
        clean_dirs = [
            os.path.join(self.build_folder, "bin.v2"),
            os.path.join(self.build_folder, "architecture"),
            os.path.join(self.source_folder, self._bcp_dir),
            os.path.join(src, "dist", "bin"),
            os.path.join(src, "stage"),
            os.path.join(src, "tools", "build", "src", "engine", "bootstrap"),
            os.path.join(src, "tools", "build", "src", "engine", "bin.ntx86"),
            os.path.join(src, "tools", "build", "src", "engine", "bin.ntx86_64"),
        ]
        for d in clean_dirs:
            if os.path.isdir(d):
                self.output.warn(f"removing '{d}'")
                shutil.rmtree(d)

    @property
    def _b2_exe(self):
        return "b2.exe" if tools.os_info.is_windows else "b2"

    @property
    def _bcp_exe(self):
        folder = os.path.join(self.source_folder, self._source_subfolder, "dist", "bin")
        return os.path.join(folder, "bcp.exe" if tools.os_info.is_windows else "bcp")

    @property
    def _use_bcp(self):
        return self.options.namespace != "boost"

    @property
    def _boost_dir(self):
        return self._bcp_dir if self._use_bcp else self._source_subfolder

    @property
    def _boost_build_dir(self):
        return os.path.join(self.source_folder, self._source_subfolder, "tools", "build")

    def _build_bcp(self):
        folder = os.path.join(self.source_folder, self._source_subfolder, "tools", "bcp")
        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            with tools.chdir(folder):
                command = f"{self._b2_exe} -j{tools.cpu_count()} --abbreviate-paths toolset={self._toolset}"
                command += " -d%d" % self.options.debug_level
                self.output.warn(command)
                self.run(command, run_environment=True)

    def _run_bcp(self):
        with tools.vcvars(self.settings) if self._is_msvc or self._is_clang_cl else tools.no_op():
            with tools.chdir(self.source_folder):
                os.mkdir(self._bcp_dir)
                namespace = f"--namespace={self.options.namespace}"
                alias = "--namespace-alias" if self.options.namespace_alias else ""
                boostdir = f"--boost={self._source_subfolder}"
                libraries = {"build", "boost-build.jam", "boostcpp.jam", "boost_install", "headers"}
                for d in os.listdir(os.path.join(self._source_subfolder, "boost")):
                    if os.path.isdir(os.path.join(self._source_subfolder, "boost", d)):
                        libraries.add(d)
                for d in os.listdir(os.path.join(self._source_subfolder, "libs")):
                    if os.path.isdir(os.path.join(self._source_subfolder, "libs", d)):
                        libraries.add(d)
                libraries = " ".join(libraries)
                command = f"{self._bcp_exe} {namespace} {alias} {boostdir} {libraries} {self._bcp_dir}"
                self.output.warn(command)
                self.run(command)

    def build(self):
        if cross_building(self, skip_x64_x86=True):
            # When cross building, do not attempt to run the test-executable (assume they work)
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "libs", "stacktrace", "build", "Jamfile.v2"),
                                  "$(>) > $(<)",
                                  "echo \"\" > $(<)", strict=False)
        # Older clang releases require a thread_local variable to be initialized by a constant value
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "boost", "stacktrace", "detail", "libbacktrace_impls.hpp"),
                              "/* thread_local */", "thread_local", strict=False)
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "boost", "stacktrace", "detail", "libbacktrace_impls.hpp"),
                              "/* static __thread */", "static __thread", strict=False)
        if self.settings.compiler == "apple-clang" or (self.settings.compiler == "clang" and Version(self.settings.compiler.version) < 6):
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "boost", "stacktrace", "detail", "libbacktrace_impls.hpp"),
                                  "thread_local", "/* thread_local */")
            tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "boost", "stacktrace", "detail", "libbacktrace_impls.hpp"),
                                  "static __thread", "/* static __thread */")
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "tools", "build", "src", "tools", "gcc.jam"),
                              "local generic-os = [ set.difference $(all-os) : aix darwin vxworks solaris osf hpux ] ;",
                              "local generic-os = [ set.difference $(all-os) : aix darwin vxworks solaris osf hpux iphone appletv ] ;",
                              strict=False)
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "tools", "build", "src", "tools", "gcc.jam"),
                              "local no-threading = android beos haiku sgi darwin vxworks ;",
                              "local no-threading = android beos haiku sgi darwin vxworks iphone appletv ;",
                              strict=False)
        tools.replace_in_file(os.path.join(self.source_folder, self._source_subfolder, "libs", "fiber", "build", "Jamfile.v2"),
                              "    <conditional>@numa",
                              "    <link>shared:<library>.//boost_fiber : <conditional>@numa",
                              strict=False)

        if self.options.header_only:
            self.output.warn("Header only package, skipping build")
            return

        self._clean()

        if self._use_bcp:
            self._build_bcp()
            self._run_bcp()

        # Help locating bzip2 and zlib
        self._create_user_config_jam(self._boost_build_dir)

        # JOIN ALL FLAGS
        b2_flags = " ".join(self._build_flags)
        full_command = f"{self._b2_exe} {b2_flags}"
        # -d2 is to print more debug info and avoid travis timing out without output
        sources = os.path.join(self.source_folder, self._boost_dir)
        full_command += f' --debug-configuration --build-dir="{self.build_folder}"'
        self.output.warn(full_command)

        # If sending a user-specified toolset to B2, setting the vcvars
        # interferes with the compiler selection.
        use_vcvars = self._is_msvc and not self.settings.compiler.get_safe("toolset", default="")
        with tools.vcvars(self.settings) if use_vcvars else tools.no_op():
            with tools.chdir(sources):
                # To show the libraries *1
                # self.run("%s --show-libraries" % b2_exe)
                self.run(full_command, run_environment=True)

    @property
    def _b2_os(self):
        return {
            "Windows": "windows",
            "WindowsStore": "windows",
            "Linux": "linux",
            "Android": "android",
            "Macos": "darwin",
            "iOS": "iphone",
            "watchOS": "iphone",
            "tvOS": "appletv",
            "FreeBSD": "freebsd",
            "SunOS": "solaris",
        }.get(str(self.settings.os))

    @property
    def _b2_address_model(self):
        if self.settings.arch in ("x86_64", "ppc64", "ppc64le", "mips64", "armv8", "armv8.3", "sparcv9"):
            return "64"

        return "32"

    @property
    def _b2_binary_format(self):
        return {
            "Windows": "pe",
            "WindowsStore": "pe",
            "Linux": "elf",
            "Android": "elf",
            "Macos": "mach-o",
            "iOS": "mach-o",
            "watchOS": "mach-o",
            "tvOS": "mach-o",
            "FreeBSD": "elf",
            "SunOS": "elf",
        }.get(str(self.settings.os))

    @property
    def _b2_architecture(self):
        if str(self.settings.arch).startswith("x86"):
            return "x86"
        if str(self.settings.arch).startswith("ppc"):
            return "power"
        if str(self.settings.arch).startswith("arm"):
            return "arm"
        if str(self.settings.arch).startswith("sparc"):
            return "sparc"
        if str(self.settings.arch).startswith("mips64"):
            return "mips64"
        if str(self.settings.arch).startswith("mips"):
            return "mips1"
        if str(self.settings.arch).startswith("s390"):
            return "s390x"

        return None

    @property
    def _b2_abi(self):
        if str(self.settings.arch).startswith("x86"):
            return "ms" if str(self.settings.os) in ["Windows", "WindowsStore"] else "sysv"
        if str(self.settings.arch).startswith("ppc"):
            return "sysv"
        if str(self.settings.arch).startswith("arm"):
            return "aapcs"
        if str(self.settings.arch).startswith("mips"):
            return "o32"

        return None

    @property
    def _gnu_cxx11_abi(self):
        """Checks libcxx setting and returns value for the GNU C++11 ABI flag
        _GLIBCXX_USE_CXX11_ABI= .  Returns None if C++ library cannot be
        determined.
        """
        try:
            if str(self.settings.compiler.libcxx) == "libstdc++":
                return "0"
            if str(self.settings.compiler.libcxx) == "libstdc++11":
                return "1"
        except ConanException:
            pass
        return None

    @property
    def _build_flags(self):
        flags = self._build_cross_flags

        # Stop at the first error. No need to continue building.
        flags.append("-q")

        if self.options.get_safe("numa"):
            flags.append("numa=on")

        # https://www.boost.org/doc/libs/1_70_0/libs/context/doc/html/context/architectures.html
        if self._b2_os:
            flags.append(f"target-os={self._b2_os}")
        if self._b2_architecture:
            flags.append(f"architecture={self._b2_architecture}")
        if self._b2_address_model:
            flags.append(f"address-model={self._b2_address_model}")
        if self._b2_binary_format:
            flags.append(f"binary-format={self._b2_binary_format}")
        if self._b2_abi:
            flags.append(f"abi={self._b2_abi}")

        flags.append(f"--layout={self.options.layout}")
        flags.append(f"--user-config={os.path.join(self._boost_build_dir, 'user-config.jam')}")
        flags.append(f"-sNO_ZLIB={'0' if self._with_zlib else '1'}")
        flags.append(f"-sNO_BZIP2={'0' if self._with_bzip2 else '1'}")
        flags.append(f"-sNO_LZMA={'0' if self._with_lzma else '1'}")
        flags.append(f"-sNO_ZSTD={'0' if self._with_zstd else '1'}")

        if self.options.get_safe("i18n_backend_icu"):
            flags.append("boost.locale.icu=on")
        else:
            flags.append("boost.locale.icu=off")
            flags.append("--disable-icu")
        if self.options.get_safe("i18n_backend_iconv") in ["libc", "libiconv"]:
            flags.append("boost.locale.iconv=on")
            if self.options.get_safe("i18n_backend_iconv") == "libc":
                flags.append("boost.locale.iconv.lib=libc")
            else:
                flags.append("boost.locale.iconv.lib=libiconv")
        else:
            flags.append("boost.locale.iconv=off")
            flags.append("--disable-iconv")

        def add_defines(library):
            for define in self.deps_cpp_info[library].defines:
                flags.append(f"define={define}")

        if self._with_zlib:
            add_defines("zlib")
        if self._with_bzip2:
            add_defines("bzip2")
        if self._with_lzma:
            add_defines("xz_utils")
        if self._with_zstd:
            add_defines("zstd")

        if self._is_msvc:
            flags.append(f"runtime-link={'static' if 'MT' in msvc_runtime_flag(self) else 'shared'}" % ())
            flags.append(f"runtime-debugging={'on' if 'd' in msvc_runtime_flag(self) else 'off'}")

        # For details https://boostorg.github.io/build/manual/master/index.html
        flags.append(f"threading={'single' if not self.options.multithreading else 'multi'}")
        flags.append(f"visibility={self.options.visibility}")

        flags.append(f"link={'shared' if self._shared else 'static'}")
        if self.settings.build_type == "Debug":
            flags.append("variant=debug")
        else:
            flags.append("variant=release")

        for libname in self._configure_options:
            if not getattr(self.options, f"without_{libname}"):
                flags.append(f"--with-{libname}")

        flags.append(f"toolset={self._toolset}")

        if self.settings.get_safe("compiler.cppstd"):
            flags.append(f"cxxflags={tools.cppstd_flag(self.settings)}")

        # LDFLAGS
        link_flags = []

        # CXX FLAGS
        cxx_flags = []
        # fPIC DEFINITION
        if self._fPIC:
            cxx_flags.append("-fPIC")
        if self.settings.build_type == "RelWithDebInfo":
            if self.settings.compiler == "gcc" or "clang" in str(self.settings.compiler):
                cxx_flags.append("-g")
            elif self._is_msvc:
                cxx_flags.append("/Z7")


        # Standalone toolchain fails when declare the std lib
        if self.settings.os not in ("Android", "Emscripten"):
            try:
                if self._gnu_cxx11_abi:
                    flags.append(f"define=_GLIBCXX_USE_CXX11_ABI={self._gnu_cxx11_abi}")

                if self.settings.compiler in ("clang", "apple-clang"):
                    libcxx = {
                        "libstdc++11": "libstdc++",
                    }.get(str(self.settings.compiler.libcxx), str(self.settings.compiler.libcxx))
                    cxx_flags.append(f"-stdlib={libcxx}")
                    link_flags.append(f"-stdlib={libcxx}")
            except ConanException:
                pass

        if self.options.error_code_header_only:
            flags.append("define=BOOST_ERROR_CODE_HEADER_ONLY=1")
        if self.options.system_no_deprecated:
            flags.append("define=BOOST_SYSTEM_NO_DEPRECATED=1")
        if self.options.asio_no_deprecated:
            flags.append("define=BOOST_ASIO_NO_DEPRECATED=1")
        if self.options.filesystem_no_deprecated:
            flags.append("define=BOOST_FILESYSTEM_NO_DEPRECATED=1")
        if self.options.system_use_utf8:
            flags.append("define=BOOST_SYSTEM_USE_UTF8=1")
        if self.options.segmented_stacks:
            flags.extend(["segmented-stacks=on",
                          "define=BOOST_USE_SEGMENTED_STACKS=1",
                          "define=BOOST_USE_UCONTEXT=1"])
        flags.append("pch=on" if self.options.pch else "pch=off")

        if tools.is_apple_os(self.settings.os):
            if self.settings.get_safe("os.version"):
                cxx_flags.append(tools.apple_deployment_target_flag(self.settings.os,
                                                                    self.settings.get_safe("os.version"),
                                                                    self.settings.get_safe("os.sdk"),
                                                                    self.settings.get_safe("os.subsystem"),
                                                                    self.settings.get_safe("arch")))
                if self.settings.get_safe("os.subsystem") == "catalyst":
                    cxx_flags.append("--target=arm64-apple-ios-macabi")
                    link_flags.append("--target=arm64-apple-ios-macabi")

        if self.settings.os == "iOS":
            if self.options.multithreading:
                cxx_flags.append("-DBOOST_AC_USE_PTHREADS")
                cxx_flags.append("-DBOOST_SP_USE_PTHREADS")

            cxx_flags.append("-fembed-bitcode")

        if self._with_iconv:
            flags.append(f"-sICONV_PATH={self.deps_cpp_info['libiconv'].rootpath}")
        if self._with_icu:
            flags.append(f"-sICU_PATH={self.deps_cpp_info['icu'].rootpath}")
            if not self.options["icu"].shared:
                # Using ICU_OPTS to pass ICU system libraries is not possible due to Boost.Regex disallowing it.
                if self._is_msvc:
                    icu_ldflags = " ".join(f"{l}.lib" for l in self.deps_cpp_info["icu"].system_libs)
                else:
                    icu_ldflags = " ".join(f"-l{l}" for l in self.deps_cpp_info["icu"].system_libs)
                link_flags.append(icu_ldflags)

        link_flags = f'linkflags="{" ".join(link_flags)}"'
        flags.append(link_flags)

        if self.options.get_safe("addr2line_location"):
            cxx_flags.append(f"-DBOOST_STACKTRACE_ADDR2LINE_LOCATION={self.options.addr2line_location}")

        cxx_flags = f'cxxflags="{" ".join(cxx_flags)}"'
        flags.append(cxx_flags)

        if self.options.buildid:
            flags.append(f"--buildid={self.options.buildid}")
        if not self.options.without_python and self.options.python_buildid:
            flags.append(f"--python-buildid={self.options.python_buildid}")

        if self.options.extra_b2_flags:
            flags.extend(shlex.split(str(self.options.extra_b2_flags)))

        flags.extend([
            "install",
            f"--prefix={self.package_folder}",
            f"-j{tools.cpu_count()}",
            "--abbreviate-paths",
            "-d%d" % self.options.debug_level,
        ])
        return flags

    @property
    def _build_cross_flags(self):
        flags = []
        if not cross_building(self):
            return flags
        arch = self.settings.get_safe("arch")
        self.output.info("Cross building, detecting compiler...")

        if arch.startswith("arm"):
            if "hf" in arch:
                flags.append("-mfloat-abi=hard")
        elif self.settings.os == "Emscripten":
            pass
        elif arch in ["x86", "x86_64"]:
            pass
        elif arch.startswith("ppc"):
            pass
        elif arch.startswith("mips"):
            pass
        else:
            self.output.warn(f"Unable to detect the appropriate ABI for {arch} architecture.")
        self.output.info(f"Cross building flags: {flags}")

        return flags

    @property
    def _ar(self):
        if os.environ.get("AR"):
            return os.environ["AR"]
        if tools.is_apple_os(self.settings.os) and self.settings.compiler == "apple-clang":
            return tools.XCRun(self.settings).ar
        return None

    @property
    def _ranlib(self):
        if os.environ.get("RANLIB"):
            return os.environ["RANLIB"]
        if tools.is_apple_os(self.settings.os) and self.settings.compiler == "apple-clang":
            return tools.XCRun(self.settings).ranlib
        return None

    @property
    def _cxx(self):
        if os.environ.get("CXX"):
            return os.environ["CXX"]
        if tools.is_apple_os(self.settings.os) and self.settings.compiler == "apple-clang":
            return tools.XCRun(self.settings).cxx
        compiler_version = str(self.settings.compiler.version)
        major = compiler_version.split(".", maxsplit=1)[0]
        if self.settings.compiler == "gcc":
            return tools.which(f"g++-{compiler_version}") or tools.which(f"g++-{major}") or tools.which("g++") or ""
        if self.settings.compiler == "clang":
            return tools.which(f"clang++-{compiler_version}") or tools.which(f"clang++-{major}") or tools.which("clang++") or ""
        return ""

    def _create_user_config_jam(self, folder):
        """To help locating the zlib and bzip2 deps"""
        self.output.warn("Patching user-config.jam")

        contents = ""
        if self._zip_bzip2_requires_needed:
            def create_library_config(deps_name, name):
                includedir = '"%s"' % self.deps_cpp_info[deps_name].include_paths[0].replace("\\", "/")
                libdir = '"%s"' % self.deps_cpp_info[deps_name].lib_paths[0].replace("\\", "/")
                lib = self.deps_cpp_info[deps_name].libs[0]
                version = self.deps_cpp_info[deps_name].version
                return f"\nusing {name} : {version} : " \
                       f"<include>{includedir} " \
                       f"<search>{libdir} " \
                       f"<name>{lib} ;"

            contents = ""
            if self._with_zlib:
                contents += create_library_config("zlib", "zlib")
            if self._with_bzip2:
                contents += create_library_config("bzip2", "bzip2")
            if self._with_lzma:
                contents += create_library_config("xz_utils", "lzma")
            if self._with_zstd:
                contents += create_library_config("zstd", "zstd")

        if not self.options.without_python:
            # https://www.boost.org/doc/libs/1_70_0/libs/python/doc/html/building/configuring_boost_build.html
            contents += f'\nusing python : {self._python_version} : "{self._python_executable}" : "{self._python_includes}" : "{self._python_library_dir}" ;'

        if not self.options.without_mpi:
            # https://www.boost.org/doc/libs/1_72_0/doc/html/mpi/getting_started.html
            contents += "\nusing mpi ;"

        # Specify here the toolset with the binary if present if don't empty parameter :
        contents += f'\nusing "{self._toolset}" : {self._toolset_version} : '

        cxx_fwd_slahes = self._cxx.replace("\\", "/")
        if self._is_msvc:
            contents += f' "{cxx_fwd_slahes}"'
        else:
            contents += f' {cxx_fwd_slahes}'

        if tools.is_apple_os(self.settings.os):
            if self.settings.compiler == "apple-clang":
                contents += f" -isysroot {tools.XCRun(self.settings).sdk_path}"
            if self.settings.get_safe("arch"):
                contents += f" -arch {tools.to_apple_arch(self.settings.arch)}"

        contents += " : \n"
        if self._ar:
            ar_path = tools.which(self._ar).replace("\\", "/")
            contents += f'<archiver>"{ar_path}" '
        if self._ranlib:
            ranlib_path = tools.which(self._ranlib).replace("\\", "/")
            contents += f'<ranlib>"{ranlib_path}" '
        cxxflags = tools.get_env("CXXFLAGS", "") + " "
        cflags = tools.get_env("CFLAGS", "") + " "
        cppflags = tools.get_env("CPPFLAGS", "") + " "
        ldflags = tools.get_env("LDFLAGS", "") + " "
        asflags = tools.get_env("ASFLAGS", "") + " "

        if self._with_stacktrace_backtrace:
            cppflags += " ".join(f"-I{p}" for p in self.deps_cpp_info["libbacktrace"].include_paths) + " "
            ldflags += " ".join(f"-L{p}" for p in self.deps_cpp_info["libbacktrace"].lib_paths) + " "

        if cxxflags.strip():
            contents += f'<cxxflags>"{cxxflags.strip()}" '
        if cflags.strip():
            contents += f'<cflags>"{cflags.strip()}" '
        if cppflags.strip():
            contents += f'<compileflags>"{cppflags.strip()}" '
        if ldflags.strip():
            contents += f'<linkflags>"{ldflags.strip()}" '
        if asflags.strip():
            contents += f'<asmflags>"{asflags.strip()}" '

        contents += " ;"

        self.output.warn(contents)
        filename = f"{folder}/user-config.jam"
        tools.save(filename,  contents)

    @property
    def _toolset_version(self):
        if self._is_msvc:
            toolset = tools.msvs_toolset(self)
            match = re.match(r"v(\d+)(\d)$", toolset)
            if match:
                return f"{match.group(1)}.{match.group(2)}"
        return ""

    @property
    def _toolset(self):
        if self._is_msvc:
            return "clang-win" if self.settings.compiler.get_safe("toolset") == "ClangCL" else "msvc"
        if self.settings.os == "Windows" and self.settings.compiler == "clang":
            return "clang-win"
        if self.settings.os == "Emscripten" and self.settings.compiler == "clang":
            return "emscripten"
        if self.settings.compiler == "gcc" and tools.is_apple_os(self.settings.os):
            return "darwin"
        if self.settings.compiler == "apple-clang":
            return "clang-darwin"
        if self.settings.os == "Android" and self.settings.compiler == "clang":
            return "clang-linux"
        if self.settings.compiler in ["clang", "gcc"]:
            return str(self.settings.compiler)
        if self.settings.compiler == "sun-cc":
            return "sunpro"
        if self.settings.compiler == "intel":
            return {
                "Macos": "intel-darwin",
                "Windows": "intel-win",
                "Linux": "intel-linux",
            }[str(self.settings.os)]

        return str(self.settings.compiler)

    @property
    def _toolset_tag(self):
        # compiler       | compiler.version | os          | toolset_tag    | remark
        # ---------------+------------------+-------------+----------------+-----------------------------
        # apple-clang    | 12               | Macos       | darwin12       |
        # clang          | 12               | Macos       | clang-darwin12 |
        # gcc            | 11               | Linux       | gcc8           |
        # gcc            | 8                | Windows     | mgw8           |
        # Visual Studio  | 17               | Windows     | vc142          | depends on compiler.toolset
        compiler = {
            "apple-clang": "",
            "Visual Studio": "vc",
            "msvc": "vc",
        }.get(str(self.settings.compiler), str(self.settings.compiler))
        if (self.settings.compiler, self.settings.os) == ("gcc", "Windows"):
            compiler = "mgw"
        os_ = ""
        if self.settings.os == "Macos":
            os_ = "darwin"
        if self._is_msvc:
            toolset_version = self._toolset_version.replace(".", "")
        else:
            toolset_version = str(Version(self.settings.compiler.version).major)

        toolset_parts = [compiler, os_]
        toolset_tag = "-".join(part for part in toolset_parts if part) + toolset_version
        return toolset_tag

    ####################################################################

    def package(self):
        # This stage/lib is in source_folder... Face palm, looks like it builds in build but then
        # copy to source with the good lib name
        self.copy("LICENSE_1_0.txt", dst="licenses", src=os.path.join(self.source_folder,
                                                                      self._source_subfolder))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        if self.options.header_only:
            self.copy(pattern="*", dst="include/boost", src=f"{self._boost_dir}/boost")

        if self.settings.os == "Emscripten" and not self.options.header_only:
            self._create_emscripten_libs()

        if self._is_msvc and self._shared:
            # Some boost releases contain both static and shared variants of some libraries (if shared=True)
            all_libs = set(tools.collect_libs(self, "lib"))
            static_libs = set(l for l in all_libs if l.startswith("lib"))
            shared_libs = all_libs.difference(static_libs)
            static_libs = set(l[3:] for l in static_libs)
            common_libs = static_libs.intersection(shared_libs)
            for common_lib in common_libs:
                common_lib_fullname = f"lib{common_lib}.lib"
                self.output.info(f'Unlinking static duplicate library: {os.path.join(self.package_folder, "lib", common_lib_fullname)}')
                os.unlink(os.path.join(self.package_folder, "lib", common_lib_fullname))

        dll_pdbs = glob.glob(os.path.join(self.package_folder, "lib", "*.dll")) + \
                    glob.glob(os.path.join(self.package_folder, "lib", "*.pdb"))
        if dll_pdbs:
            tools.mkdir(os.path.join(self.package_folder, "bin"))
            for bin_file in dll_pdbs:
                rename(self, bin_file, os.path.join(self.package_folder, "bin", os.path.basename(bin_file)))

        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")

    def _create_emscripten_libs(self):
        # Boost Build doesn't create the libraries, but it gets close,
        # leaving .bc files where the libraries would be.
        staged_libs = os.path.join(
            self.package_folder, "lib"
        )
        if not os.path.exists(staged_libs):
            self.output.warn(f"Lib folder doesn't exist, can't collect libraries: {staged_libs}")
            return
        for bc_file in os.listdir(staged_libs):
            if bc_file.startswith("lib") and bc_file.endswith(".bc"):
                a_file = bc_file[:-3] + ".a"
                cmd = f"emar q {os.path.join(staged_libs, a_file)} {os.path.join(staged_libs, bc_file)}"
                self.output.info(cmd)
                self.run(cmd)

    @staticmethod
    def _option_to_conan_requirement(name):
        return {
            "lzma": "xz_utils",
            "iconv": "libiconv",
            "python": None,  # FIXME: change to cpython when it becomes available
        }.get(name, name)

    def package_info(self):
        self.env_info.BOOST_ROOT = self.package_folder

        self.cpp_info.set_property("cmake_file_name", "Boost")
        self.cpp_info.filenames["cmake_find_package"] = "Boost"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Boost"
        self.cpp_info.names["cmake_find_package"] = "Boost"
        self.cpp_info.names["cmake_find_package_multi"] = "Boost"

        # - Use 'headers' component for all includes + defines
        # - Use '_libboost' component to attach extra system_libs, ...

        self.cpp_info.components["headers"].libs = []
        self.cpp_info.components["headers"].set_property("cmake_target_name", "Boost::headers")
        self.cpp_info.components["headers"].names["cmake_find_package"] = "headers"
        self.cpp_info.components["headers"].names["cmake_find_package_multi"] = "headers"
        self.cpp_info.components["headers"].names["pkg_config"] = "boost"

        if self.options.system_no_deprecated:
            self.cpp_info.components["headers"].defines.append("BOOST_SYSTEM_NO_DEPRECATED")

        if self.options.asio_no_deprecated:
            self.cpp_info.components["headers"].defines.append("BOOST_ASIO_NO_DEPRECATED")

        if self.options.filesystem_no_deprecated:
            self.cpp_info.components["headers"].defines.append("BOOST_FILESYSTEM_NO_DEPRECATED")

        if self.options.filesystem_version:
            self.cpp_info.components["headers"].defines.append(f"BOOST_FILESYSTEM_VERSION={self.options.filesystem_version}")

        if self.options.segmented_stacks:
            self.cpp_info.components["headers"].defines.extend(["BOOST_USE_SEGMENTED_STACKS", "BOOST_USE_UCONTEXT"])

        if self.options.system_use_utf8:
            self.cpp_info.components["headers"].defines.append("BOOST_SYSTEM_USE_UTF8")

        if self.options.buildid:
            # If you built Boost using the --buildid option then set this macro to the same value
            # as you passed to bjam.
            # For example if you built using bjam address-model=64 --buildid=amd64 then compile your code with
            # -DBOOST_LIB_BUILDID=amd64 to ensure the correct libraries are selected at link time.
            self.cpp_info.components["headers"].defines.append(f"BOOST_LIB_BUILDID={self.options.buildid}")

        if not self.options.header_only:
            if self.options.error_code_header_only:
                self.cpp_info.components["headers"].defines.append("BOOST_ERROR_CODE_HEADER_ONLY")

        if self.options.layout == "versioned":
            version = Version(self.version)
            self.cpp_info.components["headers"].includedirs.append(os.path.join("include", f"boost-{version.major}_{version.minor}"))

        # Boost::boost is an alias of Boost::headers
        self.cpp_info.components["_boost_cmake"].requires = ["headers"]
        self.cpp_info.components["_boost_cmake"].set_property("cmake_target_name", "Boost::boost")
        self.cpp_info.components["_boost_cmake"].names["cmake_find_package"] = "boost"
        self.cpp_info.components["_boost_cmake"].names["cmake_find_package_multi"] = "boost"

        if not self.options.header_only:
            self.cpp_info.components["_libboost"].requires = ["headers"]

            self.cpp_info.components["diagnostic_definitions"].libs = []
            self.cpp_info.components["diagnostic_definitions"].set_property("cmake_target_name", "Boost::diagnostic_definitions")
            self.cpp_info.components["diagnostic_definitions"].names["cmake_find_package"] = "diagnostic_definitions"
            self.cpp_info.components["diagnostic_definitions"].names["cmake_find_package_multi"] = "diagnostic_definitions"
            self.cpp_info.components["diagnostic_definitions"].names["pkg_config"] = "boost_diagnostic_definitions"  # FIXME: disable on pkg_config
            # I would assume headers also need the define BOOST_LIB_DIAGNOSTIC, as a header can trigger an autolink,
            # and this definition triggers a print out of the library selected.  See notes below on autolink and headers.
            self.cpp_info.components["headers"].requires.append("diagnostic_definitions")
            if self.options.diagnostic_definitions:
                self.cpp_info.components["diagnostic_definitions"].defines = ["BOOST_LIB_DIAGNOSTIC"]

            self.cpp_info.components["disable_autolinking"].libs = []
            self.cpp_info.components["disable_autolinking"].set_property("cmake_target_name", "Boost::disable_autolinking")
            self.cpp_info.components["disable_autolinking"].names["cmake_find_package"] = "disable_autolinking"
            self.cpp_info.components["disable_autolinking"].names["cmake_find_package_multi"] = "disable_autolinking"
            self.cpp_info.components["disable_autolinking"].names["pkg_config"] = "boost_disable_autolinking"  # FIXME: disable on pkg_config

            # Even headers needs to know the flags for disabling autolinking ...
            # magic_autolink is an option in the recipe, so if a consumer wants this version of boost,
            # then they should not get autolinking.
            # Note that autolinking can sneak in just by some file #including a header with (eg) boost/atomic.hpp,
            # even if it doesn't use any part that requires linking with libboost_atomic in order to compile.
            # So a boost-header-only library that links to Boost::headers needs to see BOOST_ALL_NO_LIB
            # in order to avoid autolinking to libboost_atomic

            # This define is already imported into all of the _libboost libraries from this recipe anyway,
            # so it would be better to be consistent and ensure ANYTHING using boost (headers or libs) has consistent #defines.

            # Same applies for for BOOST_AUTO_LINK_{layout}:
            # consumer libs that use headers also need to know what is the layout/filename of the libraries.
            #
            # eg, if using the "tagged" naming scheme, and a header triggers an autolink,
            # then that header's autolink request had better be configured to request the "tagged" library name.
            # Otherwise, the linker will be looking for a (eg) "versioned" library name, and there will be a link error.

            # Note that "_libboost" requires "headers" so these defines will be applied to all the libraries too.
            self.cpp_info.components["headers"].requires.append("disable_autolinking")
            if self._is_msvc or self._is_clang_cl:
                if self.options.magic_autolink:
                    if self.options.layout == "system":
                        self.cpp_info.components["headers"].defines.append("BOOST_AUTO_LINK_SYSTEM")
                    elif self.options.layout == "tagged":
                        self.cpp_info.components["headers"].defines.append("BOOST_AUTO_LINK_TAGGED")
                    self.output.info("Enabled magic autolinking (smart and magic decisions)")
                else:
                    # DISABLES AUTO LINKING! NO SMART AND MAGIC DECISIONS THANKS!
                    self.cpp_info.components["disable_autolinking"].defines = ["BOOST_ALL_NO_LIB"]
                    self.output.info("Disabled magic autolinking (smart and magic decisions)")

            self.cpp_info.components["dynamic_linking"].libs = []
            self.cpp_info.components["dynamic_linking"].set_property("cmake_target_name", "Boost::dynamic_linking")
            self.cpp_info.components["dynamic_linking"].names["cmake_find_package"] = "dynamic_linking"
            self.cpp_info.components["dynamic_linking"].names["cmake_find_package_multi"] = "dynamic_linking"
            self.cpp_info.components["dynamic_linking"].names["pkg_config"] = "boost_dynamic_linking"  # FIXME: disable on pkg_config
            # A library that only links to Boost::headers can be linked into another library that links a Boost::library,
            # so for this reasons, the header-only library should know the BOOST_ALL_DYN_LINK definition as it will likely
            # change some important part of the boost code and cause linking errors downstream.
            # This is in the same theme as the notes above, re autolinking.
            self.cpp_info.components["headers"].requires.append("dynamic_linking")
            if self._shared:
                # A Boost::dynamic_linking cmake target does only make sense for a shared boost package
                self.cpp_info.components["dynamic_linking"].defines = ["BOOST_ALL_DYN_LINK"]

            # https://www.boost.org/doc/libs/1_73_0/more/getting_started/windows.html#library-naming
            # libsuffix for MSVC:
            # - system: ""
            # - versioned: "-vc142-mt-d-x64-1_74"
            # - tagged: "-mt-d-x64"
            libsuffix_lut = {
                "system": "",
                "versioned": "{toolset}{threading}{abi}{arch}{version}",
                "tagged": "{threading}{abi}{arch}",
            }
            libsuffix_data = {
                "toolset": f"-{self._toolset_tag}",
                "threading": "-mt" if self.options.multithreading else "",
                "abi": "",
                "ach": "",
                "version": "",
            }
            if self._is_msvc:  # FIXME: mingw?
                # FIXME: add 'y' when using cpython cci package and when python is built in debug mode
                static_runtime_key = "s" if "MT" in msvc_runtime_flag(self) else ""
                debug_runtime_key = "g" if "d" in msvc_runtime_flag(self) else ""
                debug_key = "d" if self.settings.build_type == "Debug" else ""
                abi = static_runtime_key + debug_runtime_key + debug_key
                if abi:
                    libsuffix_data["abi"] = f"-{abi}"
            else:
                debug_tag = "d" if self.settings.build_type == "Debug" else ""
                abi = debug_tag
                if abi:
                    libsuffix_data["abi"] = f"-{abi}"

            libsuffix_data["arch"] = f"-{self._b2_architecture[0]}{self._b2_address_model}"
            version = Version(self.version)
            if not version.patch or version.patch == "0":
                libsuffix_data["version"] = f"-{version.major}_{version.minor}"
            else:
                libsuffix_data["version"] = f"-{version.major}_{version.minor}_{version.patch}"
            libsuffix = libsuffix_lut[str(self.options.layout)].format(**libsuffix_data)
            if libsuffix:
                self.output.info(f"Library layout suffix: {repr(libsuffix)}")

            libformatdata = {}
            if not self.options.without_python:
                pyversion = Version(self._python_version)
                libformatdata["py_major"] = pyversion.major
                libformatdata["py_minor"] = pyversion.minor

            def add_libprefix(n):
                """ On MSVC, static libraries are built with a 'lib' prefix. Some libraries do not support shared, so are always built as a static library. """
                libprefix = ""
                if self._is_msvc and (not self._shared or n in self._dependencies["static_only"]):
                    libprefix = "lib"
                return libprefix + n

            all_detected_libraries = set(l[:-4] if l.endswith(".dll") else l for l in tools.collect_libs(self))
            all_expected_libraries = set()
            incomplete_components = []

            def filter_transform_module_libraries(names):
                libs = []
                for name in names:
                    if name in ("boost_stacktrace_windbg", "boost_stacktrace_windbg_cached") and self.settings.os != "Windows":
                        continue
                    if name in ("boost_stacktrace_addr2line", "boost_stacktrace_backtrace", "boost_stacktrace_basic",) and self.settings.os == "Windows":
                        continue
                    if name == "boost_stacktrace_addr2line" and not self._stacktrace_addr2line_available:
                        continue
                    if name == "boost_stacktrace_backtrace" and self.options.get_safe("with_stacktrace_backtrace") == False:
                        continue
                    if not self.options.get_safe("numa") and "_numa" in name:
                        continue
                    new_name = add_libprefix(name.format(**libformatdata)) + libsuffix
                    if self.options.namespace != 'boost':
                        new_name = new_name.replace("boost_", str(self.options.namespace) + "_")
                    if name.startswith("boost_python") or name.startswith("boost_numpy"):
                        if self.options.python_buildid:
                            new_name += f"-{self.options.python_buildid}"
                    if self.options.buildid:
                        new_name += f"-{self.options.buildid}"
                    libs.append(new_name)
                return libs

            for module in self._dependencies["dependencies"].keys():
                missing_depmodules = list(depmodule for depmodule in self._all_dependent_modules(module) if self.options.get_safe(f"without_{depmodule}", False))
                if missing_depmodules:
                    continue

                module_libraries = filter_transform_module_libraries(self._dependencies["libs"][module])

                # Don't create components for modules that should have libraries, but don't have (because of filter)
                if self._dependencies["libs"][module] and not module_libraries:
                    continue

                all_expected_libraries = all_expected_libraries.union(module_libraries)
                if set(module_libraries).difference(all_detected_libraries):
                    incomplete_components.append(module)

                # Starting v1.69.0 Boost.System is header-only. A stub library is
                # still built for compatibility, but linking to it is no longer
                # necessary.
                # https://www.boost.org/doc/libs/1_75_0/libs/system/doc/html/system.html#changes_in_boost_1_69
                if module == "system":
                    module_libraries = []

                self.cpp_info.components[module].libs = module_libraries

                self.cpp_info.components[module].requires = self._dependencies["dependencies"][module] + ["_libboost"]
                self.cpp_info.components[module].set_property("cmake_target_name", "Boost::" + module)
                self.cpp_info.components[module].names["cmake_find_package"] = module
                self.cpp_info.components[module].names["cmake_find_package_multi"] = module
                self.cpp_info.components[module].names["pkg_config"] = f"boost_{module}"

                for requirement in self._dependencies.get("requirements", {}).get(module, []):
                    if self.options.get_safe(requirement, None) == False:
                        continue
                    conan_requirement = self._option_to_conan_requirement(requirement)
                    if conan_requirement not in self.requires:
                        continue
                    if module == "locale" and requirement in ("icu", "iconv"):
                        if requirement == "icu" and not self._with_icu:
                            continue
                        if requirement == "iconv" and not self._with_iconv:
                            continue
                    self.cpp_info.components[module].requires.append(f"{conan_requirement}::{conan_requirement}")

            for incomplete_component in incomplete_components:
                self.output.warn(f"Boost component '{incomplete_component}' is missing libraries. Try building boost with '-o boost:without_{incomplete_component}'. (Option is not guaranteed to exist)")

            non_used = all_detected_libraries.difference(all_expected_libraries)
            if non_used:
                raise ConanException(f"These libraries were built, but were not used in any boost module: {non_used}")

            non_built = all_expected_libraries.difference(all_detected_libraries)
            if non_built:
                raise ConanException(f"These libraries were expected to be built, but were not built: {non_built}")

            if not self.options.without_stacktrace:
                if self.settings.os in ("Linux", "FreeBSD"):
                    self.cpp_info.components["stacktrace_basic"].system_libs.append("dl")
                    if self._stacktrace_addr2line_available:
                        self.cpp_info.components["stacktrace_addr2line"].system_libs.append("dl")
                    if self._with_stacktrace_backtrace:
                        self.cpp_info.components["stacktrace_backtrace"].system_libs.append("dl")

                if self._stacktrace_addr2line_available:
                    self.cpp_info.components["stacktrace_addr2line"].defines.extend([
                        f"BOOST_STACKTRACE_ADDR2LINE_LOCATION=\"{self.options.addr2line_location}\"",
                        "BOOST_STACKTRACE_USE_ADDR2LINE",
                    ])

                if self._with_stacktrace_backtrace:
                    self.cpp_info.components["stacktrace_backtrace"].defines.append("BOOST_STACKTRACE_USE_BACKTRACE")
                    self.cpp_info.components["stacktrace_backtrace"].requires.append("libbacktrace::libbacktrace")

                self.cpp_info.components["stacktrace_noop"].defines.append("BOOST_STACKTRACE_USE_NOOP")

                if self.settings.os == "Windows":
                    self.cpp_info.components["stacktrace_windbg"].defines.append("BOOST_STACKTRACE_USE_WINDBG")
                    self.cpp_info.components["stacktrace_windbg"].system_libs.extend(["ole32", "dbgeng"])
                    self.cpp_info.components["stacktrace_windbg_cached"].defines.append("BOOST_STACKTRACE_USE_WINDBG_CACHED")
                    self.cpp_info.components["stacktrace_windbg_cached"].system_libs.extend(["ole32", "dbgeng"])
                elif tools.is_apple_os(self.settings.os) or self.settings.os == "FreeBSD":
                    self.cpp_info.components["stacktrace"].defines.append("BOOST_STACKTRACE_GNU_SOURCE_NOT_REQUIRED")

            if not self.options.without_python:
                pyversion = Version(self._python_version)
                self.cpp_info.components[f"python{pyversion.major}{pyversion.minor}"].requires = ["python"]
                if not self._shared:
                    self.cpp_info.components["python"].defines.append("BOOST_PYTHON_STATIC_LIB")

                self.cpp_info.components[f"numpy{pyversion.major}{pyversion.minor}"].requires = ["numpy"]

            if self._is_msvc or self._is_clang_cl:
                # https://github.com/conan-community/conan-boost/issues/127#issuecomment-404750974
                self.cpp_info.components["_libboost"].system_libs.append("bcrypt")
            elif self.settings.os == "Linux":
                # https://github.com/conan-community/community/issues/135
                self.cpp_info.components["_libboost"].system_libs.append("rt")
                if self.options.multithreading:
                    self.cpp_info.components["_libboost"].system_libs.append("pthread")
            elif self.settings.os == "Emscripten":
                if self.options.multithreading:
                    arch = str(self.settings.arch)
                    # https://emscripten.org/docs/porting/pthreads.html
                    # The documentation mentions that we should be using the "-s USE_PTHREADS=1"
                    # but it was causing problems with the target based configurations in conan
                    # So instead we are using the raw compiler flags (that are being activated
                    # from the aforementioned flag)
                    if arch.startswith("x86") or arch.startswith("wasm"):
                        self.cpp_info.components["_libboost"].cxxflags.append("-pthread")
                        self.cpp_info.components["_libboost"].sharedlinkflags.extend(["-pthread","--shared-memory"])
                        self.cpp_info.components["_libboost"].exelinkflags.extend(["-pthread","--shared-memory"])
            elif self.settings.os == "iOS":
                if self.options.multithreading:
                    # https://github.com/conan-io/conan-center-index/issues/3867
                    # runtime crashes occur when using the default platform-specific reference counter/atomic
                    self.cpp_info.components["headers"].defines.extend(["BOOST_AC_USE_PTHREADS", "BOOST_SP_USE_PTHREADS"])
                else:
                    self.cpp_info.components["headers"].defines.extend(["BOOST_AC_DISABLE_THREADS", "BOOST_SP_DISABLE_THREADS"])
        self.user_info.stacktrace_addr2line_available = self._stacktrace_addr2line_available

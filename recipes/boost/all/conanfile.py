from conans import ConanFile
from conans import tools
from conans.tools import Version, cppstd_flag
from conans.errors import ConanException

from conans.errors import ConanInvalidConfiguration
import os
import sys
import shlex
import shutil
import yaml

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

required_conan_version = ">=1.28.0"


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
    "locale",
    "log",
    "math",
    "mpi",
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
    topics = ("conan", "boost", "libraries", "cpp")

    _options = None


    options = {
        "shared": [True, False],
        "header_only": [True, False],
        "error_code_header_only": [True, False],
        "system_no_deprecated": [True, False],
        "asio_no_deprecated": [True, False],
        "filesystem_no_deprecated": [True, False],
        "fPIC": [True, False],
        "layout": ["system", "versioned", "tagged", "b2-default"],
        "magic_autolink": [True, False],  # enables BOOST_ALL_NO_LIB
        "diagnostic_definitions": [True, False],  # enables BOOST_LIB_DIAGNOSTIC
        "python_executable": "ANY",  # system default python installation is used, if None
        "python_version": "ANY",  # major.minor; computed automatically, if None
        "namespace": "ANY",  # custom boost namespace for bcp, e.g. myboost
        "namespace_alias": [True, False],  # enable namespace alias for bcp, boost=myboost
        "multithreading": [True, False],  # enables multithreading support
        "zlib": [True, False],
        "bzip2": [True, False],
        "lzma": [True, False],
        "zstd": [True, False],
        "segmented_stacks": [True, False],
        "debug_level": [i for i in range(0, 14)],
        "pch": [True, False],
        "extra_b2_flags": "ANY",  # custom b2 flags
        "i18n_backend": ["iconv", "icu", None],
    }
    options.update({"without_{}".format(_name): [True, False] for _name in CONFIGURE_OPTIONS})

    default_options = {
        "shared": False,
        "header_only": False,
        "error_code_header_only": False,
        "system_no_deprecated": False,
        "asio_no_deprecated": False,
        "filesystem_no_deprecated": False,
        "fPIC": True,
        "layout": "system",
        "magic_autolink": False,
        "diagnostic_definitions": False,
        "python_executable": "None",
        "python_version": "None",
        "namespace": "boost",
        "namespace_alias": False,
        "multithreading": True,
        "zlib": True,
        "bzip2": True,
        "lzma": False,
        "zstd": False,
        "segmented_stacks": False,
        "debug_level": 0,
        "pch": True,
        "extra_b2_flags": "None",
        "i18n_backend": "iconv",
    }
    default_options.update({"without_{}".format(_name): False for _name in CONFIGURE_OPTIONS})
    default_options.update({"without_{}".format(_name): True for _name in ("graph_parallel", "mpi", "python")})

    short_paths = True
    no_copy_source = True
    exports_sources = ['patches/*']

    def export(self):
        self.copy(self._dependency_filename, src="dependencies", dst="dependencies")

    @property
    def _dependency_filename(self):
        return "dependencies-{}.yml".format(self.version)

    @property
    def _dependencies(self):
        dependencies_filepath = os.path.join(self.recipe_folder, "dependencies", self._dependency_filename)
        if not os.path.isfile(dependencies_filepath):
            raise ConanException("Cannot find {}".format(dependencies_filepath))
        return yaml.load(open(dependencies_filepath))

    def _iter_modules(self):
        tree = {k: v[:] for k, v in self._dependencies["dependencies"].items()}
        while tree:
            nodeps = set(k for k, v in tree.items() if not v)
            if not nodeps:
                raise ConanException("cyclic dependency tree detected")
            for nodep in nodeps:
                yield nodep
            tree = {k: [d for d in v if d not in nodeps] for k, v in tree.items() if k not in nodeps}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _bcp_dir(self):
        return "custom-boost"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

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
        return str(exe).replace('\\', '/')

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        # Test whether all config_options from the yml are available in CONFIGURE_OPTIONS
        for opt_name in self._configure_options:
            if "without_{}".format(opt_name) not in self.options:
                raise ConanException("{} has the configure options {} which is not available in conanfile.py".format(self._dependency_filename, opt_name))

        # Remove options not supported by this version of boost
        for dep_name in CONFIGURE_OPTIONS:
            if dep_name not in self._configure_options:
                delattr(self.options, "without_{}".format(dep_name))

    @property
    def _configure_options(self):
        return self._dependencies["configure_options"]

    def configure(self):
        if not self.options.i18n_backend and not self.options.without_locale:
            raise ConanInvalidConfiguration("Boost 'locale' library requires a i18n_backend, either 'icu' or 'iconv'")

        if not self.options.multithreading:
            # * For the reason 'thread' is deactivate look at https://stackoverflow.com/a/20991533
            #   Look also on the comments of the answer for more details
            # * Although the 'context' and 'atomic' library does not mention anything about threading,
            #   when being build the compiler uses the -pthread flag, which makes it quite dangerous
            for lib in ['locale', 'coroutine', 'wave', 'type_erasure', 'fiber', 'thread', 'context', 'atomic']:
                if not self.options.get_safe('without_%s' % lib):
                    raise ConanInvalidConfiguration("Boost '%s' library requires multi threading" % lib)

        if self.settings.compiler == "Visual Studio" and "MT" in str(self.settings.compiler.runtime) and self.options.shared:
            raise ConanInvalidConfiguration("Boost can not be built as shared library with MT runtime.")

        # Check, when a boost module is enabled, whether the boost modules it depends on are enabled as well.
        for mod_name, mod_deps in self._dependencies["dependencies"].items():
            if not self.options.get_safe("without_{}".format(mod_name), True):
                for mod_dep in mod_deps:
                    if self.options.get_safe("without_{}".format(mod_dep), False):
                        raise ConanInvalidConfiguration("{} requires {}: {} is disabled".format(mod_name, mod_deps, mod_dep))

        if not self.options.without_python:
            if not self.options.python_version:
                self.options.python_version = self._detect_python_version()
                self.options.python_executable = self._python_executable

    def build_requirements(self):
        if not self.options.header_only:
            self.build_requires("b2/4.2.0")

    def _with_dependency(self, dependency):
        """
        Return true when dependency is required according to the dependencies-x.y.z.yml file
        """
        for name, reqs in self._dependencies["requirements"].items():
            if dependency in reqs:
                if not self.options.get_safe("without_{}".format(name), True):
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
        return not self.options.header_only and self._with_dependency("icu") and self.options.i18n_backend == "icu"

    @property
    def _with_iconv(self):
        return not self.options.header_only and self._with_dependency("iconv") and self.options.i18n_backend == "iconv"

    def requirements(self):
        if self._with_zlib:
            self.requires("zlib/1.2.11")
        if self._with_bzip2:
            self.requires("bzip2/1.0.8")
        if self._with_lzma:
            self.requires("xz_utils/5.2.5")
        if self._with_zstd:
            self.requires("zstd/1.4.5")

        if self._with_icu:
            self.requires("icu/68.1")
        elif self._with_iconv:
            self.requires("libiconv/1.16")

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()
            self.info.options.header_only = True
        else:
            del self.info.options.debug_level
            del self.info.options.pch
            del self.info.options.python_executable  # PATH to the interpreter is not important, only version matters
            if self.options.without_python:
                del self.info.options.python_version
            else:
                self.info.options.python_version = self._python_version

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("boost_%s" % self.version.replace(".", "_"), self._source_subfolder)
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    ##################### BUILDING METHODS ###########################

    def _run_python_script(self, script):
        """
        execute python one-liner script and return its output
        :param script: string containing python script to be executed
        :return: output of the python script execution, or None, if script has failed
        """
        output = StringIO()
        command = '"%s" -c "%s"' % (self._python_executable, script)
        self.output.info('running %s' % command)
        try:
            self.run(command=command, output=output)
        except ConanException:
            self.output.info("(failed)")
            return None
        output = output.getvalue().strip()
        # Conan is broken when run_to_output = True
        if "\n-----------------\n" in output:
            output = output.split("\n-----------------\n", 1)[1]
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
                                       "print(sysconfig.get_path('%s'))" % name)

    def _get_python_sc_var(self, name):
        """
        obtain value of python sysconfig variable
        :param name: name of variable to be queried (such as LIBRARY or LDLIBRARY)
        :return: value of python sysconfig variable
        """
        return self._run_python_script("from __future__ import print_function; "
                                       "import sysconfig; "
                                       "print(sysconfig.get_config_var('%s'))" % name)

    def _get_python_du_var(self, name):
        """
        obtain value of python distutils sysconfig variable
        (sometimes sysconfig returns empty values, while python.sysconfig provides correct values)
        :param name: name of variable to be queried (such as LIBRARY or LDLIBRARY)
        :return: value of python sysconfig variable
        """
        return self._run_python_script("from __future__ import print_function; "
                                       "import distutils.sysconfig as du_sysconfig; "
                                       "print(du_sysconfig.get_config_var('%s'))" % name)

    def _get_python_var(self, name):
        """
        obtain value of python variable, either by sysconfig, or by distutils.sysconfig
        :param name: name of variable to be queried (such as LIBRARY or LDLIBRARY)
        :return: value of python sysconfig variable
        """
        return self._get_python_sc_var(name) or self._get_python_du_var(name)

    def _detect_python_version(self):
        """
        obtain version of python interpreter
        :return: python interpreter version, in format major.minor
        """
        return self._run_python_script("from __future__ import print_function; "
                                       "import sys; "
                                       "print('%s.%s' % (sys.version_info[0], sys.version_info[1]))")


    @property
    def _python_version(self):
        version = self._detect_python_version()
        if self.options.python_version and version != self.options.python_version:
            raise ConanInvalidConfiguration("detected python version %s doesn't match conan option %s" % (version,
                                                                                          self.options.python_version))
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
        include = self._get_python_path('include')
        plat_include = self._get_python_path('platinclude')
        include_py = self._get_python_var('INCLUDEPY')
        include_dir = self._get_python_var('INCLUDEDIR')
        python_inc = self._python_inc

        candidates = [include,
                      plat_include,
                      include_py,
                      include_dir,
                      python_inc]
        for candidate in candidates:
            if candidate:
                python_h = os.path.join(candidate, 'Python.h')
                self.output.info('checking %s' % python_h)
                if os.path.isfile(python_h):
                    self.output.info('found Python.h: %s' % python_h)
                    return candidate.replace('\\', '/')
        raise Exception("couldn't locate Python.h - make sure you have installed python development files")

    @property
    def _python_libraries(self):
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
                    candidates.append("%spython%s%s%s" % (prefix, version, abiflags, suffix))

        for candidate in candidates:
            if candidate:
                python_lib = os.path.join(libdir, candidate)
                self.output.info('checking %s' % python_lib)
                if os.path.isfile(python_lib):
                    self.output.info('found python library: %s' % python_lib)
                    return python_lib.replace('\\', '/')
        raise ConanInvalidConfiguration("couldn't locate python libraries - make sure you have installed python development files")

    def _clean(self):
        src = os.path.join(self.source_folder, self._source_subfolder)
        clean_dirs = [os.path.join(self.build_folder, "bin.v2"),
                      os.path.join(self.build_folder, "architecture"),
                      os.path.join(self.source_folder, self._bcp_dir),
                      os.path.join(src, "dist", "bin"),
                      os.path.join(src, "stage"),
                      os.path.join(src, "tools", "build", "src", "engine", "bootstrap"),
                      os.path.join(src, "tools", "build", "src", "engine", "bin.ntx86"),
                      os.path.join(src, "tools", "build", "src", "engine", "bin.ntx86_64")]
        for d in clean_dirs:
            if os.path.isdir(d):
                self.output.warn('removing "%s"' % d)
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
        folder = os.path.join(self.source_folder, self._source_subfolder, 'tools', 'bcp')
        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            with tools.chdir(folder):
                command = "%s -j%s --abbreviate-paths toolset=%s" % (self._b2_exe, tools.cpu_count(), self._toolset)
                if self.options.debug_level:
                    command += " -d%d" % self.options.debug_level
                self.output.warn(command)
                self.run(command, run_environment=True)

    def _run_bcp(self):
        with tools.vcvars(self.settings) if self._is_msvc or self._is_clang_cl else tools.no_op():
            with tools.chdir(self.source_folder):
                os.mkdir(self._bcp_dir)
                namespace = "--namespace=%s" % self.options.namespace
                alias = "--namespace-alias" if self.options.namespace_alias else ""
                boostdir = "--boost=%s" % self._source_subfolder
                libraries = {"build", "boost-build.jam", "boostcpp.jam", "boost_install", "headers"}
                for d in os.listdir(os.path.join(self._source_subfolder, "boost")):
                    if os.path.isdir(os.path.join(self._source_subfolder, "boost", d)):
                        libraries.add(d)
                for d in os.listdir(os.path.join(self._source_subfolder, "libs")):
                    if os.path.isdir(os.path.join(self._source_subfolder, "libs", d)):
                        libraries.add(d)
                libraries = ' '.join(libraries)
                command = "{bcp} {namespace} {alias} " \
                          "{boostdir} {libraries} {outdir}".format(bcp=self._bcp_exe,
                                                                   namespace=namespace,
                                                                   alias=alias,
                                                                   libraries=libraries,
                                                                   boostdir=boostdir,
                                                                   outdir=self._bcp_dir)
                self.output.warn(command)
                self.run(command)

    def build(self):
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
        full_command = "%s %s" % (self._b2_exe, b2_flags)
        # -d2 is to print more debug info and avoid travis timing out without output
        sources = os.path.join(self.source_folder, self._boost_dir)
        full_command += ' --debug-configuration --build-dir="%s"' % self.build_folder
        self.output.warn(full_command)

        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            with tools.chdir(sources):
                # To show the libraries *1
                # self.run("%s --show-libraries" % b2_exe)
                self.run(full_command, run_environment=True)

    @property
    def _b2_os(self):
        return {"Windows": "windows",
                "WindowsStore": "windows",
                "Linux": "linux",
                "Android": "android",
                "Macos": "darwin",
                "iOS": "iphone",
                "watchOS": "iphone",
                "tvOS": "appletv",
                "FreeBSD": "freebsd",
                "SunOS": "solaris"}.get(str(self.settings.os))

    @property
    def _b2_address_model(self):
        if str(self.settings.arch) in ["x86_64", "ppc64", "ppc64le", "mips64", "armv8", "sparcv9"]:
            return "64"
        else:
            return "32"

    @property
    def _b2_binary_format(self):
        return {"Windows": "pe",
                "WindowsStore": "pe",
                "Linux": "elf",
                "Android": "elf",
                "Macos": "mach-o",
                "iOS": "mach-o",
                "watchOS": "mach-o",
                "tvOS": "mach-o",
                "FreeBSD": "elf",
                "SunOS": "elf"}.get(str(self.settings.os))

    @property
    def _b2_architecture(self):
        if str(self.settings.arch).startswith('x86'):
            return 'x86'
        elif str(self.settings.arch).startswith('ppc'):
            return 'power'
        elif str(self.settings.arch).startswith('arm'):
            return 'arm'
        elif str(self.settings.arch).startswith('sparc'):
            return 'sparc'
        elif str(self.settings.arch).startswith('mips64'):
            return 'mips64'
        elif str(self.settings.arch).startswith('mips'):
            return 'mips1'
        else:
            return None

    @property
    def _b2_abi(self):
        if str(self.settings.arch).startswith('x86'):
            return "ms" if str(self.settings.os) in ["Windows", "WindowsStore"] else "sysv"
        elif str(self.settings.arch).startswith('ppc'):
            return "sysv"
        elif str(self.settings.arch).startswith('arm'):
            return "aapcs"
        elif str(self.settings.arch).startswith('mips'):
            return "o32"
        else:
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
            elif str(self.settings.compiler.libcxx) == "libstdc++11":
                return "1"
        except:
            pass
        return None

    @property
    def _build_flags(self):
        flags = self._build_cross_flags

        # https://www.boost.org/doc/libs/1_70_0/libs/context/doc/html/context/architectures.html
        if self._b2_os:
            flags.append("target-os=%s" % self._b2_os)
        if self._b2_architecture:
            flags.append("architecture=%s" % self._b2_architecture)
        if self._b2_address_model:
            flags.append("address-model=%s" % self._b2_address_model)
        if self._b2_binary_format:
            flags.append("binary-format=%s" % self._b2_binary_format)
        if self._b2_abi:
            flags.append("abi=%s" % self._b2_abi)

        if self.options.layout is not "b2-default":
            flags.append("--layout=%s" % self.options.layout)
        flags.append("--user-config=%s" % os.path.join(self._boost_build_dir, 'user-config.jam'))
        flags.append("-sNO_ZLIB=%s" % ("0" if self._with_zlib else "1"))
        flags.append("-sNO_BZIP2=%s" % ("0" if self._with_bzip2 else "1"))
        flags.append("-sNO_LZMA=%s" % ("0" if self._with_lzma else "1"))
        flags.append("-sNO_ZSTD=%s" % ("0" if self._with_zstd else "1"))

        if self.options.i18n_backend == 'icu':
            flags.append("-sICU_PATH={}".format(self.deps_cpp_info["icu"].rootpath))
            flags.append("boost.locale.iconv=off boost.locale.icu=on")
        elif self.options.i18n_backend == 'iconv':
            flags.append("boost.locale.iconv=on boost.locale.icu=off")
        else:
            flags.append("boost.locale.iconv=off boost.locale.icu=off")
            flags.append("--disable-icu --disable-iconv")

        def add_defines(library):
            for define in self.deps_cpp_info[library].defines:
                flags.append("define=%s" % define)

        if self._with_zlib:
            add_defines("zlib")
        if self._with_bzip2:
            add_defines("bzip2")
        if self._with_lzma:
            add_defines("xz_utils")
        if self._with_zstd:
            add_defines("zstd")

        if self._is_msvc:
            flags.append("runtime-link=%s" % ("static" if "MT" in str(self.settings.compiler.runtime) else "shared"))
            flags.append("runtime-debugging=%s" % ("on" if "d" in str(self.settings.compiler.runtime) else "off"))

        # For details https://boostorg.github.io/build/manual/master/index.html
        flags.append("threading=%s" % ("single" if not self.options.multithreading else "multi" ))

        flags.append("link=%s" % ("static" if not self.options.shared else "shared"))
        if self.settings.build_type == "Debug":
            flags.append("variant=debug")
        else:
            flags.append("variant=release")

        for libname in self._configure_options:
            if getattr(self.options, "without_%s" % libname):
                flags.append("--without-%s" % libname)

        flags.append("toolset=%s" % self._toolset)

        if self.settings.get_safe("compiler.cppstd"):
            flags.append("cxxflags=%s" % cppstd_flag(self.settings))

        # CXX FLAGS
        cxx_flags = []
        # fPIC DEFINITION
        if self.settings.os != "Windows":
            if self.options.fPIC:
                cxx_flags.append("-fPIC")
        if self.settings.build_type == "RelWithDebInfo":
            if self.settings.compiler == "gcc" or "clang" in str(self.settings.compiler):
                cxx_flags.append("-g")
            elif self.settings.compiler == "Visual Studio":
                cxx_flags.append("/Z7")

        # Standalone toolchain fails when declare the std lib
        if self.settings.os != "Android" and self.settings.os != "Emscripten":
            try:
                if self._gnu_cxx11_abi:
                    flags.append("define=_GLIBCXX_USE_CXX11_ABI=%s" % self._gnu_cxx11_abi)

                if "clang" in str(self.settings.compiler):
                    if str(self.settings.compiler.libcxx) == "libc++":
                        cxx_flags.append("-stdlib=libc++")
                        flags.append('linkflags="-stdlib=libc++"')
                    else:
                        cxx_flags.append("-stdlib=libstdc++")
            except:
                pass

        if self.options.error_code_header_only:
            flags.append("define=BOOST_ERROR_CODE_HEADER_ONLY=1")
        if self.options.system_no_deprecated:
            flags.append("define=BOOST_SYSTEM_NO_DEPRECATED=1")
        if self.options.asio_no_deprecated:
            flags.append("define=BOOST_ASIO_NO_DEPRECATED=1")
        if self.options.filesystem_no_deprecated:
            flags.append("define=BOOST_FILESYSTEM_NO_DEPRECATED=1")
        if self.options.segmented_stacks:
            flags.extend(["segmented-stacks=on",
                          "define=BOOST_USE_SEGMENTED_STACKS=1",
                          "define=BOOST_USE_UCONTEXT=1"])
        flags.append("pch=on" if self.options.pch else "pch=off")

        if tools.is_apple_os(self.settings.os):
            if self.settings.get_safe("os.version"):
                cxx_flags.append(tools.apple_deployment_target_flag(self.settings.os,
                                                                    self.settings.os.version))

        if self.settings.os == "iOS":
            if self.options.multithreading:
                cxx_flags.append("-DBOOST_AC_USE_PTHREADS")
                cxx_flags.append("-DBOOST_SP_USE_PTHREADS")

            cxx_flags.append("-fvisibility=hidden")
            cxx_flags.append("-fvisibility-inlines-hidden")
            cxx_flags.append("-fembed-bitcode")

        cxx_flags = 'cxxflags="%s"' % " ".join(cxx_flags) if cxx_flags else ""
        flags.append(cxx_flags)

        if self.options.extra_b2_flags:
            flags.extend(shlex.split(str(self.options.extra_b2_flags)))

        flags.extend(["install",
                      "--prefix=%s" % self.package_folder,
                      "-j%s" % tools.cpu_count(),
                      "--abbreviate-paths"])
        if self.options.debug_level:
            flags.append("-d%d" % self.options.debug_level)
        return flags

    @property
    def _build_cross_flags(self):
        flags = []
        if not tools.cross_building(self.settings):
            return flags
        arch = self.settings.get_safe('arch')
        self.output.info("Cross building, detecting compiler...")

        if arch.startswith('arm'):
            if 'hf' in arch:
                flags.append('-mfloat-abi=hard')
        elif self.settings.os == "Emscripten":
            pass
        elif arch in ["x86", "x86_64"]:
            pass
        elif arch.startswith("ppc"):
            pass
        elif arch.startswith("mips"):
            pass
        else:
            self.output.warn("Unable to detect the appropriate ABI for %s architecture." % arch)
        self.output.info("Cross building flags: %s" % flags)

        return flags

    @property
    def _ar(self):
        if "AR" in os.environ:
            return os.environ["AR"]
        if tools.is_apple_os(self.settings.os) and self.settings.compiler == "apple-clang":
            return tools.XCRun(self.settings).ar
        return None

    @property
    def _ranlib(self):
        if "RANLIB" in os.environ:
            return os.environ["RANLIB"]
        if tools.is_apple_os(self.settings.os) and self.settings.compiler == "apple-clang":
            return tools.XCRun(self.settings).ranlib
        return None

    @property
    def _cxx(self):
        if "CXX" in os.environ:
            return os.environ["CXX"]
        if tools.is_apple_os(self.settings.os) and self.settings.compiler == "apple-clang":
            return tools.XCRun(self.settings).cxx
        compiler_version = str(self.settings.compiler.version)
        major = compiler_version.split(".")[0]
        if self.settings.compiler == "gcc":
            return tools.which("g++-%s" % compiler_version) or tools.which("g++-%s" % major) or tools.which("g++") or ""
        if self.settings.compiler == "clang":
            return tools.which("clang++-%s" % compiler_version) or tools.which("clang++-%s" % major) or tools.which("clang++") or ""
        return ""

    def _create_user_config_jam(self, folder):
        """To help locating the zlib and bzip2 deps"""
        self.output.warn("Patching user-config.jam")

        contents = ""
        if self._zip_bzip2_requires_needed:
            def create_library_config(deps_name, name):
                includedir = '"%s"' % self.deps_cpp_info[deps_name].include_paths[0].replace('\\', '/')
                libdir = '"%s"' % self.deps_cpp_info[deps_name].lib_paths[0].replace('\\', '/')
                lib = self.deps_cpp_info[deps_name].libs[0]
                version = self.deps_cpp_info[deps_name].version
                return "\nusing {name} : {version} : " \
                       "<include>{includedir} " \
                       "<search>{libdir} " \
                       "<name>{lib} ;".format(name=name,
                                              version=version,
                                              includedir=includedir,
                                              libdir=libdir,
                                              lib=lib)

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
            contents += '\nusing python : {version} : "{executable}" : "{includes}" : "{libraries}" ;'\
                .format(version=self._python_version,
                        executable=self._python_executable,
                        includes=self._python_includes,
                        libraries=self._python_libraries)

        # Specify here the toolset with the binary if present if don't empty parameter :
        contents += '\nusing "%s" : %s : ' % (self._toolset, self._toolset_version)
        contents += ' "%s"' % self._cxx.replace("\\", "/")

        if tools.is_apple_os(self.settings.os):
            if self.settings.compiler == "apple-clang":
                contents += " -isysroot %s" % tools.XCRun(self.settings).sdk_path
            if self.settings.get_safe("arch"):
                contents += " -arch %s" % tools.to_apple_arch(self.settings.arch)

        contents += " : \n"
        if self._ar:
            contents += '<archiver>"%s" ' % tools.which(self._ar).replace("\\", "/")
        if self._ranlib:
            contents += '<ranlib>"%s" ' % tools.which(self._ranlib).replace("\\", "/")
        if "CXXFLAGS" in os.environ:
            contents += '<cxxflags>"%s" ' % os.environ["CXXFLAGS"]
        if "CFLAGS" in os.environ:
            contents += '<cflags>"%s" ' % os.environ["CFLAGS"]
        if "LDFLAGS" in os.environ:
            contents += '<linkflags>"%s" ' % os.environ["LDFLAGS"]
        if "ASFLAGS" in os.environ:
            contents += '<asmflags>"%s" ' % os.environ["ASFLAGS"]

        contents += " ;"

        self.output.warn(contents)
        filename = "%s/user-config.jam" % folder
        tools.save(filename,  contents)

    @property
    def _toolset_version(self):
        if self._is_msvc:
            compiler_version = str(self.settings.compiler.version)
            if Version(compiler_version) >= "16":
                return "14.2"
            elif Version(compiler_version) >= "15":
                return "14.1"
            else:
                return "%s.0" % compiler_version
        return ""

    @property
    def _toolset(self):
        if self._is_msvc:
            return "msvc"
        elif self.settings.os == "Windows" and self.settings.compiler == "clang":
            return "clang-win"
        elif self.settings.os == "Emscripten" and self.settings.compiler == "clang":
            return "emscripten"
        elif self.settings.compiler == "gcc" and tools.is_apple_os(self.settings.os):
            return "darwin"
        elif self.settings.compiler == "apple-clang":
            return "clang-darwin"
        elif self.settings.os == "Android" and self.settings.compiler == "clang":
            return "clang-linux"
        elif self.settings.compiler in ["clang", "gcc"]:
            return str(self.settings.compiler)
        elif self.settings.compiler == "sun-cc":
            return "sunpro"
        elif self.settings.compiler == "intel":
            return {
                "Macos": "intel-darwin",
                "Windows": "intel-win",
                "Linux": "intel-linux",
            }[str(self.settings.os)]
        else:
            return str(self.settings.compiler)

    @property
    def _toolset_tag(self):
        if self._is_msvc:
            return "vc{}".format(self._toolset_version.replace(".",""))
        else:
            # FIXME: missing toolset tags for compilers (see self._toolset)
            compiler = str(self.settings.compiler)
            if self.settings.compiler == "apple-clang":
                compiler = "darwin"
            return "{}{}".format(compiler, self.settings.compiler.version)

    ####################################################################

    def package(self):
        # This stage/lib is in source_folder... Face palm, looks like it builds in build but then
        # copy to source with the good lib name
        self.copy("LICENSE_1_0.txt", dst="licenses", src=os.path.join(self.source_folder,
                                                                      self._source_subfolder))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        if self.options.header_only:
            self.copy(pattern="*", dst="include/boost", src="%s/boost" % self._boost_dir)

        if self.settings.os == "Emscripten":
            self._create_emscripten_libs()

        if self._is_msvc and self.options.shared:
            # Some boost releases contain both static and shared variants of some libraries (if shared=True)
            all_libs = set(tools.collect_libs(self, "lib"))
            static_libs = set(l for l in all_libs if l.startswith("lib"))
            shared_libs = all_libs.difference(static_libs)
            static_libs = set(l[3:] for l in static_libs)
            common_libs = static_libs.intersection(shared_libs)
            for common_lib in common_libs:
                self.output.info("Unlinking static duplicate library: {}".format(os.path.join(self.package_folder, "lib", "lib{}.lib".format(common_lib))))
                os.unlink(os.path.join(self.package_folder, "lib", "lib{}.lib".format(common_lib)))

    def _create_emscripten_libs(self):
        # Boost Build doesn't create the libraries, but it gets close,
        # leaving .bc files where the libraries would be.
        staged_libs = os.path.join(
            self.package_folder, "lib"
        )
        for bc_file in os.listdir(staged_libs):
            if bc_file.startswith("lib") and bc_file.endswith(".bc"):
                a_file = bc_file[:-3] + ".a"
                cmd = "emar q {dst} {src}".format(
                    dst=os.path.join(staged_libs, a_file),
                    src=os.path.join(staged_libs, bc_file),
                )
                self.output.info(cmd)
                self.run(cmd)

    @property
    def _is_versioned_layout(self):
        layout = self.options.get_safe("layout")
        return layout == "versioned" or (layout == "b2-default" and os.name == 'nt')

    @staticmethod
    def _option_to_conan_requirement(name):
        return {
            "lzma": "xz_utils",
            "iconv": "libiconv",
            "python": None,  # FIXME: change to cpython when it becomes available
        }.get(name, name)

    def package_info(self):
        self.env_info.BOOST_ROOT = self.package_folder

        self.cpp_info.filenames["cmake_find_package"] = "Boost"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Boost"
        self.cpp_info.names["cmake_find_package"] = "Boost"
        self.cpp_info.names["cmake_find_package_multi"] = "Boost"

        # - Use 'headers' component for all includes + defines
        # - Use '_libboost' component to attach extra system_libs, ...

        self.cpp_info.components["headers"].libs = []
        self.cpp_info.components["headers"].names["cmake_find_package"] = "headers"
        self.cpp_info.components["headers"].names["cmake_find_package_multi"] = "headers"

        if self.options.system_no_deprecated:
            self.cpp_info.components["headers"].defines.append("BOOST_SYSTEM_NO_DEPRECATED")

        if self.options.asio_no_deprecated:
            self.cpp_info.components["headers"].defines.append("BOOST_ASIO_NO_DEPRECATED")

        if self.options.filesystem_no_deprecated:
            self.cpp_info.components["headers"].append("BOOST_FILESYSTEM_NO_DEPRECATED")

        if self.options.segmented_stacks:
            self.cpp_info.components["headers"].extend(["BOOST_USE_SEGMENTED_STACKS", "BOOST_USE_UCONTEXT"])

        if not self.options.header_only:
            if self.options.error_code_header_only:
                self.cpp_info.components["headers"].defines.append("BOOST_ERROR_CODE_HEADER_ONLY")

        if self._is_versioned_layout:
            version = tools.Version(self.version)
            self.cpp_info.components["headers"].includedirs.append(os.path.join("include", "boost-{}_{}".format(version.major, version.minor)))

        # Boost::boost is an alias of Boost::headers
        self.cpp_info.components["_boost_cmake"].requires = ["headers"]
        self.cpp_info.components["_boost_cmake"].names["cmake_find_package"] = "boost"
        self.cpp_info.components["_boost_cmake"].names["cmake_find_package_multi"] = "boost"

        if not self.options.header_only:
            self.cpp_info.components["_libboost"].requires = ["headers"]
            self.cpp_info.components["_libboost"].bindirs.append("lib")

            self.cpp_info.components["diagnostic_definitions"].libs = []
            self.cpp_info.components["diagnostic_definitions"].names["cmake_find_package"] = "diagnostic_definitions"
            self.cpp_info.components["diagnostic_definitions"].names["cmake_find_package_multi"] = "diagnostic_definitions"
            self.cpp_info.components["_libboost"].requires.append("diagnostic_definitions")
            if self.options.diagnostic_definitions:
                self.cpp_info.components["diagnostic_definitions"].defines = ["BOOST_LIB_DIAGNOSTIC"]

            self.cpp_info.components["disable_autolinking"].libs = []
            self.cpp_info.components["disable_autolinking"].names["cmake_find_package"] = "disable_autolinking"
            self.cpp_info.components["disable_autolinking"].names["cmake_find_package_multi"] = "disable_autolinking"
            self.cpp_info.components["_libboost"].requires.append("disable_autolinking")
            if self._is_msvc or self._is_clang_cl:
                if self.options.magic_autolink:
                    if self.options.layout == "system":
                        self.cpp_info.components["_libboost"].defines.append("BOOST_AUTO_LINK_SYSTEM")
                    elif self.options.layout == "tagged":
                        self.cpp_info.components["_libboost"].defines.append("BOOST_AUTO_LINK_TAGGED")
                    self.output.info("Enabled magic autolinking (smart and magic decisions)")
                else:
                    # DISABLES AUTO LINKING! NO SMART AND MAGIC DECISIONS THANKS!
                    self.cpp_info.components["disable_autolinking"].defines = ["BOOST_ALL_NO_LIB"]
                    self.output.info("Disabled magic autolinking (smart and magic decisions)")

            self.cpp_info.components["dynamic_linking"].libs = []
            self.cpp_info.components["dynamic_linking"].names["cmake_find_package"] = "dynamic_linking"
            self.cpp_info.components["dynamic_linking"].names["cmake_find_package_multi"] = "dynamic_linking"
            self.cpp_info.components["_libboost"].requires.append("dynamic_linking")
            if self.options.shared:
                # A Boost::dynamic_linking cmake target does only make sense for a shared boost package
                self.cpp_info.components["dynamic_linking"].defines = ["BOOST_ALL_DYN_LINK"]

            libsuffix = ""
            if self._is_versioned_layout:
                # https://www.boost.org/doc/libs/1_73_0/more/getting_started/windows.html#library-naming
                toolset_tag = "-{}".format(self._toolset_tag)
                threading_tag = "-mt" if self.options.multithreading else ""
                abi_tag = ""
                if self._is_msvc:
                    # FIXME: add 'y' when using cpython cci package and when python is built in debug mode
                    static_runtime_key = "s" if "MT" in str(self.settings.compiler.runtime) else ""
                    debug_runtime_key = "g" if "d" in str(self.settings.compiler.runtime) else ""
                    debug_key = "d" if self.settings.build_type == "Debug" else ""
                    abi = static_runtime_key + debug_runtime_key + debug_key
                    if abi:
                        abi_tag = "-{}".format(abi)
                else:
                    debug_tag = "d" if self.settings.build_type == "Debug" else ""
                    abi = debug_tag
                    if abi:
                        abi_tag = "-{}".format(abi)

                arch_tag = "-{}{}".format(self._b2_architecture[0], self._b2_address_model)
                version = tools.Version(self.version)
                if not version.patch or version.patch == "0":
                    version_tag = "-{}_{}".format(version.major, version.minor)
                else:
                    version_tag = "-{}_{}_{}".format(version.major, version.minor, version.patch)
                libsuffix = toolset_tag + threading_tag + abi_tag + arch_tag + version_tag
                self.output.info("Versioning library suffix: {}".format(libsuffix))

            libformatdata = {}
            if not self.options.without_python:
                pyversion = tools.Version(self._python_version)
                libformatdata["py_major"] = pyversion.major
                libformatdata["py_minor"] = pyversion.minor

            def add_libprefix(n):
                """ On MSVC, static libraries are built with a 'lib' prefix. Some libraries do not support shared, so are always built as a static library. """
                libprefix = ""
                if self.settings.compiler == "Visual Studio" and (not self.options.shared or n in self._dependencies["static_only"]):
                    libprefix = "lib"
                return libprefix + n

            modules_seen = set()
            detected_libraries = set(tools.collect_libs(self))
            used_libraries = set()
            for module in self._iter_modules():
                if self.options.get_safe("without_{}".format(module), False) or not all(d in modules_seen for d in self._dependencies["dependencies"][module]):
                    continue

                module_libraries = [add_libprefix(lib.format(**libformatdata)) + libsuffix for lib in self._dependencies["libs"][module]]
                if all(l in detected_libraries for l in module_libraries):
                    modules_seen.add(module)
                    used_libraries = used_libraries.union(module_libraries)
                    self.cpp_info.components[module].libs = module_libraries

                    self.cpp_info.components[module].requires = self._dependencies["dependencies"][module] + ["_libboost"]
                    self.cpp_info.components[module].names["cmake_find_package"] = module
                    self.cpp_info.components[module].names["cmake_find_package_multi"] = module

                    for requirement in self._dependencies.get("requirements", {}).get(module, []):
                        if requirement == "backtrace":
                            # FIXME: backtrace not (yet) available in cci
                            continue
                        if self.options.get_safe(requirement, None) == False:
                            continue
                        conan_requirement = self._option_to_conan_requirement(requirement)
                        if not conan_requirement:
                            continue
                        if conan_requirement in ("icu", "iconv"):
                            if conan_requirement != self.options.get_safe("i18n_backend"):
                                continue
                        self.cpp_info.components[module].requires.append("{0}::{0}".format(conan_requirement))

            if used_libraries != detected_libraries:
                non_used = detected_libraries.difference(used_libraries)
                assert len(non_used) == 0, "These libraries were not used in conan components: {}".format(non_used)

                non_existing = used_libraries.difference(detected_libraries)
                assert len(non_existing) == 0, "These libraries were used, but not built: {}".format(non_existing)

            if not self.options.without_python:
                pyversion = tools.Version(self._python_version)
                self.cpp_info.components["python{}{}".format(pyversion.major, pyversion.minor)].requires = ["python"]
                if not self.options.shared:
                    self.cpp_info.components["python"].defines.append("BOOST_PYTHON_STATIC_LIB")

                self.cpp_info.components["numpy{}{}".format(pyversion.major, pyversion.minor)].requires = ["numpy"]

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

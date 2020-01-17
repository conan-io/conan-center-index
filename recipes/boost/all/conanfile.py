from conans import ConanFile
from conans import tools
from conans.client.build.cppstd_flags import cppstd_flag
from conans.tools import Version
from conans.errors import ConanException

from conans.errors import ConanInvalidConfiguration
import os
import sys

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

# From from *1 (see below, b2 --show-libraries), also ordered following linkage order
# see https://github.com/Kitware/CMake/blob/master/Modules/FindBoost.cmake to know the order

lib_list = ['math', 'wave', 'container', 'contract', 'exception', 'graph', 'iostreams', 'locale', 'log',
            'program_options', 'random', 'regex', 'mpi', 'serialization',
            'coroutine', 'fiber', 'context', 'timer', 'thread', 'chrono', 'date_time',
            'atomic', 'filesystem', 'system', 'graph_parallel', 'python',
            'stacktrace', 'test', 'type_erasure']


class BoostConan(ConanFile):
    name = "boost"
    settings = "os", "arch", "compiler", "build_type"
    description = "Boost provides free peer-reviewed portable C++ source libraries"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.boost.org"
    license = "BSL-1.0"
    topics = ("conan", "boost", "libraries", "cpp")
    # The current python option requires the package to be built locally, to find default Python
    # implementation
    options = {
        "shared": [True, False],
        "header_only": [True, False],
        "error_code_header_only": [True, False],
        "system_no_deprecated": [True, False],
        "asio_no_deprecated": [True, False],
        "filesystem_no_deprecated": [True, False],
        "fPIC": [True, False],
        "layout": ["system", "versioned", "tagged"],
        "magic_autolink": [True, False],  # enables BOOST_ALL_NO_LIB
        "python_executable": "ANY",  # system default python installation is used, if None
        "python_version": "ANY",  # major.minor; computed automatically, if None
        "zlib": [True, False],
        "bzip2": [True, False],
        "lzma": [True, False],
        "zstd": [True, False],
        "segmented_stacks": [True, False],
        "extra_b2_flags": "ANY"  # custom b2 flags
    }
    options.update({"without_%s" % libname: [True, False] for libname in lib_list})

    default_options = {
        'shared': False,
        'header_only': False,
        'error_code_header_only': False,
        'system_no_deprecated': False,
        'asio_no_deprecated': False,
        'filesystem_no_deprecated': False,
        'fPIC': True,
        'layout': 'system',
        'magic_autolink': False,
        'python_executable': 'None',
        'python_version': 'None',        
        'zlib': True,
        'bzip2': True,
        'lzma': False,
        'zstd': False,
        'segmented_stacks': False,
        'extra_b2_flags': 'None',
    }

    for libname in lib_list:
        if libname != "python":
            default_options.update({"without_%s" % libname: False})
    default_options.update({"without_python": True})
    short_paths = True
    no_copy_source = True
    exports_sources = ['patches/*']

    @property
    def _folder_name(self):
        return "boost_%s" % self.version.replace(".", "_")

    @property
    def _boost_dist_root(self):
        """Folder where the boost package is extracted"""
        return os.path.join(self.source_folder, self._folder_name)

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

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

    def requirements(self):
        if self._zip_bzip2_requires_needed:
            if self.options.zlib:
                self.requires("zlib/1.2.11")
            if self.options.bzip2:
                self.requires("bzip2/1.0.8")
            if self.options.lzma:
                self.requires("xz_utils/5.2.4")
            if self.options.zstd:
                self.requires("zstd/1.4.3")

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()
            self.info.options.header_only = True
        else:
            del self.info.options.python_executable  # PATH to the interpreter is not important, only version matters
            if self.options.without_python:
                del self.info.options.python_version
            else:
                self.info.options.python_version = self._python_version

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        for patch in self.conan_data["patches"][self.version]:
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
        self.output.info(output)
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

    @property
    def _python_version(self):
        """
        obtain version of python interpreter
        :return: python interpreter version, in format major.minor
        """
        version = self._run_python_script("from __future__ import print_function; "
                                          "import sys; "
                                          "print('%s.%s' % (sys.version_info[0], sys.version_info[1]))")
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

    @property
    def _b2_exe(self):
        return os.path.join(self.build_folder, "b2.exe" if tools.os_info.is_windows else "b2")

    def build(self):
        if self.options.header_only:
            self.output.warn("Header only package, skipping build")
            return

        self._bootstrap()

        flags = self._get_build_flags()
        # Help locating bzip2 and zlib
        self._create_user_config_jam(self.build_folder)

        # JOIN ALL FLAGS
        cmd = self._b2_exe
        cmd += " " + " ".join(flags)
        cmd += " -j%s" % tools.cpu_count()
        cmd += " --abbreviate-paths"
        # -d2 is to print more debug info and avoid travis timing out without output
        cmd += " -d2"
        cmd += " --debug-configuration"
        cmd += " --build-dir=\"%s\"" % self.build_folder
        cmd += " --stagedir=\"%s\"" % self.build_folder
        self.output.warn(cmd)

        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            with tools.chdir(self._boost_dist_root):
                # To show the libraries *1
                # self.run("%s --show-libraries" % b2_exe)
                self.run(cmd)

        arch = self.settings.get_safe('arch')
        if arch.startswith("asm.js"):
            self._create_emscripten_libs()

    def _create_emscripten_libs(self):
        # Boost Build doesn't create the libraries, but it gets close,
        # leaving .bc files where the libraries would be.
        staged_libs = os.path.join(
            self.source_folder, self._boost_dir, "stage", "lib"
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

    def _get_build_flags(self):

        if tools.cross_building(self.settings):
            flags = self._get_build_cross_flags()
        else:
            flags = []

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

        flags.append("--layout=%s" % self.options.layout)
        flags.append("-sBOOST_BUILD_PATH=%s" % self.build_folder)
        flags.append("-sBOOST_ROOT=%s" % self._boost_dist_root)
        flags.append("--user-config=%s" % os.path.join(self.build_folder, 'user-config.jam'))
        flags.append("-sNO_ZLIB=%s" % ("0" if self.options.zlib else "1"))
        flags.append("-sNO_BZIP2=%s" % ("0" if self.options.bzip2 else "1"))
        flags.append("-sNO_LZMA=%s" % ("0" if self.options.lzma else "1"))
        flags.append("-sNO_ZSTD=%s" % ("0" if self.options.zstd else "1"))

        def add_defines(option, library):
            if option:
                for define in self.deps_cpp_info[library].defines:
                    flags.append("define=%s" % define)

        if self._zip_bzip2_requires_needed:
            add_defines(self.options.zlib, "zlib")
            add_defines(self.options.bzip2, "bzip2")
            add_defines(self.options.lzma, "lzma")
            add_defines(self.options.zstd, "zstd")

        if self._is_msvc and self.settings.compiler.runtime:
            flags.append("runtime-link=%s" % ("static" if "MT" in str(self.settings.compiler.runtime) else "shared"))

        flags.append("threading=multi")

        flags.append("link=%s" % ("static" if not self.options.shared else "shared"))
        if self.settings.build_type == "Debug":
            flags.append("variant=debug")
        else:
            flags.append("variant=release")

        for libname in lib_list:
            if getattr(self.options, "without_%s" % libname):
                flags.append("--without-%s" % libname)

        toolset, _, _ = self._get_toolset_version_and_exe()
        flags.append("toolset=%s" % toolset)

        if self.settings.get_safe("compiler.cppstd"):
            flags.append("cxxflags=%s" % cppstd_flag(
                    self.settings.get_safe("compiler"),
                    self.settings.get_safe("compiler.version"),
                    self.settings.get_safe("compiler.cppstd")
                )
            )

        # CXX FLAGS
        cxx_flags = []
        # fPIC DEFINITION
        if self.settings.os != "Windows":
            if self.options.fPIC:
                cxx_flags.append("-fPIC")

        # Standalone toolchain fails when declare the std lib
        if self.settings.os != "Android":
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

        if tools.is_apple_os(self.settings.os):
            if self.settings.get_safe("os.version"):
                cxx_flags.append(tools.apple_deployment_target_flag(self.settings.os,
                                                                    self.settings.os.version))

        if self.settings.os == "iOS":
            cxx_flags.append("-DBOOST_AC_USE_PTHREADS")
            cxx_flags.append("-DBOOST_SP_USE_PTHREADS")
            cxx_flags.append("-fvisibility=hidden")
            cxx_flags.append("-fvisibility-inlines-hidden")
            cxx_flags.append("-fembed-bitcode")

        cxx_flags = 'cxxflags="%s"' % " ".join(cxx_flags) if cxx_flags else ""
        flags.append(cxx_flags)

        if self.options.extra_b2_flags:
            flags.append(str(self.options.extra_b2_flags))

        return flags

    def _get_build_cross_flags(self):
        arch = self.settings.get_safe('arch')
        flags = []
        self.output.info("Cross building, detecting compiler...")

        if arch.startswith('arm'):
            if 'hf' in arch:
                flags.append('-mfloat-abi=hard')
        elif arch in ["x86", "x86_64"]:
            pass
        elif arch.startswith("ppc"):
            pass
        elif arch.startswith("mips"):
            pass
        elif arch.startswith("asm.js"):
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
        return None

    def _create_user_config_jam(self, folder):
        """To help locating the zlib and bzip2 deps"""
        self.output.warn("Patching user-config.jam")

        compiler_command = self._cxx

        contents = ""
        if self._zip_bzip2_requires_needed:
            def create_library_config(name):
                includedir = self.deps_cpp_info[name].include_paths[0].replace('\\', '/')
                libdir = self.deps_cpp_info[name].lib_paths[0].replace('\\', '/')
                lib = self.deps_cpp_info[name].libs[0]
                version = self.deps_cpp_info[name].version
                return "\nusing {name} : {version} : " \
                       "<include>{includedir} " \
                       "<search>{libdir} " \
                       "<name>{lib} ;".format(name=name,
                                              version=version,
                                              includedir=includedir,
                                              libdir=libdir,
                                              lib=lib)

            contents = ""
            if self.options.zlib:
                contents += create_library_config("zlib")
            if self.options.bzip2:
                contents += create_library_config("bzip2")
            if self.options.lzma:
                contents += create_library_config("lzma")
            if self.options.zstd:
                contents += create_library_config("zstd")

        if not self.options.without_python:
            # https://www.boost.org/doc/libs/1_70_0/libs/python/doc/html/building/configuring_boost_build.html
            contents += '\nusing python : {version} : "{executable}" : "{includes}" : "{libraries}" ;'\
                .format(version=self._python_version,
                        executable=self._python_executable,
                        includes=self._python_includes,
                        libraries=self._python_libraries)

        toolset, version, exe = self._get_toolset_version_and_exe()
        exe = compiler_command or exe  # Prioritize CXX

        # Specify here the toolset with the binary if present if don't empty parameter : :
        contents += '\nusing "%s" : "%s" : ' % (toolset, version)
        contents += ' %s' % exe.replace("\\", "/")

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
        tools.save(filename, contents)

    def _get_toolset_version_and_exe(self):
        compiler_version = str(self.settings.compiler.version)
        compiler = str(self.settings.compiler)
        if self._is_msvc:
            cversion = self.settings.compiler.version
            if Version(str(cversion)) >= "16":
                _msvc_version = "14.2"
            elif Version(str(cversion)) >= "15":
                _msvc_version = "14.1"
            else:
                _msvc_version = "%s.0" % cversion
            return "msvc", _msvc_version, ""
        elif self.settings.os == "Windows" and self.settings.compiler == "clang":
            return "clang-win", compiler_version, ""
        elif self.settings.os == "Emscripten" and self.settings.compiler == "clang":
            return "emscripten", compiler_version, self._cxx
        elif self.settings.compiler == "gcc" and tools.is_apple_os(self.settings.os):
            return "darwin", compiler_version, self._cxx
        elif compiler == "gcc" and compiler_version[0] >= "5":
            # For GCC >= v5 we only need the major otherwise Boost doesn't find the compiler
            # The NOT windows check is necessary to exclude MinGW:
            if not tools.which("g++-%s" % compiler_version[0]):
                # In fedora 24, 25 the gcc is 6, but there is no g++-6 and the detection is 6.3.1
                # so b2 fails because 6 != 6.3.1. Specify the exe to avoid the smart detection
                executable = tools.which("g++") or ""
            else:
                executable = ""
            return compiler, compiler_version[0], executable
        elif self.settings.compiler == "apple-clang":
            return "clang-darwin", compiler_version, self._cxx
        elif self.settings.os == "Android" and self.settings.compiler == "clang":
            return "clang-linux", compiler_version, self._cxx
        elif str(self.settings.compiler) in ["clang", "gcc"]:
            # For GCC < v5 and Clang we need to provide the entire version string
            return compiler, compiler_version, ""
        elif self.settings.compiler == "sun-cc":
            return "sunpro", compiler_version, ""
        else:
            return compiler, compiler_version, ""

    ##################### BOOSTRAP METHODS ###########################
    def _get_boostrap_toolset(self):
        if self._is_msvc:
            comp_ver = self.settings.compiler.version
            if Version(str(comp_ver)) >= "16":
                return "vc142"
            elif Version(str(comp_ver)) >= "15":
                return "vc141"
            else:
                return "vc%s" % comp_ver

        if tools.os_info.is_windows:
            return "gcc" if self.settings.compiler == "gcc" else ""

        if tools.os_info.is_macos:
            return "clang"

        with_toolset = {"apple-clang": "clang"}.get(str(self.settings.compiler),
                                                    str(self.settings.compiler))

        # fallback for the case when no unversioned gcc/clang is available
        if with_toolset in ["gcc", "clang"]:
            # check for C++ compiler, as b2 uses only C++ one, which may not be installed alongside C compiler
            compiler = "g++" if with_toolset == "gcc" else "clang++"
            if not tools.which(compiler):
                with_toolset = "cxx" if Version(str(self.version)) >= "1.71" else "cc"
        return with_toolset

    def _bootstrap(self):
        try:
            bootstrap = \
                os.path.join(self._boost_dist_root,
                             "bootstrap.bat" if tools.os_info.is_windows else "bootstrap.sh")
            with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
                with tools.chdir(self.build_folder):
                    if tools.cross_building(self.settings):
                        cmd = bootstrap
                    else:
                        option = "" if tools.os_info.is_windows else "-with-toolset="
                        cmd = "%s %s%s" % (bootstrap, option, self._get_boostrap_toolset())
                    self.output.info(cmd)

                    removed_environment_variables = [
                        "CC",
                        "CXX",
                        "CFLAGS",
                        "CXXFLAGS",
                        "SDKROOT",
                        "IPHONEOS_DEPLOYMENT_TARGET"
                    ]
                    removed_environment_variables = dict((env_var, None) for env_var in removed_environment_variables)

                    with tools.environment_append(removed_environment_variables):
                        self.run(cmd)

        except Exception as exc:
            self.output.warn(str(exc))
            bootstrap_log = os.path.join(self.build_folder, "bootstrap.log")
            if os.path.exists(bootstrap_log):
                self.output.warn(tools.load(bootstrap_log))
            raise

    ####################################################################

    def package(self):
        self.copy("LICENSE_1_0.txt", dst="licenses", src=self._boost_dist_root)
        out_lib_dir = os.path.join(self.build_folder, "lib")
        self.copy(pattern="*", dst="include/boost", src="%s/boost" % self._boost_dist_root)
        if not self.options.shared:
            self.copy(pattern="*.a", dst="lib", src=out_lib_dir, keep_path=False)
        self.copy(pattern="*.so", dst="lib", src=out_lib_dir, keep_path=False, symlinks=True)
        self.copy(pattern="*.so.*", dst="lib", src=out_lib_dir, keep_path=False, symlinks=True)
        self.copy(pattern="*.dylib*", dst="lib", src=out_lib_dir, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=out_lib_dir, keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=out_lib_dir, keep_path=False)

    def package_info(self):
        gen_libs = [] if self.options.header_only else tools.collect_libs(self)

        # List of lists, so if more than one matches the lib like serialization and wserialization
        # both will be added to the list
        ordered_libs = [[] for _ in range(len(lib_list))]

        # The order is important, reorder following the lib_list order
        missing_order_info = []
        for real_lib_name in gen_libs:
            for pos, alib in enumerate(lib_list):
                if os.path.splitext(real_lib_name)[0].split("-")[0].endswith(alib):
                    ordered_libs[pos].append(real_lib_name)
                    break
            else:
                # self.output.info("Missing in order: %s" % real_lib_name)
                if "_exec_monitor" not in real_lib_name:  # https://github.com/bincrafters/community/issues/94
                    missing_order_info.append(real_lib_name)  # Assume they do not depend on other

        # Flat the list and append the missing order
        self.cpp_info.libs = [item for sublist in ordered_libs
                                      for item in sublist if sublist] + missing_order_info

        if self.options.without_test:  # remove boost_unit_test_framework
            self.cpp_info.libs = [lib for lib in self.cpp_info.libs if "unit_test" not in lib]

        self.output.info("LIBRARIES: %s" % self.cpp_info.libs)
        self.output.info("Package folder: %s" % self.package_folder)

        if not self.options.header_only and self.options.shared:
            self.cpp_info.defines.append("BOOST_ALL_DYN_LINK")

        if self.options.system_no_deprecated:
            self.cpp_info.defines.append("BOOST_SYSTEM_NO_DEPRECATED")

        if self.options.asio_no_deprecated:
            self.cpp_info.defines.append("BOOST_ASIO_NO_DEPRECATED")

        if self.options.filesystem_no_deprecated:
            self.cpp_info.defines.append("BOOST_FILESYSTEM_NO_DEPRECATED")

        if self.options.segmented_stacks:
            self.cpp_info.defines.extend(["BOOST_USE_SEGMENTED_STACKS", "BOOST_USE_UCONTEXT"])

        if self.settings.os != "Android":
            if self._gnu_cxx11_abi:
                self.cpp_info.defines.append("_GLIBCXX_USE_CXX11_ABI=%s" % self._gnu_cxx11_abi)

        if not self.options.header_only:
            if self.options.error_code_header_only:
                self.cpp_info.defines.append("BOOST_ERROR_CODE_HEADER_ONLY")

            if not self.options.without_python:
                if not self.options.shared:
                    self.cpp_info.defines.append("BOOST_PYTHON_STATIC_LIB")

            if self._is_msvc:
                if not self.options.magic_autolink:
                    # DISABLES AUTO LINKING! NO SMART AND MAGIC DECISIONS THANKS!
                    self.cpp_info.defines.append("BOOST_ALL_NO_LIB")
                    self.output.info("Disabled magic autolinking (smart and magic decisions)")
                else:
                    if self.options.layout == "system":
                        self.cpp_info.defines.append("BOOST_AUTO_LINK_SYSTEM")
                    elif self.options.layout == "tagged":
                        self.cpp_info.defines.append("BOOST_AUTO_LINK_TAGGED")
                    self.output.info("Enabled magic autolinking (smart and magic decisions)")

                # https://github.com/conan-community/conan-boost/issues/127#issuecomment-404750974
                self.cpp_info.libs.append("bcrypt")
            elif self.settings.os == "Linux":
                # https://github.com/conan-community/conan-boost/issues/135
                self.cpp_info.libs.append("pthread")

        self.env_info.BOOST_ROOT = self.package_folder
        self.cpp_info.names["cmake_find_package"] = "Boost"
        self.cpp_info.names["cmake_find_package_multi"] = "Boost"


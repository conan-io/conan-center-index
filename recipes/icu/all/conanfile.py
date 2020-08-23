import os
import glob
import platform
import shutil
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.tools import Version


class ICUBase(ConanFile):
    name = "icu"
    homepage = "http://site.icu-project.org"
    license = "ICU"
    description = "ICU is a mature, widely used set of C/C++ and Java libraries " \
                  "providing Unicode and Globalization support for software applications."
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "icu", "icu4c", "i see you", "unicode")
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _env_build = None
    settings = "os", "arch", "compiler", "build_type"
    exports = ["patches/*.patch"]
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "data_packaging": ["files", "archive", "library", "static"],
               "with_unit_tests": [True, False],
               "silent": [True, False],
               "with_dyload": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "data_packaging": "archive",
                       "with_unit_tests": False,
                       "silent": True,
                       "with_dyload": True}

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("icu", self._source_subfolder)

    def _workaround_icu_20545(self):
        if tools.os_info.is_windows:
            # https://unicode-org.atlassian.net/projects/ICU/issues/ICU-20545
            srcdir = os.path.join(self.build_folder, self._source_subfolder, "source")
            makeconv_cpp = os.path.join(srcdir, "tools", "makeconv", "makeconv.cpp")
            tools.replace_in_file(makeconv_cpp,
                                  "pathBuf.appendPathPart(arg, localError);",
                                  "pathBuf.append('/', localError); pathBuf.append(arg, localError);")

    def build(self):
        for p in self.conan_data["patches"][self.version]:
            tools.patch(**p)
        if self._is_msvc:
            run_configure_icu_file = os.path.join(self._source_subfolder, 'source', 'runConfigureICU')

            flags = "-%s" % self.settings.compiler.runtime
            if self.settings.get_safe("build_type") in ['Debug', 'RelWithDebInfo'] and Version(self.settings.compiler.version) >= "12":
                flags += " -FS"
            tools.replace_in_file(run_configure_icu_file, "-MDd", flags)
            tools.replace_in_file(run_configure_icu_file, "-MD", flags)

        self._workaround_icu_20545()

        self._env_build = AutoToolsBuildEnvironment(self)
        if not self.options.get_safe("shared"):
            self._env_build.defines.append("U_STATIC_IMPLEMENTATION")
        if tools.is_apple_os(self.settings.os):
            self._env_build.defines.append("_DARWIN_C_SOURCE")
            if self.settings.get_safe("os.version"):
                self._env_build.flags.append(tools.apple_deployment_target_flag(self.settings.os,
                                                                            self.settings.os.version))

        if "msys2" in self.deps_user_info:
            self._env_build.vars["PYTHON"] = tools.unix_path(os.path.join(self.deps_env_info["msys2"].MSYS_BIN, "python"), tools.MSYS2)

        build_dir = os.path.join(self.build_folder, self._source_subfolder, 'build')
        os.mkdir(build_dir)

        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            with tools.environment_append(self._env_build.vars):
                with tools.chdir(build_dir):
                    # workaround for https://unicode-org.atlassian.net/browse/ICU-20531
                    os.makedirs(os.path.join("data", "out", "tmp"))

                    self.run(self._build_config_cmd, win_bash=tools.os_info.is_windows)
                    if self.options.get_safe("silent"):
                        silent = '--silent' if self.options.silent else 'VERBOSE=1'
                    else:
                        silent = '--silent'
                    command = "make {silent} -j {cpu_count}".format(silent=silent,
                                                                    cpu_count=tools.cpu_count())
                    self.run(command, win_bash=tools.os_info.is_windows)
                    if self.options.get_safe("with_unit_tests"):
                        command = "make {silent} check".format(silent=silent)
                        self.run(command, win_bash=tools.os_info.is_windows)
                    command = "make {silent} install".format(silent=silent)
                    self.run(command, win_bash=tools.os_info.is_windows)

        self._install_name_tool()

    def package(self):
        for dll in glob.glob(os.path.join(self.package_folder, 'lib', '*.dll')):
            shutil.move(dll, os.path.join(self.package_folder, 'bin'))

        self.copy("LICENSE", dst="licenses", src=os.path.join(self.source_folder, self._source_subfolder))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    @property
    def build_config_args(self):
        prefix = self.package_folder.replace('\\', '/')
        platform = {("Windows", "Visual Studio"): "Cygwin/MSVC",
                    ("Windows", "gcc"): "MinGW",
                    ("AIX", "gcc"): "AIX/GCC",
                    ("AIX", "xlc"): "AIX",
                    ("SunOS", "gcc"): "Solaris/GCC",
                    ("Linux", "gcc"): "Linux/gcc",
                    ("Linux", "clang"): "Linux",
                    ("Macos", "gcc"): "MacOSX",
                    ("Macos", "clang"): "MacOSX",
                    ("Macos", "apple-clang"): "MacOSX"}.get((str(self.settings.os),
                                                             str(self.settings.compiler)))
        arch64 = ['x86_64', 'sparcv9', 'ppc64']
        bits = "64" if self.settings.arch in arch64 else "32"
        args = [platform,
                "--prefix={0}".format(prefix),
                "--with-library-bits={0}".format(bits),
                "--disable-samples",
                "--disable-layout",
                "--disable-layoutex",
                "--disable-extras"]
        
        if not self.options.with_dyload:
            args += ["--disable-dyload"]

        if tools.cross_building(self.settings, skip_x64_x86=True):
            if self._env_build.build:
                args.append("--build=%s" % self._env_build.build)
            if self._env_build.host:
                args.append("--host=%s" % self._env_build.host)
            if self._env_build.target:
                args.append("--target=%s" % self._env_build.target)

        if self.options.get_safe("data_packaging"):
            args.append("--with-data-packaging={0}".format(self.options.data_packaging))
        else:
            args.append("--with-data-packaging=static")
        datadir = os.path.join(self.package_folder, "lib")
        datadir = datadir.replace("\\", "/") if tools.os_info.is_windows else datadir
        args.append("--datarootdir=%s" % datadir)  # do not use share
        bindir = os.path.join(self.package_folder, "bin")
        bindir = bindir.replace("\\", "/") if tools.os_info.is_windows else bindir
        args.append("--sbindir=%s" % bindir)

        if self._is_mingw:
            mingw_chost = 'i686-w64-mingw32' if self.settings.arch == 'x86' else 'x86_64-w64-mingw32'
            args.extend(["--build={0}".format(mingw_chost),
                         "--host={0}".format(mingw_chost)])

        if self.settings.get_safe("build_type") == "Debug":
            args.extend(["--disable-release", "--enable-debug"])
        if self.options.get_safe("shared"):
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--enable-static", "--disable-shared"])
        if not self.options.get_safe("with_unit_tests"):
            args.append('--disable-tests')
        return args

    @property
    def _build_config_cmd(self):
        return "../source/runConfigureICU %s" % " ".join(self.build_config_args)

    def _install_name_tool(self):
        if tools.is_apple_os(self.settings.os):
            with tools.chdir(os.path.join(self.package_folder, 'lib')):
                for dylib in glob.glob('*icu*.{0}.dylib'.format(self.version)):
                    command = 'install_name_tool -id {0} {1}'.format(os.path.basename(dylib), dylib)
                    self.output.info(command)
                    self.run(command)

    def package_id(self):
        del self.info.options.with_unit_tests  # ICU unit testing shouldn't affect the package's ID
        del self.info.options.silent  # Verbosity doesn't affect package's ID

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def package_info(self):
        self.cpp_info.names['cmake_find_package'] = 'ICU'
        self.cpp_info.names['cmake_find_package_multi'] = 'ICU'

        def lib_name(lib):
            name = lib
            if self.settings.os == "Windows":
                if not self.options.shared:
                    name = 's' + name
                if self.settings.build_type == "Debug":
                    name += 'd'
            return name

        libs = ['icuin' if self.settings.os == "Windows" else 'icui18n',
                'icuio', 'icutest', 'icutu', 'icuuc',
                'icudt' if self.settings.os == "Windows" else 'icudata']
        self.cpp_info.libs = [lib_name(lib) for lib in libs]
        self.cpp_info.bindirs.append('lib')

        data_dir_name = self.name
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            data_dir_name += 'd'
        data_dir = os.path.join(self.package_folder, 'lib', data_dir_name, self.version)
        vtag = self.version.split('.')[0]
        data_file = "icudt{v}l.dat".format(v=vtag)
        data_path = os.path.join(data_dir, data_file).replace('\\', '/')
        if self.options.get_safe("data_packaging") in ["files", "archive"]:
            self.env_info.ICU_DATA.append(data_path)

        if not self.options.shared:
            self.cpp_info.defines.append("U_STATIC_IMPLEMENTATION")
        if self.settings.os == 'Linux':
            if self.options.with_dyload:
                self.cpp_info.system_libs.append('dl')
            self.cpp_info.system_libs.append('pthread')

        if self.settings.os == 'Windows':
            self.cpp_info.system_libs.append('advapi32')

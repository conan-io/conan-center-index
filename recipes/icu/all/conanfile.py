import glob
import os
import platform
import shutil

from conans import ConanFile, tools, AutoToolsBuildEnvironment


class ICUBase(ConanFile):
    name = "icu"
    homepage = "http://site.icu-project.org"
    license = "ICU"
    description = "ICU is a mature, widely used set of C/C++ and Java libraries " \
                  "providing Unicode and Globalization support for software applications."
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "icu", "icu4c", "i see you", "unicode")
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/*.patch"
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

    _env_build = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def package_id(self):
        del self.info.options.with_unit_tests  # ICU unit testing shouldn't affect the package's ID
        del self.info.options.silent  # Verbosity doesn't affect package's ID

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("icu", self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self._is_msvc:
            run_configure_icu_file = os.path.join(self._source_subfolder, "source", "runConfigureICU")

            flags = "-%s" % self.settings.compiler.runtime
            if self.settings.build_type in ["Debug", "RelWithDebInfo"] and tools.Version(self.settings.compiler.version) >= "12":
                flags += " -FS"
            tools.replace_in_file(run_configure_icu_file, "-MDd", flags)
            tools.replace_in_file(run_configure_icu_file, "-MD", flags)

        self._workaround_icu_20545()

        env_build = self._configure_autotools()
        build_dir = os.path.join(self.build_folder, self._source_subfolder, "build")
        os.mkdir(build_dir)
        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            with tools.environment_append(env_build.vars):
                with tools.chdir(build_dir):
                    # workaround for https://unicode-org.atlassian.net/browse/ICU-20531
                    os.makedirs(os.path.join("data", "out", "tmp"))

                    self.run(self._build_config_cmd, win_bash=tools.os_info.is_windows)
                    command = "make {silent} -j {cpu_count}".format(silent=self._silent,
                                                                    cpu_count=tools.cpu_count())
                    self.run(command, win_bash=tools.os_info.is_windows)
                    if self.options.with_unit_tests:
                        command = "make {silent} check".format(silent=self._silent)
                        self.run(command, win_bash=tools.os_info.is_windows)

    def _configure_autotools(self):
        if self._env_build:
            return self._env_build
        self._env_build = AutoToolsBuildEnvironment(self)
        if not self.options.shared:
            self._env_build.defines.append("U_STATIC_IMPLEMENTATION")
        if tools.is_apple_os(self.settings.os):
            self._env_build.defines.append("_DARWIN_C_SOURCE")
            if self.settings.get_safe("os.version"):
                self._env_build.flags.append(tools.apple_deployment_target_flag(self.settings.os,
                                                                            self.settings.os.version))

        if "msys2" in self.deps_user_info:
            self._env_build.vars["PYTHON"] = tools.unix_path(os.path.join(self.deps_env_info["msys2"].MSYS_BIN, "python"), tools.MSYS2)
        return self._env_build

    def _workaround_icu_20545(self):
        if tools.os_info.is_windows:
            # https://unicode-org.atlassian.net/projects/ICU/issues/ICU-20545
            srcdir = os.path.join(self.build_folder, self._source_subfolder, "source")
            makeconv_cpp = os.path.join(srcdir, "tools", "makeconv", "makeconv.cpp")
            tools.replace_in_file(makeconv_cpp,
                                  "pathBuf.appendPathPart(arg, localError);",
                                  "pathBuf.append(\"/\", localError); pathBuf.append(arg, localError);")

    @property
    def _build_config_cmd(self):
        prefix = self.package_folder.replace("\\", "/")
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
        arch64 = ['x86_64', 'sparcv9', 'ppc64', 'ppc64le', 'armv8', 'armv8.3', 'mips64']
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

        env_build = self._configure_autotools()
        if tools.cross_building(self.settings, skip_x64_x86=True):
            if env_build.build:
                args.append("--build=%s" % env_build.build)
            if env_build.host:
                args.append("--host=%s" % env_build.host)
            if env_build.target:
                args.append("--target=%s" % env_build.target)

        args.append("--with-data-packaging={0}".format(self.options.data_packaging))
        datadir = os.path.join(self.package_folder, "lib")
        datadir = datadir.replace("\\", "/") if tools.os_info.is_windows else datadir
        args.append("--datarootdir=%s" % datadir)  # do not use share
        bindir = os.path.join(self.package_folder, "bin")
        bindir = bindir.replace("\\", "/") if tools.os_info.is_windows else bindir
        args.append("--sbindir=%s" % bindir)

        if self._is_mingw:
            mingw_chost = "i686-w64-mingw32" if self.settings.arch == "x86" else "x86_64-w64-mingw32"
            args.extend(["--build={0}".format(mingw_chost),
                         "--host={0}".format(mingw_chost)])

        if self.settings.build_type == "Debug":
            args.extend(["--disable-release", "--enable-debug"])
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--enable-static", "--disable-shared"])
        if not self.options.with_unit_tests:
            args.append("--disable-tests")
        return "../source/runConfigureICU %s" % " ".join(args)

    @property
    def _silent(self):
        return "--silent" if self.options.silent else "VERBOSE=1"

    def package(self):
        self.copy("LICENSE", dst="licenses", src=os.path.join(self.source_folder, self._source_subfolder))

        env_build = self._configure_autotools()
        build_dir = os.path.join(self.build_folder, self._source_subfolder, "build")
        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            with tools.environment_append(env_build.vars):
                with tools.chdir(build_dir):
                    command = "make {silent} install".format(silent=self._silent)
                    self.run(command, win_bash=tools.os_info.is_windows)
        self._install_name_tool()

        for dll in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
            shutil.move(dll, os.path.join(self.package_folder, "bin"))

        if self.options.data_packaging in ["files", "archive"]:
            tools.mkdir(os.path.join(self.package_folder, "res"))
            shutil.move(self._data_path, os.path.join(self.package_folder, "res"))

        tools.rmdir(os.path.join(self.package_folder, "lib", "icu"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "man"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def _install_name_tool(self):
        if tools.is_apple_os(self.settings.os):
            with tools.chdir(os.path.join(self.package_folder, "lib")):
                for dylib in glob.glob("*icu*.{0}.dylib".format(self.version)):
                    command = "install_name_tool -id {0} {1}".format(os.path.basename(dylib), dylib)
                    self.output.info(command)
                    self.run(command)

    @property
    def _data_path(self):
        data_dir_name = "icu"
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            data_dir_name += "d"
        data_dir = os.path.join(self.package_folder, "lib", data_dir_name, self.version)
        return os.path.join(data_dir, self._data_filename)

    @property
    def _data_filename(self):
        vtag = self.version.split(".")[0]
        return "icudt{}l.dat".format(vtag)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "ICU"
        self.cpp_info.names["cmake_find_package_multi"] = "ICU"

        # icudata
        self.cpp_info.components["icu-data"].names["cmake_find_package"] = "data"
        self.cpp_info.components["icu-data"].names["cmake_find_package_multi"] = "data"
        self.cpp_info.components["icu-data"].libs = [self._lib_name("icudt" if self.settings.os == "Windows" else "icudata")]
        if not self.options.shared:
            self.cpp_info.components["icu-data"].defines.append("U_STATIC_IMPLEMENTATION")

        # icu uses c++, so add the c++ runtime
        if tools.stdcpp_library(self):
            self.cpp_info.components["icu-data"].system_libs.append(tools.stdcpp_library(self))

        # Alias of data CMake component
        self.cpp_info.components["icu-data-alias"].names["cmake_find_package"] = "dt"
        self.cpp_info.components["icu-data-alias"].names["cmake_find_package_multi"] = "dt"
        self.cpp_info.components["icu-data-alias"].requires = ["icu-data"]

        # icuuc
        self.cpp_info.components["icu-uc"].names["cmake_find_package"] = "uc"
        self.cpp_info.components["icu-uc"].names["cmake_find_package_multi"] = "uc"
        self.cpp_info.components["icu-uc"].names["pkg_config"] = "icu-uc"
        self.cpp_info.components["icu-uc"].libs = [self._lib_name("icuuc")]
        self.cpp_info.components["icu-uc"].requires = ["icu-data"]
        if self.settings.os == "Linux":
            self.cpp_info.components["icu-uc"].system_libs = ["m", "pthread"]
            if self.options.with_dyload:
                self.cpp_info.components["icu-uc"].system_libs.append("dl")
        elif self.settings.os == "Windows":
            self.cpp_info.components["icu-uc"].system_libs = ["advapi32"]

        # icui18n
        self.cpp_info.components["icu-i18n"].names["cmake_find_package"] = "i18n"
        self.cpp_info.components["icu-i18n"].names["cmake_find_package_multi"] = "i18n"
        self.cpp_info.components["icu-i18n"].names["pkg_config"] = "icu-i18n"
        self.cpp_info.components["icu-i18n"].libs = [self._lib_name("icuin" if self.settings.os == "Windows" else "icui18n")]
        self.cpp_info.components["icu-i18n"].requires = ["icu-uc"]
        if self.settings.os == "Linux":
            self.cpp_info.components["icu-i18n"].system_libs = ["m"]

        # Alias of i18n CMake component
        self.cpp_info.components["icu-i18n-alias"].names["cmake_find_package"] = "in"
        self.cpp_info.components["icu-i18n-alias"].names["cmake_find_package_multi"] = "in"
        self.cpp_info.components["icu-i18n-alias"].requires = ["icu-i18n"]

        # icuio
        self.cpp_info.components["icu-io"].names["cmake_find_package"] = "io"
        self.cpp_info.components["icu-io"].names["cmake_find_package_multi"] = "io"
        self.cpp_info.components["icu-io"].names["pkg_config"] = "icu-io"
        self.cpp_info.components["icu-io"].libs = [self._lib_name("icuio")]
        self.cpp_info.components["icu-io"].requires = ["icu-i18n", "icu-uc"]

        # icutu
        self.cpp_info.components["icu-tu"].names["cmake_find_package"] = "tu"
        self.cpp_info.components["icu-tu"].names["cmake_find_package_multi"] = "tu"
        self.cpp_info.components["icu-tu"].libs = [self._lib_name("icutu")]
        self.cpp_info.components["icu-tu"].requires = ["icu-i18n", "icu-uc"]
        if self.settings.os == "Linux":
            self.cpp_info.components["icu-tu"].system_libs = ["pthread"]

        # icutest
        self.cpp_info.components["icu-test"].names["cmake_find_package"] = "test"
        self.cpp_info.components["icu-test"].names["cmake_find_package_multi"] = "test"
        self.cpp_info.components["icu-test"].libs = [self._lib_name("icutest")]
        self.cpp_info.components["icu-test"].requires = ["icu-tu", "icu-uc"]

        if self.options.data_packaging in ["files", "archive"]:
            data_path = os.path.join(self.package_folder, "res", self._data_filename).replace("\\", "/")
            self.output.info("Appending ICU_DATA environment variable: {}".format(data_path))
            self.env_info.ICU_DATA.append(data_path)

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

    def _lib_name(self, lib):
        name = lib
        if self.settings.os == "Windows":
            if not self.options.shared:
                name = "s" + name
            if self.settings.build_type == "Debug":
                name += "d"
        return name

from conan.tools.microsoft import msvc_runtime_flag
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import glob
import os
import shutil

required_conan_version = ">=1.43.0"


class ICUBase(ConanFile):
    name = "icu"
    homepage = "http://site.icu-project.org"
    license = "ICU"
    description = "ICU is a mature, widely used set of C/C++ and Java libraries " \
                  "providing Unicode and Globalization support for software applications."
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("icu", "icu4c", "i see you", "unicode")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "data_packaging": ["files", "archive", "library", "static"],
        "with_unit_tests": [True, False],
        "silent": [True, False],
        "with_dyload": [True, False],
        "dat_package_file": "ANY",
        "with_icuio": [True, False],
        "with_extras": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "data_packaging": "archive",
        "with_unit_tests": False,
        "silent": True,
        "with_dyload": True,
        "dat_package_file": None,
        "with_icuio": True,
        "with_extras": False,
    }

    _env_build = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _make_tool(self):
        return "make" if self.settings.os != "FreeBSD" else "gmake"

    @property
    def _enable_icu_tools(self):
        return self.settings.os not in ["iOS", "tvOS", "watchOS"]

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.data_packaging

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def package_id(self):
        del self.info.options.with_unit_tests  # ICU unit testing shouldn't affect the package's ID
        del self.info.options.silent  # Verbosity doesn't affect package's ID
        if self.info.options.dat_package_file:
            dat_package_file_sha256 = tools.sha256sum(str(self.info.options.dat_package_file))
            self.info.options.dat_package_file = dat_package_file_sha256

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

        if tools.cross_building(self, skip_x64_x86=True) and hasattr(self, 'settings_build'):
            self.build_requires("icu/{}".format(self.version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        self._patch_sources()

        if self.options.dat_package_file:
            dat_package_file = glob.glob(os.path.join(self.source_folder, self._source_subfolder, "source", "data", "in", "*.dat"))
            if dat_package_file:
                shutil.copy(str(self.options.dat_package_file), dat_package_file[0])

        env_build = self._configure_autotools()
        build_dir = os.path.join(self.build_folder, self._source_subfolder, "build")
        os.mkdir(build_dir)
        build_env = env_build.vars
        if self._is_msvc:
            build_env.update({'CC': 'cl', 'CXX': 'cl'})
        with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
            with tools.environment_append(build_env):
                with tools.chdir(build_dir):
                    # workaround for https://unicode-org.atlassian.net/browse/ICU-20531
                    os.makedirs(os.path.join("data", "out", "tmp"))
                    # workaround for "No rule to make target 'out/tmp/dirs.timestamp'"
                    tools.files.save(self, os.path.join("data", "out", "tmp", "dirs.timestamp"), "")

                    self.run(self._build_config_cmd, win_bash=tools.os_info.is_windows)
                    command = "{make} {silent} -j {cpu_count}".format(make=self._make_tool,
                                                                      silent=self._silent,
                                                                      cpu_count=tools.cpu_count())
                    self.run(command, win_bash=tools.os_info.is_windows)
                    if self.options.with_unit_tests:
                        command = "{make} {silent} check".format(make=self._make_tool,
                                                                 silent=self._silent)
                        self.run(command, win_bash=tools.os_info.is_windows)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        if tools.os_info.is_windows:
            # https://unicode-org.atlassian.net/projects/ICU/issues/ICU-20545
            srcdir = os.path.join(self.build_folder, self._source_subfolder, "source")
            makeconv_cpp = os.path.join(srcdir, "tools", "makeconv", "makeconv.cpp")
            tools.files.replace_in_file(self, makeconv_cpp,
                                  "pathBuf.appendPathPart(arg, localError);",
                                  "pathBuf.append(\"/\", localError); pathBuf.append(arg, localError);")

        # relocatable shared libs on macOS
        mh_darwin = os.path.join(self._source_subfolder, "source", "config", "mh-darwin")
        tools.files.replace_in_file(self, mh_darwin, "-install_name $(libdir)/$(notdir", "-install_name @rpath/$(notdir")
        tools.files.replace_in_file(self, 
            mh_darwin,
            "-install_name $(notdir $(MIDDLE_SO_TARGET)) $(PKGDATA_TRAILING_SPACE)",
            "-install_name @rpath/$(notdir $(MIDDLE_SO_TARGET))",
        )

    def _configure_autotools(self):
        if self._env_build:
            return self._env_build
        self._env_build = AutoToolsBuildEnvironment(self)
        if self._is_msvc:
            self._env_build.flags.append("-FS")
        if not self.options.shared:
            self._env_build.defines.append("U_STATIC_IMPLEMENTATION")
        if tools.is_apple_os(self.settings.os):
            self._env_build.defines.append("_DARWIN_C_SOURCE")
        if "msys2" in self.deps_user_info:
            self._env_build.vars["PYTHON"] = tools.unix_path(os.path.join(self.deps_env_info["msys2"].MSYS_BIN, "python"), tools.MSYS2)
        return self._env_build

    @property
    def _build_config_cmd(self):
        prefix = self.package_folder.replace("\\", "/")
        arch64 = ['x86_64', 'sparcv9', 'ppc64', 'ppc64le', 'armv8', 'armv8.3', 'mips64']
        bits = "64" if self.settings.arch in arch64 else "32"
        args = ["--prefix={0}".format(prefix),
                "--disable-samples",
                "--disable-layout",
                "--disable-layoutex"]

        if not self.options.with_dyload:
            args += ["--disable-dyload"]

        if not self._enable_icu_tools:
            args.append("--disable-tools")

        if not self.options.with_icuio:
            args.append("--disable-icuio")

        if not self.options.with_extras:
            args.append("--disable-extras")

        env_build = self._configure_autotools()
        if tools.cross_building(self, skip_x64_x86=True):
            if self.settings.os in ["iOS", "tvOS", "watchOS"]:
                args.append("--host={}".format(tools.get_gnu_triplet("Macos", str(self.settings.arch))))
            elif env_build.host:
                args.append("--host={}".format(env_build.host))
            bin_path = self.deps_env_info["icu"].PATH[0].replace("\\", "/")
            base_path, _ = bin_path.rsplit('/', 1)
            args.append("--with-cross-build={}".format(base_path))
        else:
            args.append("--with-library-bits={0}".format(bits),)

        if self.settings.os != "Windows":
            # http://userguide.icu-project.org/icudata
            # This is the only directly supported behavior on Windows builds.
            args.append("--with-data-packaging={0}".format(self.options.data_packaging))

        datadir = os.path.join(self.package_folder, "lib")
        datadir = datadir.replace("\\", "/") if tools.os_info.is_windows else datadir
        args.append("--datarootdir=%s" % datadir)  # do not use share
        bindir = os.path.join(self.package_folder, "bin")
        bindir = bindir.replace("\\", "/") if tools.os_info.is_windows else bindir
        args.append("--sbindir=%s" % bindir)
        libdir = os.path.join(self.package_folder, "lib")
        libdir = libdir.replace("\\", "/") if tools.os_info.is_windows else libdir
        args.append("--libdir=%s" % libdir)

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
        return "../source/configure %s" % " ".join(args)

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
                    command = "{make} {silent} install".format(make=self._make_tool,
                                                               silent=self._silent)
                    self.run(command, win_bash=tools.os_info.is_windows)

        for dll in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
            shutil.move(dll, os.path.join(self.package_folder, "bin"))

        if self.settings.os != "Windows" and self.options.data_packaging in ["files", "archive"]:
            tools.mkdir(os.path.join(self.package_folder, "res"))
            shutil.move(self._data_path, os.path.join(self.package_folder, "res"))

        # Copy some files required for cross-compiling
        self.copy("icucross.mk", src=os.path.join(build_dir, "config"), dst="config")
        self.copy("icucross.inc", src=os.path.join(build_dir, "config"), dst="config")

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "icu"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "man"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

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
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "ICU")

        self.cpp_info.names["cmake_find_package"] = "ICU"
        self.cpp_info.names["cmake_find_package_multi"] = "ICU"

        # icudata
        self.cpp_info.components["icu-data"].set_property("cmake_target_name", "ICU::data")
        self.cpp_info.components["icu-data"].names["cmake_find_package"] = "data"
        self.cpp_info.components["icu-data"].names["cmake_find_package_multi"] = "data"
        self.cpp_info.components["icu-data"].libs = [self._lib_name("icudt" if self.settings.os == "Windows" else "icudata")]
        if not self.options.shared:
            self.cpp_info.components["icu-data"].defines.append("U_STATIC_IMPLEMENTATION")

        # icu uses c++, so add the c++ runtime
        if tools.stdcpp_library(self):
            self.cpp_info.components["icu-data"].system_libs.append(tools.stdcpp_library(self))

        # Alias of data CMake component
        self.cpp_info.components["icu-data-alias"].set_property("cmake_target_name", "ICU::dt")
        self.cpp_info.components["icu-data-alias"].names["cmake_find_package"] = "dt"
        self.cpp_info.components["icu-data-alias"].names["cmake_find_package_multi"] = "dt"
        self.cpp_info.components["icu-data-alias"].requires = ["icu-data"]

        # icuuc
        self.cpp_info.components["icu-uc"].set_property("cmake_target_name", "ICU::uc")
        self.cpp_info.components["icu-uc"].set_property("pkg_config_name", "icu-uc")
        self.cpp_info.components["icu-uc"].names["cmake_find_package"] = "uc"
        self.cpp_info.components["icu-uc"].names["cmake_find_package_multi"] = "uc"
        self.cpp_info.components["icu-uc"].libs = [self._lib_name("icuuc")]
        self.cpp_info.components["icu-uc"].requires = ["icu-data"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["icu-uc"].system_libs = ["m", "pthread"]
            if self.options.with_dyload:
                self.cpp_info.components["icu-uc"].system_libs.append("dl")
        elif self.settings.os == "Windows":
            self.cpp_info.components["icu-uc"].system_libs = ["advapi32"]

        # icui18n
        self.cpp_info.components["icu-i18n"].set_property("cmake_target_name", "ICU::i18n")
        self.cpp_info.components["icu-i18n"].set_property("pkg_config_name", "icu-i18n")
        self.cpp_info.components["icu-i18n"].names["cmake_find_package"] = "i18n"
        self.cpp_info.components["icu-i18n"].names["cmake_find_package_multi"] = "i18n"
        self.cpp_info.components["icu-i18n"].libs = [self._lib_name("icuin" if self.settings.os == "Windows" else "icui18n")]
        self.cpp_info.components["icu-i18n"].requires = ["icu-uc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["icu-i18n"].system_libs = ["m"]

        # Alias of i18n CMake component
        self.cpp_info.components["icu-i18n-alias"].set_property("cmake_target_name", "ICU::in")
        self.cpp_info.components["icu-i18n-alias"].names["cmake_find_package"] = "in"
        self.cpp_info.components["icu-i18n-alias"].names["cmake_find_package_multi"] = "in"
        self.cpp_info.components["icu-i18n-alias"].requires = ["icu-i18n"]

        # icuio
        if self.options.with_icuio:
            self.cpp_info.components["icu-io"].set_property("cmake_target_name", "ICU::io")
            self.cpp_info.components["icu-io"].set_property("pkg_config_name", "icu-io")
            self.cpp_info.components["icu-io"].names["cmake_find_package"] = "io"
            self.cpp_info.components["icu-io"].names["cmake_find_package_multi"] = "io"
            self.cpp_info.components["icu-io"].libs = [self._lib_name("icuio")]
            self.cpp_info.components["icu-io"].requires = ["icu-i18n", "icu-uc"]

        if self.settings.os != "Windows" and self.options.data_packaging in ["files", "archive"]:
            data_path = os.path.join(self.package_folder, "res", self._data_filename).replace("\\", "/")
            self.output.info("Prepending to ICU_DATA runtime environment variable: {}".format(data_path))
            self.runenv_info.prepend_path("ICU_DATA", data_path)
            if self._enable_icu_tools or self.options.with_extras:
                self.buildenv_info.prepend_path("ICU_DATA", data_path)
            # TODO: to remove after conan v2, it allows to not break consumers still relying on virtualenv generator
            self.env_info.ICU_DATA.append(data_path)

        if self._enable_icu_tools:
            # icutu
            self.cpp_info.components["icu-tu"].set_property("cmake_target_name", "ICU::tu")
            self.cpp_info.components["icu-tu"].names["cmake_find_package"] = "tu"
            self.cpp_info.components["icu-tu"].names["cmake_find_package_multi"] = "tu"
            self.cpp_info.components["icu-tu"].libs = [self._lib_name("icutu")]
            self.cpp_info.components["icu-tu"].requires = ["icu-i18n", "icu-uc"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["icu-tu"].system_libs = ["pthread"]

            # icutest
            self.cpp_info.components["icu-test"].set_property("cmake_target_name", "ICU::test")
            self.cpp_info.components["icu-test"].names["cmake_find_package"] = "test"
            self.cpp_info.components["icu-test"].names["cmake_find_package_multi"] = "test"
            self.cpp_info.components["icu-test"].libs = [self._lib_name("icutest")]
            self.cpp_info.components["icu-test"].requires = ["icu-tu", "icu-uc"]

        if self._enable_icu_tools or self.options.with_extras:
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

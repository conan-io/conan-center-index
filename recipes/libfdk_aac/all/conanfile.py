from conans import ConanFile, AutoToolsBuildEnvironment, CMake, VisualStudioBuildEnvironment, tools
import contextlib
import os

required_conan_version = ">=1.33.0"


class LibFDKAACConan(ConanFile):
    name = "libfdk_aac"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A standalone library of the Fraunhofer FDK AAC code from Android"
    license = "https://github.com/mstorsjo/fdk-aac/blob/master/NOTICE"
    homepage = "https://sourceforge.net/projects/opencore-amr/"
    topics = ("libfdk_aac", "multimedia", "audio", "fraunhofer", "aac", "decoder", "encoding", "decoding")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    _cmake = None
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _use_cmake(self):
        return tools.Version(self.version) >= "2.0.2"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        if not self._use_cmake and self.settings.compiler != "Visual Studio":
            self.build_requires("libtool/2.4.6")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_PROGRAMS"] = False
        self._cmake.definitions["FDK_AAC_INSTALL_CMAKE_CONFIG_MODULE"] = False
        self._cmake.definitions["FDK_AAC_INSTALL_PKGCONFIG_MODULE"] = False
        self._cmake.configure()
        return self._cmake

    @contextlib.contextmanager
    def _msvc_build_environment(self):
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    yield

    def _build_vs(self):
        with self._msvc_build_environment():
            # Rely on flags injected by conan
            tools.replace_in_file("Makefile.vc",
                                  "CFLAGS   = /nologo /W3 /Ox /MT",
                                  "CFLAGS   = /nologo")
            tools.replace_in_file("Makefile.vc",
                                  "MKDIR_FLAGS = -p",
                                  "MKDIR_FLAGS =")
            # Build either shared or static, and don't build utility (it always depends on static lib)
            tools.replace_in_file("Makefile.vc", "copy $(PROGS) $(bindir)", "")
            tools.replace_in_file("Makefile.vc", "copy $(LIB_DEF) $(libdir)", "")
            if self.options.shared:
                tools.replace_in_file("Makefile.vc",
                                      "all: $(LIB_DEF) $(STATIC_LIB) $(SHARED_LIB) $(IMP_LIB) $(PROGS)",
                                      "all: $(LIB_DEF) $(SHARED_LIB) $(IMP_LIB)")
                tools.replace_in_file("Makefile.vc", "copy $(STATIC_LIB) $(libdir)", "")
            else:
                tools.replace_in_file("Makefile.vc",
                                      "all: $(LIB_DEF) $(STATIC_LIB) $(SHARED_LIB) $(IMP_LIB) $(PROGS)",
                                      "all: $(STATIC_LIB)")
                tools.replace_in_file("Makefile.vc", "copy $(IMP_LIB) $(libdir)", "")
                tools.replace_in_file("Makefile.vc", "copy $(SHARED_LIB) $(bindir)", "")
            self.run("nmake -f Makefile.vc")

    def _build_autotools(self):
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
            if self.settings.os == "Android" and tools.os_info.is_windows:
                # remove escape for quotation marks, to make ndk on windows happy
                tools.replace_in_file("configure",
                    "s/[	 `~#$^&*(){}\\\\|;'\\\''\"<>?]/\\\\&/g", "s/[	 `~#$^&*(){}\\\\|;<>?]/\\\\&/g")
        autotools = self._configure_autotools()
        autotools.make()

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        if self._use_cmake:
            cmake = self._configure_cmake()
            cmake.build()
        elif self.settings.compiler == "Visual Studio":
            self._build_vs()
        else:
            self._build_autotools()

    def package(self):
        self.copy(pattern="NOTICE", src=self._source_subfolder, dst="licenses")
        if self._use_cmake:
            cmake = self._configure_cmake()
            cmake.install()
        elif self.settings.compiler == "Visual Studio":
            with self._msvc_build_environment():
                self.run("nmake -f Makefile.vc prefix=\"{}\" install".format(self.package_folder))
            if self.options.shared:
                tools.rename(os.path.join(self.package_folder, "lib", "fdk-aac.dll.lib"),
                             os.path.join(self.package_folder, "lib", "fdk-aac.lib"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "fdk-aac"
        self.cpp_info.filenames["cmake_find_package_multi"] = "fdk-aac"
        self.cpp_info.names["cmake_find_package"] = "FDK-AAC"
        self.cpp_info.names["cmake_find_package_multi"] = "FDK-AAC"
        self.cpp_info.names["pkg_config"] = "fdk-aac"
        self.cpp_info.components["fdk-aac"].names["cmake_find_package"] = "fdk-aac"
        self.cpp_info.components["fdk-aac"].names["cmake_find_package_multi"] = "fdk-aac"
        self.cpp_info.components["fdk-aac"].libs = ["fdk-aac"]
        if self.settings.os in ["Linux", "FreeBSD", "Android"]:
            self.cpp_info.components["fdk-aac"].system_libs.append("m")

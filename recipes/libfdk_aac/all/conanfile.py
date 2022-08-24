from conans import ConanFile, AutoToolsBuildEnvironment, CMake, VisualStudioBuildEnvironment, tools
import contextlib
import functools
import os

required_conan_version = ">=1.43.0"


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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

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
        if not self._use_cmake and not self._is_msvc:
            self.build_requires("libtool/2.4.6")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_PROGRAMS"] = False
        cmake.definitions["FDK_AAC_INSTALL_CMAKE_CONFIG_MODULE"] = False
        cmake.definitions["FDK_AAC_INSTALL_PKGCONFIG_MODULE"] = False
        cmake.configure()
        return cmake

    @contextlib.contextmanager
    def _msvc_build_environment(self):
        with tools.files.chdir(self, self._source_subfolder):
            with tools.vcvars(self):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    yield

    def _build_vs(self):
        with self._msvc_build_environment():
            # Rely on flags injected by conan
            tools.files.replace_in_file(self, "Makefile.vc",
                                  "CFLAGS   = /nologo /W3 /Ox /MT",
                                  "CFLAGS   = /nologo")
            tools.files.replace_in_file(self, "Makefile.vc",
                                  "MKDIR_FLAGS = -p",
                                  "MKDIR_FLAGS =")
            # Build either shared or static, and don't build utility (it always depends on static lib)
            tools.files.replace_in_file(self, "Makefile.vc", "copy $(PROGS) $(bindir)", "")
            tools.files.replace_in_file(self, "Makefile.vc", "copy $(LIB_DEF) $(libdir)", "")
            if self.options.shared:
                tools.files.replace_in_file(self, "Makefile.vc",
                                      "all: $(LIB_DEF) $(STATIC_LIB) $(SHARED_LIB) $(IMP_LIB) $(PROGS)",
                                      "all: $(LIB_DEF) $(SHARED_LIB) $(IMP_LIB)")
                tools.files.replace_in_file(self, "Makefile.vc", "copy $(STATIC_LIB) $(libdir)", "")
            else:
                tools.files.replace_in_file(self, "Makefile.vc",
                                      "all: $(LIB_DEF) $(STATIC_LIB) $(SHARED_LIB) $(IMP_LIB) $(PROGS)",
                                      "all: $(STATIC_LIB)")
                tools.files.replace_in_file(self, "Makefile.vc", "copy $(IMP_LIB) $(libdir)", "")
                tools.files.replace_in_file(self, "Makefile.vc", "copy $(SHARED_LIB) $(bindir)", "")
            self.run("nmake -f Makefile.vc")

    def _build_autotools(self):
        with tools.files.chdir(self, self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
            # relocatable shared lib on macOS
            tools.files.replace_in_file(self, "configure", "-install_name \\$rpath/", "-install_name @rpath/")
            if self.settings.os == "Android" and tools.os_info.is_windows:
                # remove escape for quotation marks, to make ndk on windows happy
                tools.files.replace_in_file(self, "configure",
                    "s/[	 `~#$^&*(){}\\\\|;'\\\''\"<>?]/\\\\&/g", "s/[	 `~#$^&*(){}\\\\|;<>?]/\\\\&/g")
        autotools = self._configure_autotools()
        autotools.make()

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        autotools.configure(args=args, configure_dir=self._source_subfolder)
        return autotools

    def build(self):
        if self._use_cmake:
            cmake = self._configure_cmake()
            cmake.build()
        elif self._is_msvc:
            self._build_vs()
        else:
            self._build_autotools()

    def package(self):
        self.copy(pattern="NOTICE", src=self._source_subfolder, dst="licenses")
        if self._use_cmake:
            cmake = self._configure_cmake()
            cmake.install()
        elif self._is_msvc:
            with self._msvc_build_environment():
                self.run("nmake -f Makefile.vc prefix=\"{}\" install".format(self.package_folder))
            if self.options.shared:
                tools.files.rename(self, os.path.join(self.package_folder, "lib", "fdk-aac.dll.lib"),
                             os.path.join(self.package_folder, "lib", "fdk-aac.lib"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fdk-aac")
        self.cpp_info.set_property("cmake_target_name", "FDK-AAC::fdk-aac")
        self.cpp_info.set_property("pkg_config_name", "fdk-aac")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["fdk-aac"].libs = ["fdk-aac"]
        if self.settings.os in ["Linux", "FreeBSD", "Android"]:
            self.cpp_info.components["fdk-aac"].system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "fdk-aac"
        self.cpp_info.filenames["cmake_find_package_multi"] = "fdk-aac"
        self.cpp_info.names["cmake_find_package"] = "FDK-AAC"
        self.cpp_info.names["cmake_find_package_multi"] = "FDK-AAC"
        self.cpp_info.names["pkg_config"] = "fdk-aac"
        self.cpp_info.components["fdk-aac"].names["cmake_find_package"] = "fdk-aac"
        self.cpp_info.components["fdk-aac"].names["cmake_find_package_multi"] = "fdk-aac"
        self.cpp_info.components["fdk-aac"].set_property("cmake_target_name", "FDK-AAC::fdk-aac")

from conans import ConanFile, AutoToolsBuildEnvironment, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class LibelfConan(ConanFile):
    name = "libelf"
    description = "ELF object file access library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://directory.fsf.org/wiki/Libelf"
    license = "LGPL-2.0"
    topics = ("conan", "elf", "fsf", "libelf", "object-file")
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _autotools = None
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared and self.settings.os not in ["Linux", "Windows"]:
            raise ConanInvalidConfiguration("libelf can not be built as shared library on non linux or windows platforms")

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.build_requires("autoconf/2.69")
            self.build_requires("gnu-config/cci.20201022")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _build_cmake(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _package_cmake(self):
        cmake = self._configure_cmake()
        cmake.install()

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        with tools.chdir(self._source_subfolder):
            self.run("autoreconf -fiv", run_environment=True)
        args = ["--enable-shared={}".format("yes" if self.options.shared else "no")]
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def _build_autotools(self):
        autotools = self._configure_autotools()
        autotools.make()

    def _package_autotools(self):
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "locale"))
        if self.settings.os == "Linux" and self.options.shared:
            os.remove(os.path.join(self.package_folder, "lib", "libelf.a"))

    @property
    def _user_info_build(self):
        # If using the experimental feature with different context for host and
        # build, the 'user_info' attributes of the 'build_requires' packages
        # will be located into the 'user_info_build' object. In other cases they
        # will be located into the 'deps_user_info' object.
        return getattr(self, "user_info_build", None) or self.deps_user_info

    def build(self):
        if self.settings.os == "Windows":
            self._build_cmake()
        else:
            tools.replace_in_file(os.path.join(self._source_subfolder, "lib", "Makefile.in"),
                                  "$(LINK_SHLIB)",
                                  "$(LINK_SHLIB) $(LDFLAGS)")
            # libelf sources contains really outdated 'config.sub' and
            # 'config.guess' files. It not allows to build libelf for armv8 arch.
            shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                        os.path.join(self._source_subfolder, "config.sub"))
            shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                        os.path.join(self._source_subfolder, "config.guess"))
            self._build_autotools()

    def package(self):
        self.copy(pattern="COPYING.LIB", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Windows":
            self._package_cmake()
        else:
            self._package_autotools()
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

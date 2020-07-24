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
    exports_sources = ["CMakeLists.txt", "cmake/CMakeLists.txt"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    _autotools = None
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os != "Linux":
            if self.options.shared:
                raise ConanInvalidConfiguration("libelf can not be built as shared library on non linux platforms")

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
        shutil.copyfile(os.path.join("cmake", "CMakeLists.txt"), os.path.join(self._source_subfolder, "CMakeLists.txt"))
        cmake = self._configure_cmake()
        cmake.build()

    def _package_cmake(self):
        cmake = self._configure_cmake()
        cmake.install()

    def _configure_autotools(self):
        if not self._autotools:
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
        shutil.rmtree(os.path.join(self.package_folder, "share"), ignore_errors=True)
        shutil.rmtree(os.path.join(self.package_folder, "lib", "locale"), ignore_errors=True)
        if self.settings.os == "Linux" and self.options.shared:
            os.remove(os.path.join(self.package_folder, "lib", "libelf.a"))

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "lib", "Makefile.in"),
                              "$(LINK_SHLIB)",
                              "$(LINK_SHLIB) $(LDFLAGS)")
        if self.settings.os == "Windows":
            self._build_cmake()
        else:
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

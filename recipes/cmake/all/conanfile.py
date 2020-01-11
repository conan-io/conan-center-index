import os
from conans import tools, ConanFile, CMake
from conans import __version__ as conan_version
from conans.model.version import Version
from conans.errors import ConanInvalidConfiguration, NotFoundException, ConanException


class CMakeConan(ConanFile):
    name = "cmake"
    description = "Conan installer for CMake"
    topics = ("conan", "cmake", "build", "installer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Kitware/CMake"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os_build", "arch_build", "compiler", "arch"

    _source_subfolder = "source_subfolder"

    @property
    def _arch(self):
        return self.settings.get_safe("arch_build") or self.settings.get_safe("arch")

    @property
    def _os(self):
        return self.settings.get_safe("os_build") or self.settings.get_safe("os")

    def _minor_version(self):
        return ".".join(str(self.version).split(".")[:2])

    def configure(self):
        if self._os == "Macos" and self._arch == "x86":
            raise ConanInvalidConfiguration("CMake does not support x86 for macOS")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_BOOTSTRAP"] = False
        if self.settings.os_build == "Linux":
            cmake.definitions["OPENSSL_USE_STATIC_LIBS"] = True
            cmake.definitions["CMAKE_EXE_LINKER_FLAGS"] = "-lz"
        cmake.configure(source_dir=self._source_subfolder)
        return cmake

    def build(self):
        if self.settings.os_build == "Linux":
            tools.replace_in_file(os.path.join(self._source_subfolder, "Utilities", "cmcurl", "CMakeLists.txt"),
                                "list(APPEND CURL_LIBS ${OPENSSL_LIBRARIES})",
                                "list(APPEND CURL_LIBS ${OPENSSL_LIBRARIES} -ldl -lpthread)")
        self.settings.arch = self.settings.arch_build  # workaround for cross-building to get the correct arch during the build
        cmake = self._configure_cmake()
        cmake.build()

    def package_id(self):
        self.info.include_build_settings()
        del self.info.settings.arch
        del self.info.settings.compiler

    def package(self):
        self.copy("Copyright.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "doc"))

    def package_info(self):
        minor = self._minor_version()

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        self.env_info.CMAKE_ROOT = self.package_folder
        mod_path = os.path.join(self.package_folder, "share", "cmake-%s" % minor, "Modules")
        self.env_info.CMAKE_MODULE_PATH = mod_path
        if not os.path.exists(mod_path):
            raise ConanException("Module path not found: %s" % mod_path)

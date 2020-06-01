import os
from conans import tools, ConanFile, CMake
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration, ConanException


class CMakeConan(ConanFile):
    name = "cmake"
    description = "Conan installer for CMake"
    topics = ("conan", "cmake", "build", "installer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Kitware/CMake"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "build_type"

    _source_subfolder = "source_subfolder"
    _cmake = None

    def _minor_version(self):
        return ".".join(str(self.version).split(".")[:2])

    def configure(self):
        if self.settings.os == "Macos" and self.settings.arch == "x86":
            raise ConanInvalidConfiguration("CMake does not support x86 for macOS")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["CMAKE_BOOTSTRAP"] = False
            if self.settings.os == "Linux":
                self._cmake.definitions["OPENSSL_USE_STATIC_LIBS"] = True
                self._cmake.definitions["CMAKE_EXE_LINKER_FLAGS"] = "-lz"
            self._cmake.configure(source_dir=self._source_subfolder)
        return self._cmake

    def build(self):
        if self.settings.os == "Linux":
            tools.replace_in_file(os.path.join(self._source_subfolder, "Utilities", "cmcurl", "CMakeLists.txt"),
                                  "list(APPEND CURL_LIBS ${OPENSSL_LIBRARIES})",
                                  "list(APPEND CURL_LIBS ${OPENSSL_LIBRARIES} -ldl -lpthread)")
        cmake = self._configure_cmake()
        cmake.build()

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

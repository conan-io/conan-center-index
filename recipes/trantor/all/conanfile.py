import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class TrantorConan(ConanFile):
    name = "trantor"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    homepage = "https://github.com/an-tao/trantor"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Non-blocking I/O TCP network library based on +14/17"
    topics = ("tcp-server", "non-blocking-io", "asynchronous", "networking")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake", "cmake_find_package_multi"
    _cmake = None

    def requirements(self):
        self.requires("openssl/1.1.1h")
        self.requires("c-ares/1.16.1")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC
            compiler_version = Version(self.settings.compiler.version.value)
            if compiler_version < "15":
                raise ConanInvalidConfiguration("On Windows Trantor can only be built with "
                                                "Visual Studio 2017 or higher.")
            if "MT" in self.settings.compiler.runtime and self.options.shared:
                raise ConanInvalidConfiguration(
                    "Trantor can not be built by MSVC and MT runtime as shared library.")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "find_package(c-ares)",
                              "find_package(c-ares REQUIRED)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "target_link_libraries(${PROJECT_NAME} PRIVATE c-ares_lib)",
                              "target_link_libraries(${PROJECT_NAME} PRIVATE c-ares::cares)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "\"${CMAKE_CURRENT_SOURCE_DIR}/cmake_modules/Findc-ares.cmake\"",
                              "#")
        tools.rmdir(os.path.join(self._source_subfolder, "cmake_modules"))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "trantor-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TRANTOR_SHARED"] = self.options.shared
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("License", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Trantor"
        self.cpp_info.names["cmake_find_package_multi"] = "Trantor"
        self.cpp_info.libs = tools.collect_libs(self)

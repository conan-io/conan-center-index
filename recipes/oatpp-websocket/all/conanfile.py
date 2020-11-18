from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.28.0"

class OatppWebSocketConan(ConanFile):
    name = "oatpp-websocket"
    description = "WebSocket functionality for oatpp applications"
    homepage = "https://github.com/oatpp/oatpp-websocket"
    license = "Apache-2.0"
    topics = ("conan", "oat++", "oatpp", "websocket")
    url = "https://github.com/conan-io/conan-center-index"
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "CMakeLists.txt"

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
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("oatpp-websocket can not be built as shared library on Windows")

        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("oatpp-websocket requires GCC >=5")

    def requirements(self):
        # oatpp and oatpp-websocket are tightly coupled so use the same version
        self.requires("oatpp/" + self.version)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("oatpp-websocket-{0}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["OATPP_BUILD_TESTS"] = False
        self._cmake.definitions["OATPP_MODULES_LOCATION"] = "INSTALLED"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "oatpp-websocket"
        self.cpp_info.filenames["cmake_find_package_multi"] = "oatpp-websocket"
        self.cpp_info.names["cmake_find_package"] = "oatpp"
        self.cpp_info.names["cmake_find_package_multi"] = "oatpp"
        self.cpp_info.components["_oatpp-websocket"].names["cmake_find_package"] = "oatpp-websocket"
        self.cpp_info.components["_oatpp-websocket"].names["cmake_find_package_multi"] = "oatpp-websocket"
        self.cpp_info.components["_oatpp-websocket"].includedirs = [
            os.path.join("include", "oatpp-{}".format(self.version), "oatpp-websocket")
        ]
        self.cpp_info.components["_oatpp-websocket"].libdirs = [os.path.join("lib", "oatpp-{}".format(self.version))]
        self.cpp_info.components["_oatpp-websocket"].libs = ["oatpp-websocket"]
        if self.settings.os == "Linux":
            self.cpp_info.components["_oatpp-websocket"].system_libs = ["pthread"]
        self.cpp_info.components["_oatpp-websocket"].requires = ["oatpp::oatpp"]

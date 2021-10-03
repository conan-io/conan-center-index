from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class RestbedConan(ConanFile):
    name = "restbed"
    homepage = "https://github.com/Corvusoft/restbed/"
    description = "Restbed brings asynchronous RESTful functionality to C++14 applications"
    topics = ("restbed", "rest", "restful", "asynchronous", "http")
    url = "https://github.com/conan-io/conan-center-index"
    license = ("CPL", "AGPL")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_ssl": [True, False],
        "build_ipc": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_ssl": True,
        "build_ipc": False
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("asio/1.19.2")
        if self.options.build_ssl:
            self.requires("openssl/1.1.1l")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SSL"] = self.options.build_ssl
        self._cmake.definitions["BUILD_IPC"] = self.options.build_ipc
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "14")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE.CPL", dst="licenses", src=os.path.join(self._source_subfolder, "legal"))
        self.copy("LICENSE.AGPL", dst="licenses", src=os.path.join(self._source_subfolder, "legal"))
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "restbed"
        self.cpp_info.names["pkg_config"] = "restbed"
        self.cpp_info.libs = ["restbed"]

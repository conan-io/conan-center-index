import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class ZmqppConan(ConanFile):
    name = "zmqpp"
    homepage = "https://github.com/zeromq/zmqpp"
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    description = "This C++ binding for 0mq/zmq is a 'high-level' library that hides most of the c-style interface core 0mq provides."
    topics = ("conan", "zmq", "0mq", "zeromq", "message-queue", "asynchronous")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = ["cmake", "cmake_find_package"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def requirements(self):
        self.requires("zeromq/4.3.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("zmqpp-%s" % (self.version), self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def validate(self):
        compiler = self.settings.compiler
        if compiler.get_safe('cppstd'):
            tools.check_min_cppstd(self, 11)
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio compiler is not supported")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ZMQPP_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["ZMQPP_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["ZMQPP_BUILD_EXAMPLES"] = False
        self._cmake.definitions["ZMQPP_BUILD_CLIENT"] = False
        self._cmake.definitions["ZMQPP_BUILD_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libzmqpp"
        self.cpp_info.libs = tools.collect_libs(self)


from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.33.0"


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
    generators = "cmake"
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

    def requirements(self):
        self.requires("zeromq/4.3.4")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ZMQPP_LIBZMQ_CMAKE"] = False
        self._cmake.definitions["ZMQPP_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["ZMQPP_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["ZMQPP_BUILD_EXAMPLES"] = False
        self._cmake.definitions["ZMQPP_BUILD_CLIENT"] = False
        self._cmake.definitions["ZMQPP_BUILD_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libzmqpp"
        self.cpp_info.libs = ["zmqpp" if self.options.shared else "zmqpp-static"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]

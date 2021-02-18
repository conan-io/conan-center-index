import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class ZmqppConan(ConanFile):
    name = "zmqpp"
    homepage = "https://github.com/zeromq/zmqpp"
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    description = "This C++ binding for 0mq/zmq is a 'high-level' library that hides most of the c-style interface core 0mq provides."
    topics = ("conan", "zmq", "0mq", "ZeroMQ", "message-queue", "asynchronous")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"

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
        self.requires("libsodium/1.0.18")
        self.requires("zeromq/4.3.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("zmqpp-%s" % (self.version), self._source_subfolder)
        cmakeFile = os.path.join(self._source_subfolder, "CMakeLists.txt")
        if self.options.shared == "False": # zmqpp uses different name for static library
            tools.replace_in_file(cmakeFile, "generate_export_header(zmqpp)", "generate_export_header(zmqpp-static)")
            tools.replace_in_file(cmakeFile, "${CMAKE_CURRENT_BINARY_DIR}/zmqpp_export.h", "${CMAKE_CURRENT_BINARY_DIR}/zmqpp-static_export.h")
        else:
            tools.replace_in_file(cmakeFile, "set( LIB_TO_LINK_TO_EXAMPLES zmqpp )", "set( LIB_TO_LINK_TO_EXAMPLES zmqpp )\n"
                                                          "target_link_libraries(zmqpp sodium)")
            tools.replace_in_file(cmakeFile, "enable_testing()", "enable_testing()\n"
                                                           "find_package(libsodium REQUIRED)")
        #
#         os.rename("Findlibsodium.cmake", "FindSodium.cmake")
#         tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
#                                        "SODIUM_FOUND",
#                                        "libsodium_FOUND")
#         tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
#                                        "SODIUM_INCLUDE_DIRS",
#                                        "libsodium_INCLUDE_DIRS")
#         tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
#                                        "SODIUM_LIBRARIES",
#                                        "libsodium_LIBRARIES")

    def validate(self):
        compiler = self.settings.compiler
        if compiler.get_safe('cppstd'):
            tools.check_min_cppstd(self, 11)

        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio compiler is not supported")
        
        # libstdc++11 is required
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration("libstdc++11 required")
        if self.settings.compiler == "gcc" and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration("libstdc++11 required")

    def build(self):
        self.cmake = CMake(self)
        self.cmake.verbose = True
        self.cmake.definitions["ZMQPP_BUILD_SHARED"] = self.options.shared
        self.cmake.definitions["ZMQPP_BUILD_STATIC"] = not self.options.shared
#       self.cmake.definitions["BUILD_SHARED"] = self.options.shared
#       self.cmake.definitions["BUILD_STATIC"] = not self.options.shared
#        if not self.options.shared:
#            self.cmake.definitions["ZMQ_STATIC"] = False
        self.cmake.configure(build_folder=self._build_subfolder)
        #self.cmake.configure()
        self.cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.cmake.configure()
        self.cmake.install()

    def package_info(self):
        #self.cpp_info.libs = ["zmqpp"]
        self.cpp_info.names["cmake_find_package"] = "zmqpp"
        self.cpp_info.names["cmake_find_package_multi"] = "zmqpp"
        self.cpp_info.names["pkg_config"] = "libzmqpp"
        libzmq_target = "libzmqpp" # if self.options.shared else "libzmqpp-static"
        self.cpp_info.components[libzmq_target].names["cmake_find_package"] = libzmq_target
        self.cpp_info.components[libzmq_target].names["cmake_find_package_multi"] = libzmq_target
        self.cpp_info.components[libzmq_target].libs = tools.collect_libs(self)
        self.cpp_info.components[libzmq_target].requires = ["libsodium::libsodium", "zeromq::zeromq"]

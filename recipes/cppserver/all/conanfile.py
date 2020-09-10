from conans import ConanFile, CMake, tools
import os
import glob


class CppServer(ConanFile):
    name = "cppserver"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/chronoxor/CppServer"
    description = "Ultra fast and low latency asynchronous socket server and" \
        " client C++ library with support TCP, SSL, UDP, HTTP, HTTPS, WebSocket" \
        " protocols and 10K connections problem solution."
    topics = ("network", "socket", "async", "low-latency")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False}
    requires = ["asio/1.17.0", "openssl/1.1.1g", "cppcommon/cci.20201104"]
    generators = "cmake", "cmake_find_package"
    exports_sources = ["patches/**", "CMakeLists.txt"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["CPPSERVER_MODULE"] = "OFF"
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("CppServer-*")[0]
        import time
        time.sleep(30)
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build(self):
        patches = self.conan_data["patches"][self.version]
        for patch in patches:
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy(pattern="*.inl", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "crypt32", "mswsock"]
            self.cpp_info.defines.extend(
                ["_WIN32_WINNT=_WIN32_WINNT_WIN7",
                "_WINSOCK_DEPRECATED_NO_WARNINGS",
                "_SILENCE_CXX17_ALLOCATOR_VOID_DEPRECATION_WARNING"])

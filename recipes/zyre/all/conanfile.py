from conans import ConanFile, CMake, tools
import os


class ZyreConan(ConanFile):
    name = "zyre"
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zeromq/zyre"
    description = "Local Area Clustering for Peer-to-Peer Applications."
    topics = ("conan", "zyre", "czmq", "zmq", "zeromq",
              "message-queue", "asynchronous")
    exports_sources = "CMakeLists.txt", "patches/**"
    settings = "os", "compiler", "build_type", "arch"
    requires = "zeromq/4.3.2", "czmq/4.2.0"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "drafts": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "drafts": False,
    }
    generators = ["cmake", "cmake_find_package"]
    _cmake = None
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.verbose = True
        self._cmake.definitions["ENABLE_DRAFTS"] = self.options.drafts
        self._cmake.configure(build_dir=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder,
                  dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["zyre"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "dl", "rt", "m"]
        if not self.options.shared:
            self.cpp_info.defines = ["ZYRE_STATIC"]

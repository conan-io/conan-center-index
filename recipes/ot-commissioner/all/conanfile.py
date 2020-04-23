import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class OtCommissionerConan(ConanFile):
    name = "ot-commissioner"
    description = "OpenThread Commissioner, a Thread commissioner for joining new Thread devices and managing Thread networks."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://giþthub.com/openthread/ot-commissioner"
    topics = ("conan", "thread", "commissioning")
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("libevent/2.1.11")
        self.requires("mdns/20200331")
        self.requires("nlohmann_json/3.7.3")
        self.requires("mbedtls/2.16.3-gpl")
        self.requires("fmt/6.1.2")
        # TODO: port to CCI
        self.requires("cose-c/20200225@gocarlos/testing")
        self.requires("cn-cbor/1.0.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        # extracted_dir = self.name + "-" + self.version
        extracted_dir = self.name + "-" + os.path.basename(self.conan_data["sources"][self.version]["url"]).split(".")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["OT_COMM_USE_VENDORED_LIBS"] = False
        self._cmake.definitions["OT_COMM_TEST"] = False
        self._cmake.definitions["OT_COMM_APP"] = False
        self._cmake.definitions["OT_COMM_COVERAGE"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "spdlog", "cmake"))

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]

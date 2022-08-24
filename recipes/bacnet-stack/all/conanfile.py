import os
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration


class BacnetStackConan(ConanFile):
    name = "bacnet-stack"
    license = "GPL-2.0-or-later"
    homepage = "https://github.com/bacnet-stack/bacnet-stack/"
    url = "https://github.com/conan-io/conan-center-index"
    description = """
        BACnet Protocol Stack library provides a BACnet application layer,
        network layer and media access (MAC) layer communications services."""
    topics = ("bacnet")
    exports_sources = ['CMakeLists.txt']
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    generators = "cmake", "cmake_find_package"

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Windows shared builds are not supported right now, see issue https://github.com/bacnet-stack/bacnet-stack/issues/49")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        if self.version.startswith("2020"):
            extracted_dir = self.name + "-" + os.path.basename(self.conan_data["sources"][self.version]["url"]).split(".")[0]
        else:
            extracted_dir = self.name + "-" + self.name + "-" + self.version

        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BACNET_STACK_BUILD_APPS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("gpl-2.txt", dst='licenses', src=os.path.join(self._source_subfolder, "license"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder,
                                 "lib", "bacnet-stack", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["bacnet-stack"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
        if not self.options.shared:
            self.cpp_info.defines = ["BACNET_STACK_STATIC_DEFINE"]

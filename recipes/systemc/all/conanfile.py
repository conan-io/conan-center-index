from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.28.0"


class SystemcConan(ConanFile):
    name = "systemc"
    version = "2.3.3"
    description = """SystemC is a set of C++ classes and macros which provide
                     an event-driven simulation interface."""
    homepage = "https://www.accellera.org/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    topics = ("simulation", "modeling", "esl", "tlm")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_async_updates": [True, False],
        "disable_copyright_msg": [True, False],
        "disable_virtual_bind": [True, False],
        "enable_assertions": [True, False],
        "enable_immediate_self_notifications": [True, False],
        "enable_pthreads": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_async_updates": False,
        "disable_copyright_msg": False,
        "disable_virtual_bind":  False,
        "enable_assertions": True,
        "enable_immediate_self_notifications": False,
        "enable_pthreads": False,
    }

    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.enable_pthreads

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("Macos build not supported")

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Building SystemC as a shared library on Windows is currently not supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["DISABLE_ASYNC_UPDATES"] = \
            self.options.disable_async_updates
        cmake.definitions["DISABLE_COPYRIGHT_MESSAGE"] = \
            self.options.disable_copyright_msg
        cmake.definitions["DISABLE_VIRTUAL_BIND"] = \
            self.options.disable_virtual_bind
        cmake.definitions["ENABLE_ASSERTIONS"] = \
            self.options.enable_assertions
        cmake.definitions["ENABLE_IMMEDIATE_SELF_NOTIFICATIONS"] = \
            self.options.enable_immediate_self_notifications
        cmake.definitions["ENABLE_PTHREADS"] = \
            self.options.get_safe("enable_pthreads", False)
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("NOTICE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "SystemCLanguage"
        self.cpp_info.filenames["cmake_find_package_multi"] = "SystemCLanguage"
        self.cpp_info.names["cmake_find_package"] = "SystemC"
        self.cpp_info.names["cmake_find_package_multi"] = "SystemC"
        self.cpp_info.components["_systemc"].names["cmake_find_package"] = "systemc"
        self.cpp_info.components["_systemc"].names["cmake_find_package_multi"] = "systemc"
        self.cpp_info.components["_systemc"].libs = ["systemc"]
        if self.settings.os == "Linux":
            self.cpp_info.components["_systemc"].system_libs = ["pthread"]
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.components["_systemc"].cxxflags.append("/vmg")

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class SystemcConan(ConanFile):
    name = "systemc"
    version = "2.3.3"
    description = """SystemC is a set of C++ classes and macros which provide
                     an event-driven simulation interface."""
    homepage = "https://www.accellera.org/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    topics = ("simulation", "modeling", "esl", "tlm")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_async_updates": [True, False],
        "disable_copyright_msg": [True, False],
        "disable_virtual_bind": [True, False],
        "enable_assertions": [True, False],
        "enable_immediate_self_notifications": [True, False],
        "enable_pthreads": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_async_updates": False,
        "disable_copyright_msg": False,
        "disable_virtual_bind":  False,
        "enable_assertions": True,
        "enable_immediate_self_notifications": False,
        "enable_pthreads": False
    }
    generators = "cmake"
    exports_sources = "patches/**"

    _cmake = None

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

        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("Macos build not supported")

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("The compilation of SystemC as a "
                                            "DLL on Windows is currently not "
                                            "supported")

        if tools.valid_min_cppstd(self, "17"):
            raise ConanInvalidConfiguration(
                "C++ Standard %s not supported by SystemC" %
                self.settings.compiler.cppstd)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("systemc-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):

        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["DISABLE_ASYNC_UPDATES"] = \
            self.options.disable_async_updates
        self._cmake.definitions["DISABLE_COPYRIGHT_MESSAGE"] = \
            self.options.disable_copyright_msg
        self._cmake.definitions["DISABLE_VIRTUAL_BIND"] = \
            self.options.disable_virtual_bind
        self._cmake.definitions["ENABLE_ASSERTIONS"] = \
            self.options.enable_assertions
        self._cmake.definitions["ENABLE_IMMEDIATE_SELF_NOTIFICATIONS"] = \
            self.options.enable_immediate_self_notifications
        self._cmake.definitions["ENABLE_PTHREADS"] = \
            self.options.get_safe("enable_pthreads", False)
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("NOTICE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["systemc"]
        # FIXME: cmake generates SystemC::systemc target, not SystemC::SystemC
        self.cpp_info.names["cmake_find_package"] = "SystemC"
        self.cpp_info.names["cmake_find_package_multi"] = "SystemC"

        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]

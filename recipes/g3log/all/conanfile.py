import os
from os import path
from conan import ConanFile, tools
from conans import CMake
from conans.tools import Version
from conan.errors import ConanInvalidConfiguration


class G3logConan(ConanFile):
    name = "g3log"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KjellKod/g3log"
    license = "The Unlicense"
    description = """G3log is an asynchronous, "crash safe", logger that is easy to use with default logging sinks or you can add your own."""
    topics = ("conan", "g3log", "log")
    settings = "os", "compiler", "build_type", "arch"
    options = {
      "shared": [True, False],
      "fPIC": [True, False],
      "use_dynamic_logging_levels": [True, False],
      "change_debug_to_dbug": [True, False],
      "use_dynamic_max_message_size": [True, False],
      "log_full_filename": [True, False],
      "enable_fatal_signal_handling": [True, False],
      "enable_vectored_exception_handling": [True, False],
      "debug_break_at_fatal_signal": [True, False]
    }
    default_options = {key: False for key in options.keys()}
    default_options["use_dynamic_max_message_size"] = True
    default_options["enable_fatal_signal_handling"] = True
    default_options["enable_vectored_exception_handling"] = True
    default_options["fPIC"] = True
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    _source_subfolder = "source_subfolder"

    def _has_support_for_cpp14(self):
        supported_compilers = [("apple-clang", 5.1), ("clang", 3.4), ("gcc", 6.1), ("Visual Studio", 15.0)]
        compiler, version = self.settings.compiler, Version(self.settings.compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "14")
        if not self._has_support_for_cpp14():
            raise ConanInvalidConfiguration("g3log requires C++14 or higher support standard."
                                            " {} {} is not supported."
                                            .format(self.settings.compiler,
                                                    self.settings.compiler.version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        dir_postfix = self.conan_data["sources"][self.version]["url"].split("/")[-1][:-7]
        os.rename("g3log-{}".format(dir_postfix), self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler != "Visual Studio":
            del self.options.enable_vectored_exception_handling
            del self.options.debug_break_at_fatal_signal

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['VERSION'] = self.version
        cmake.definitions["G3_SHARED_LIB"] = self.options.shared
        cmake.definitions["USE_DYNAMIC_LOGGING_LEVELS"] = self.options.use_dynamic_logging_levels
        cmake.definitions["CHANGE_G3LOG_DEBUG_TO_DBUG"] = self.options.change_debug_to_dbug
        cmake.definitions["USE_G3_DYNAMIC_MAX_MESSAGE_SIZE"] = self.options.use_dynamic_max_message_size
        cmake.definitions["G3_LOG_FULL_FILENAME"] = self.options.log_full_filename
        cmake.definitions["ENABLE_FATAL_SIGNALHANDLING"] = self.options.enable_fatal_signal_handling
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["ENABLE_VECTORED_EXCEPTIONHANDLING"] = self.options.enable_vectored_exception_handling
            cmake.definitions["DEBUG_BREAK_AT_FATAL_SIGNAL"] = self.options.debug_break_at_fatal_signal
        cmake.definitions["ADD_FATAL_EXAMPLE"] = "OFF"
        cmake.definitions["ADD_G3LOG_PERFORMANCE"] = "OFF"
        cmake.definitions["ADD_G3LOG_UNIT_TEST"] = "OFF"
        cmake.configure()
        return cmake

    def build(self):
        if "patches" in self.conan_data and self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["g3logger"]
        if str(self.settings.os) in ["Linux", "Android"]:
            self.cpp_info.system_libs.append('pthread')

import os
from os import path
from conans import ConanFile, CMake, tools


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
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        dir_postfix = self.conan_data["sources"][self.version]["url"].split("/")[-1][:-7]
        os.rename("g3log-{}".format(dir_postfix), self._source_subfolder)

    def config_options(self):
        if self.settings.compiler != "Visual Studio":
            del self.options.enable_vectored_exception_handling
            del self.options.debug_break_at_fatal_signal

    def _configure_cmake(self):
        cmake = CMake(self)
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
        if self.settings.os == "Windows":
            self.copy("g3logger.lib", dst="lib", src="lib")
            self.copy("g3logger.dll", dst="bin", src="bin")
            self.copy("g3logrotate.lib", dst="lib", src="lib")
        elif self.settings.os == "Linux":
            if self.options.shared:
                self.copy("libg3logger.so*", dst="lib", src="lib", symlinks=True)
            else:
                self.copy("libg3logger.a", dst="lib", src="lib")
        if self.version == "20170108":
            self.copy("g3log/*.hpp", dst="include", src="include")  # generated_definitions.hpp
        else:
            self.copy("g3log/*.hpp", dst="include", src=path.join(self._source_subfolder, 'include'))  # generated_definitions.hpp
        self.copy("g3log/*.hpp", dst="include", src=path.join(self._source_subfolder, 'src'))

    def package_info(self):
        self.cpp_info.libs = ["g3logger"]
        if str(self.settings.os) in ["Linux", "Android"]:
            self.cpp_info.libs.append('pthread')

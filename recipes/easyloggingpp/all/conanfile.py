import os
from conan import ConanFile, tools
from conan.tools.cmake import CMake


required_conan_version = ">=1.33.0"

class EasyloggingppConan(ConanFile):
    name = "easyloggingpp"
    license = "The MIT License (MIT)"
    homepage = "https://github.com/amrayn/easyloggingpp"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Single header C++ logging library."
    topics = ("logging", "stacktrace", "efficient-logging")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = "CMakeLists.txt",
    options = {
        "enable_crash_log": [True, False],
        "enable_thread_safe": [True, False],
        "enable_debug_errors": [True, False],
        "enable_default_logfile": [True, False],
    }
    default_options = {
        "enable_crash_log": False,
        "enable_thread_safe": False,
        "enable_debug_errors": False,
        "enable_default_logfile": True,
    }
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["build_static_lib"] = True
        self._cmake.definitions["enable_crash_log"] = self.options.enable_crash_log
        self._cmake.definitions["enable_thread_safe"] = self.options.enable_thread_safe
        self._cmake.definitions["enable_debug_errors"] = self.options.enable_debug_errors
        self._cmake.definitions["enable_default_logfile"] = self.options.enable_default_logfile
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        self.copy(pattern="LICENSE",
                  dst="licenses",
                  src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "easyloggingpp"
        self.cpp_info.names["cmake_find_package_multi"] = "easyloggingpp"
        self.cpp_info.libs = ["easyloggingpp"]
        if self.options.enable_crash_log:
            self.cpp_info.defines.append("ELPP_FEATURE_CRASH_LOG")
        if self.options.enable_thread_safe:
            self.cpp_info.defines.append("ELPP_THREAD_SAFE")
        if self.options.enable_debug_errors:
            self.cpp_info.defines.append("ELPP_DEBUG_ERRORS")
        if self.options.enable_default_logfile:
            self.cpp_info.defines.append("ELPP_NO_DEFAULT_LOG_FILE")

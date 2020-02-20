import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class SpdlogConan(ConanFile):
    name = "spdlog"
    description = "Fast C++ logging library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gabime/spdlog"
    topics = ("conan", "spdlog", "logging", "header-only")
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "header_only": [True, False],
               "wchar_support": [True, False],
               "wchar_filenames": [True, False],
               "no_exceptions": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "header_only": False,
                       "wchar_support": False,
                       "wchar_filenames": False,
                       "no_exceptions": False}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            del self.options.shared
            del self.options.fPIC
        elif self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("spdlog shared lib is not yet supported under windows")
        if self.settings.os != "Windows" and \
           (self.options.wchar_support or self.options.wchar_filenames):
            raise ConanInvalidConfiguration("wchar is not yet supported under windows")

    def requirements(self):
        self.requires("fmt/6.1.2") 

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SPDLOG_BUILD_EXAMPLE"] = False
        cmake.definitions["SPDLOG_BUILD_EXAMPLE_HO"] = False
        cmake.definitions["SPDLOG_BUILD_TESTS"] = False
        cmake.definitions["SPDLOG_BUILD_TESTS_HO"] = False
        cmake.definitions["SPDLOG_BUILD_BENCH"] = False
        cmake.definitions["SPDLOG_FMT_EXTERNAL"] = True
        cmake.definitions["SPDLOG_BUILD_SHARED"] = not self.options.header_only and self.options.shared
        cmake.definitions["SPDLOG_WCHAR_SUPPORT"] = self.options.wchar_support
        cmake.definitions["SPDLOG_WCHAR_FILENAMES"] = self.options.wchar_filenames
        cmake.definitions["SPDLOG_INSTALL"] = True
        cmake.definitions["SPDLOG_NO_EXCEPTIONS"] = self.options.no_exceptions
        cmake.configure()
        return cmake

    def _disable_werror(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "utils.cmake"), "/WX", "")

    def build(self):
        self._disable_werror()
        if self.options.header_only:
            tools.patch(**self.conan_data["patches"][self.version])
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst='licenses', src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "spdlog", "cmake"))

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    def package_info(self):
        if self.options.header_only:
            self.cpp_info.defines = ["SPDLOG_HEADER_ONLY", "SPDLOG_FMT_EXTERNAL"]
        else:
            self.cpp_info.libs = tools.collect_libs(self)
            self.cpp_info.defines = ["SPDLOG_COMPILED_LIB", "SPDLOG_FMT_EXTERNAL"]
        if self.options.wchar_support:
            self.cpp_info.defines.append("SPDLOG_WCHAR_TO_UTF8_SUPPORT")
        if self.options.wchar_filenames:
            self.cpp_info.defines.append("SPDLOG_WCHAR_FILENAMES")
        if self.options.no_exceptions:
            self.cpp_info.defines.append("SPDLOG_NO_EXCEPTIONS")
        if tools.os_info.is_linux:
            self.cpp_info.libs.append("pthread")

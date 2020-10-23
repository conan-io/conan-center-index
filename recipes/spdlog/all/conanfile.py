import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class SpdlogConan(ConanFile):
    name = "spdlog"
    description = "Fast C++ logging library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gabime/spdlog"
    topics = ("conan", "spdlog", "logging", "header-only")
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
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

    _cmake = None

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
        elif self.settings.os == "Windows" and self.options.shared and Version(self.version) < "1.6.0":
            raise ConanInvalidConfiguration("spdlog shared lib is not yet supported under windows")
        if self.settings.os != "Windows" and \
           (self.options.wchar_support or self.options.wchar_filenames):
            raise ConanInvalidConfiguration("wchar is not yet supported under windows")

    def requirements(self):
        if Version(self.version) >= "1.7.0":
            self.requires("fmt/7.0.3")
        elif Version(self.version) >= "1.5.0":
            self.requires("fmt/6.2.0")
        else:
            self.requires("fmt/6.0.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SPDLOG_BUILD_EXAMPLE"] = False
        self._cmake.definitions["SPDLOG_BUILD_EXAMPLE_HO"] = False
        self._cmake.definitions["SPDLOG_BUILD_TESTS"] = False
        self._cmake.definitions["SPDLOG_BUILD_TESTS_HO"] = False
        self._cmake.definitions["SPDLOG_BUILD_BENCH"] = False
        self._cmake.definitions["SPDLOG_FMT_EXTERNAL"] = True
        self._cmake.definitions["SPDLOG_FMT_EXTERNAL_HO"] = self.options["fmt"].header_only
        self._cmake.definitions["SPDLOG_BUILD_SHARED"] = not self.options.header_only and self.options.shared
        self._cmake.definitions["SPDLOG_WCHAR_SUPPORT"] = self.options.wchar_support
        self._cmake.definitions["SPDLOG_WCHAR_FILENAMES"] = self.options.wchar_filenames
        self._cmake.definitions["SPDLOG_INSTALL"] = True
        self._cmake.definitions["SPDLOG_NO_EXCEPTIONS"] = self.options.no_exceptions
        if self.settings.os in ("iOS", "tvOS", "watchOS"):
            self._cmake.definitions["SPDLOG_NO_TLS"] = True
        self._cmake.configure()
        return self._cmake

    def _disable_werror(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "utils.cmake"), "/WX", "")

    def build(self):
        if Version(self.version) < "1.7" and Version(self.deps_cpp_info["fmt"].version) >= 7:
            raise ConanInvalidConfiguration("The project {}/{} requires fmt < 7.x".format(self.name, self.version))

        self._disable_werror()
        if not self.options.header_only:
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if self.options.header_only:
            self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        else:
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
            component_name = "spdlog_header_only"
        else:
            component_name = "libspdlog"
            self.cpp_info.components["libspdlog"].libs = tools.collect_libs(self)
            self.cpp_info.components["libspdlog"].defines.append("SPDLOG_COMPILED_LIB")

        self.cpp_info.components[component_name].defines.append("SPDLOG_FMT_EXTERNAL")
        if self.options["fmt"].header_only:
            self.cpp_info.components[component_name].requires = ["fmt::fmt-header-only"]
        else:
            self.cpp_info.components[component_name].requires = ["fmt::fmt"]
        if self.options.wchar_support:
            self.cpp_info.components[component_name].defines.append("SPDLOG_WCHAR_TO_UTF8_SUPPORT")
        if self.options.wchar_filenames:
            self.cpp_info.components[component_name].defines.append("SPDLOG_WCHAR_FILENAMES")
        if self.options.no_exceptions:
            self.cpp_info.components[component_name].defines.append("SPDLOG_NO_EXCEPTIONS")
        if self.settings.os == "Linux":
            self.cpp_info.components[component_name].system_libs = ["pthread"]

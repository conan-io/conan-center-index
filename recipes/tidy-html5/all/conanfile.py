import os
from conans import ConanFile, CMake, tools


class TidyHtml5Conan(ConanFile):
    name = "tidy-html5"
    license = "W3C"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.html-tidy.org"
    description = "The granddaddy of HTML tools, with support for modern standards"
    topics = ("html", "parser", "xml", "tools")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "support_localizations": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "support_localizations": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake",
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = CMake(self)
        cmake.definitions['BUILD_TAB2SPACE'] = False
        cmake.definitions['BUILD_SAMPLE_CODE'] = False
        cmake.definitions['TIDY_COMPAT_HEADERS'] = False
        cmake.definitions['SUPPORT_CONSOLE_APP'] = False
        cmake.definitions['SUPPORT_LOCALIZATIONS'] = self.options.support_localizations
        cmake.definitions['ENABLE_DEBUG_LOG'] = False
        cmake.definitions['ENABLE_ALLOC_DEBUG'] = False
        cmake.definitions['ENABLE_MEMORY_DEBUG'] = False
        cmake.definitions['BUILD_SHARED_LIB'] = self.options.shared
        cmake.configure(build_folder=self._build_subfolder)
        self._cmake = cmake
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE.md", dst="licenses", src=os.path.join(self._source_subfolder, 'README'))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.a")

    def package_info(self):
        #FIXME: tidy does not install under a CMake namespace
        self.cpp_info.names["cmake_find_package"] = "tidy"
        self.cpp_info.names["cmake_find_package_multi"] = "tidy"
        self.cpp_info.names["pkg_config"] = "tidy"

        suffix = 'd' if self.settings.compiler == 'Visual Studio' and self.settings.build_type == 'Debug' else ''
        if self.options.shared:
            self.cpp_info.components["tidy-share"].names["cmake_find_package"] = "tidy-share"
            self.cpp_info.components["tidy-share"].names["cmake_find_package_multi"] = "tidy-share"
            self.cpp_info.components["tidy-share"].libs = ["tidy" + suffix]
        else:
            self.cpp_info.components["tidy-static"].names["cmake_find_package"] = "tidy-static"
            self.cpp_info.components["tidy-static"].names["cmake_find_package_multi"] = "tidy-static"
            self.cpp_info.components["tidy-static"].libs = ["tidys" + suffix]
            self.cpp_info.components["tidy-static"].defines.append('TIDY_STATIC')

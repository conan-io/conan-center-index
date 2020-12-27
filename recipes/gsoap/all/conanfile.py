from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class GSoapConan(ConanFile):
    name = "gsoap"
    description = "The gSOAP toolkit is a C and C++ software development toolkit for SOAP and " \
                  "REST XML Web services and generic C/C++ XML data bindings."
    topics = ("conan", "gsoap", "logging")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/gsoap2"
    license = ("gSOAP-1.3b", "GPL-2.0-or-later")
    exports_sources = ["CMakeLists.txt", "src/*.cmake", "src/*.txt"]
    generators = "cmake"
    short_paths = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "tools": [True, False],
        "with_openssl": [True, False],
        "with_ipv6": [True, False],
        "with_cookies": [True, False],
        "with_c_locale": [True, False],
    }
    default_options = {
        "fPIC": True,
        "tools": True,
        "with_openssl": True,
        "with_ipv6": True,
        "with_cookies": True,
        "with_c_locale": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.cross_building(self.settings):
            self.options.tools = False

    def configure(self):
        if tools.cross_building(self.settings) and self.options.tools:
            raise ConanInvalidConfiguration("Cannot build tools when cross building")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "gsoap-" + self.version[:self.version.rindex(".")]
        os.rename(extracted_dir, self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows:
            self.build_requires("winflexbison/2.5.22")
        else:
            self.build_requires("bison/3.5.3")
            self.build_requires("flex/2.6.4")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1i")
            self.requires("zlib/1.2.11")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["GSOAP_PATH"] = self._source_subfolder
        self._cmake.definitions["BUILD_TOOLS"] = self.options.tools
        self._cmake.definitions["WITH_OPENSSL"] = self.options.with_openssl
        self._cmake.definitions["WITH_IPV6"] = self.options.with_ipv6
        self._cmake.definitions["WITH_COOKIES"] = self.options.with_cookies
        self._cmake.definitions["WITH_C_LOCALE"] = self.options.with_c_locale
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        # FIXME: use autotools build system instead of custom cmake scripts (the cmake scripts are not building a lot of libraries gsoap, gsoap++, gsoapssl, gsoapssl++, gsoapck, gsoapck++)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="GPLv2_license.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        if self.options.with_ipv6:
            self.cpp_info.components["libgsoap"].defines.append("WITH_IPV6")
        if self.options.with_cookies:
            self.cpp_info.components["libgsoap"].defines.append("WITH_COOKIES")
        if self.options.with_c_locale:
            self.cpp_info.components["libgsoap"].defines.append("WITH_C_LOCALE")

        if self.options.with_openssl:
            self.cpp_info.components["gsoapssl++"].libs = ["gsoapssl++"]
            self.cpp_info.components["gsoapssl++"].names["pkg_config"] = ["gsoap++"]
            self.cpp_info.components["gsoapssl++"].requires = ["openssl::openssl", "zlib::zlib"]
            self.cpp_info.components["gsoapssl++"].defines.extend(["WITH_OPENSSL", "WITH_GZIP"])
        else:
            self.cpp_info.components["gsoap++"].libs = ["gsoap++"]
            self.cpp_info.components["gsoap++"].names["pkg_config"] = "gsoap++"

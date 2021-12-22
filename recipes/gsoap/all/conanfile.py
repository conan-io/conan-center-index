from conans import ConanFile, CMake, tools
import os, shutil


class ConanFileDefault(ConanFile):
    name = "gsoap"
    description = "The gSOAP toolkit is a C and C++ software development toolkit for SOAP and " \
                  "REST XML Web services and generic C/C++ XML data bindings."
    topics = ("conan", "gsoap", "logging")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/gsoap2"
    license = ("gSOAP-1.3b", "GPL-2.0-or-later")
    exports_sources = ["CMakeLists.txt", "src/*.cmake", "src/*.txt"]
    generators = "cmake", "cmake_find_package"
    short_paths = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    settings = "os", "arch", "compiler", "build_type"
    options = {"with_openssl": [True, False],
               "with_ipv6": [True, False],
               "with_cookies": [True, False],
               "with_c_locale": [True, False]}
    default_options = {
        'with_openssl': True,
        'with_ipv6': True,
        'with_cookies': True,
        'with_c_locale': True}


    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def build_requirements(self):
        if tools.cross_building(self, skip_x64_x86=True) and hasattr(self, 'settings_build'):
            self.build_requires("gsoap/{}".format(self.version))

        if hasattr(self, "settings_build") and self.settings_build.os == "Windows":
            self.build_requires("winflexbison/2.5.24")
        else:
            self.build_requires("bison/3.7.6")
            self.build_requires("flex/2.6.4")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1l")
            self.requires("zlib/1.2.11")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["GSOAP_PATH"] = self._source_subfolder
        self._cmake.definitions["BUILD_TOOLS"] = True
        self._cmake.definitions["WITH_OPENSSL"] = self.options.with_openssl
        self._cmake.definitions["WITH_IPV6"] = self.options.with_ipv6
        self._cmake.definitions["WITH_COOKIES"] = self.options.with_cookies
        self._cmake.definitions["WITH_C_LOCALE"] = self.options.with_c_locale
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package_info(self):
        defines = []
        if self.options.with_openssl:
            libs = ["gsoapssl++", ]
            defines.append("WITH_OPENSSL")
            defines.append("WITH_GZIP")
        else:
            libs = ["gsoap++", ]
        self.cpp_info.libs = libs

        if self.options.with_ipv6:
            defines.append("WITH_IPV6")
        if self.options.with_cookies:
            defines.append("WITH_COOKIES")
        if self.options.with_c_locale:
            defines.append("WITH_C_LOCALE")
        self.cpp_info.defines = defines

    def package(self):
        self.copy(pattern="GPLv2_license.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        shutil.move(os.path.join(self.package_folder, 'import'), os.path.join(self.package_folder, 'bin', 'import'))

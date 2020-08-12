from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.28.0"

class LibeventConan(ConanFile):
    name = "libevent"
    description = "libevent - an event notification library"
    topics = ("conan", "libevent", "event")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libevent/libevent"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_openssl": [True, False],
               "disable_threads": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_openssl": True,
                       "disable_threads": False}
    generators = "cmake", "cmake_find_package"
    short_paths = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1g")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        # temporary fix due to missing files in dist package for 2.1.11, see upstream bug 863
        # for other versions "libevent-{0}-stable".format(self.version) is enough
        extracted_folder = "libevent-release-{0}-stable".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "OPENSSL_INCLUDE_DIR",
                              "OpenSSL_INCLUDE_DIRS")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "OPENSSL_LIBRARIES",
                              "OpenSSL_LIBRARIES")
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.options.with_openssl:
            self._cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath
        self._cmake.definitions["EVENT__LIBRARY_TYPE"] = "SHARED" if self.options.shared else "STATIC"
        self._cmake.definitions["EVENT__DISABLE_DEBUG_MODE"] = self.settings.build_type == "Release"
        self._cmake.definitions["EVENT__DISABLE_OPENSSL"] = not self.options.with_openssl
        self._cmake.definitions["EVENT__DISABLE_THREAD_SUPPORT"] = self.options.disable_threads
        self._cmake.definitions["EVENT__DISABLE_BENCHMARK"] = True
        self._cmake.definitions["EVENT__DISABLE_TESTS"] = True
        self._cmake.definitions["EVENT__DISABLE_REGRESS"] = True
        self._cmake.definitions["EVENT__DISABLE_SAMPLES"] = True
        # libevent uses static runtime (MT) for static builds by default
        self._cmake.definitions["EVENT__MSVC_STATIC_RUNTIME"] = self.settings.compiler == "Visual Studio" and \
                self.settings.compiler.runtime == "MT"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        # drop pc and cmake file
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "Libevent"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Libevent"
        self.cpp_info.names["cmake_find_package"] = "libevent"
        self.cpp_info.names["cmake_find_package_multi"] = "libevent"
        # core
        self.cpp_info.components["core"].names["pkg_config"] = "libevent_core"
        self.cpp_info.components["core"].libs = ["event_core"]
        if self.settings.os == "Linux" and not self.options.disable_threads:
            self.cpp_info.components["core"].system_libs = ["pthread"]
        if self.settings.os == "Windows":
            self.cpp_info.components["core"].system_libs = ["ws2_32", "advapi32", "iphlpapi"]
        # extra
        self.cpp_info.components["extra"].names["pkg_config"] = "libevent_extra"
        self.cpp_info.components["extra"].libs = ["event_extra"]
        if self.settings.os == "Windows":
            self.cpp_info.components["extra"].system_libs = ["shell32"]
        self.cpp_info.components["extra"].requires = ["core"]
        # openssl
        if self.options.with_openssl:
            self.cpp_info.components["openssl"].names["pkg_config"] = "libevent_openssl"
            self.cpp_info.components["openssl"].libs = ["event_openssl"]
            self.cpp_info.components["openssl"].requires = ["core", "openssl::openssl"]
        # pthreads
        if self.settings.os != "Windows" and not self.options.disable_threads:
            self.cpp_info.components["pthreads"].names["pkg_config"] = "libevent_pthreads"
            self.cpp_info.components["pthreads"].libs = ["event_pthreads"]
            self.cpp_info.components["pthreads"].requires = ["core"]

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class Nghttp2Conan(ConanFile):
    name = "libnghttp2"
    description = "HTTP/2 C Library and tools"
    topics = ("conan", "http")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nghttp2.org"
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "pkg_config"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_app": [True, False],
               "with_hpack": [True, False],
               "with_jemalloc": [True, False],
               "with_asio": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_app": True,
                       "with_hpack": True,
                       "with_jemalloc": False,
                       "with_asio": False}

    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.with_asio and self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Build with asio and MSVC is not supported yet, see upstream bug #589")
        if self.settings.compiler == "gcc":
            v = tools.Version(str(self.settings.compiler.version))
            if v < "6.0":
                raise ConanInvalidConfiguration("gcc >= 6.0 required")

    def requirements(self):
        self.requires.add("zlib/1.2.11")
        if self.options.with_app:
            self.requires.add("openssl/1.1.1d")
            self.requires.add("c-ares/1.15.0")
            self.requires.add("libev/4.27")
            self.requires.add("libevent/2.1.11")
            self.requires.add("libxml2/2.9.9")
        if self.options.with_hpack:
            self.requires.add("jansson/2.12")
        if self.options.with_jemalloc:
            self.requires.add("jemalloc/5.2.1")
        if self.options.with_asio:
            self.requires.add("boost/1.71.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "nghttp2-{0}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_SHARED_LIB"] = "ON" if self.options.shared else "OFF"
        cmake.definitions["ENABLE_STATIC_LIB"] = "OFF" if self.options.shared else "ON"
        cmake.definitions["ENABLE_HPACK_TOOLS"] = "ON" if self.options.with_hpack else "OFF"
        cmake.definitions["ENABLE_APP"] = "ON" if self.options.with_app else "OFF"
        cmake.definitions["ENABLE_EXAMPLES"] = "OFF"
        cmake.definitions["ENABLE_PYTHON_BINDINGS"] = "OFF"
        cmake.definitions["ENABLE_FAILMALLOC"] = "OFF"
        # disable unneeded auto-picked dependencies
        cmake.definitions["WITH_LIBXML2"] = "OFF"
        cmake.definitions["WITH_JEMALLOC"] = "ON" if self.options.with_jemalloc else "OFF"
        cmake.definitions["WITH_SPDYLAY"] = "OFF"

        cmake.definitions["ENABLE_ASIO_LIB"] = "ON" if self.options.with_asio else "OFF"

        if self.options.with_app:
            cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath
        if self.options.with_asio:
            cmake.definitions["BOOST_ROOT"] = self.deps_cpp_info["boost"].rootpath
        cmake.definitions["ZLIB_ROOT"] = self.deps_cpp_info["zlib"].rootpath

        cmake.configure()
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        target_libnghttp2 = "nghttp2" if self.options.shared else "nghttp2_static"
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                              "\n"
                              "link_libraries(\n"
                              "  nghttp2\n",
                              "\n"
                              "link_libraries(\n"
                              "  {} ${{CONAN_LIBS}}\n".format(target_libnghttp2))

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        cmake.patch_config_paths()

        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler == "Visual Studio":
            if not self.options.shared:
                self.cpp_info.defines.append("NGHTTP2_STATICLIB")

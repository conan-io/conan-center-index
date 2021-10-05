import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class Nghttp2Conan(ConanFile):
    name = "libnghttp2"
    description = "HTTP/2 C Library and tools"
    topics = ("http", "http2")
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

    def validate(self):
        if self.options.with_asio and self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Build with asio and MSVC is not supported yet, see upstream bug #589")
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "6":
            raise ConanInvalidConfiguration("gcc >= 6.0 required")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.with_app:
            self.requires("openssl/1.1.1l")
            self.requires("c-ares/1.17.1")
            self.requires("libev/4.33")
            self.requires("libevent/2.1.12")
            self.requires("libxml2/2.9.12")
        if self.options.with_hpack:
            self.requires("jansson/2.14")
        if self.options.with_jemalloc:
            self.requires("jemalloc/5.2.1")
        if self.options.with_asio:
            self.requires("boost/1.77.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

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

        if tools.Version(self.version) >= "1.42.0":
            # backward-incompatible change in 1.42.0
            cmake.definitions["STATIC_LIB_SUFFIX"] = "_static"

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
        if not self.options.shared:
            # easier to patch here rather than have patch 'nghttp_static_include_directories' for each version
            tools.save(os.path.join(self._source_subfolder, "lib", "CMakeLists.txt"),
                       "target_include_directories(nghttp2_static INTERFACE\n"
                       "${CMAKE_CURRENT_BINARY_DIR}/includes\n"
                       "${CMAKE_CURRENT_SOURCE_DIR}/includes)\n",
                       append=True)
        target_libnghttp2 = "nghttp2" if self.options.shared else "nghttp2_static"
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                              "\n"
                              "link_libraries(\n"
                              "  nghttp2\n",
                              "\n"
                              "link_libraries(\n"
                              "  {} ${{CONAN_LIBS}}\n".format(target_libnghttp2))
        if not self.options.shared:
            tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                                  "\n"
                                  "  add_library(nghttp2_asio SHARED\n",
                                  "\n"
                                  "  add_library(nghttp2_asio\n")
            tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                                  "\n"
                                  "  target_link_libraries(nghttp2_asio\n"
                                  "    nghttp2\n",
                                  "\n"
                                  "  target_link_libraries(nghttp2_asio\n"
                                  "    {}\n".format(target_libnghttp2))

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
        suffix = "_static" if tools.Version(self.version) > "1.39.2" and not self.options.shared else ""
        self.cpp_info.libs = ["nghttp2" + suffix]
        if self.options.with_asio:
            self.cpp_info.libs.insert(0, "nghttp2_asio")
        if self.settings.compiler == "Visual Studio":
            if not self.options.shared:
                self.cpp_info.defines.append("NGHTTP2_STATICLIB")

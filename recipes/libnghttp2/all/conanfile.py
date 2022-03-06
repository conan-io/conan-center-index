from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.36.0"


class Nghttp2Conan(ConanFile):
    name = "libnghttp2"
    description = "HTTP/2 C Library and tools"
    topics = ("http", "http2")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nghttp2.org"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_app": [True, False],
        "with_hpack": [True, False],
        "with_jemalloc": [True, False],
        "with_asio": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_app": True,
        "with_hpack": True,
        "with_jemalloc": False,
        "with_asio": False,
    }

    generators = "cmake", "pkg_config"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not (self.options.with_app or self.options.with_hpack or self.options.with_asio):
            del self.settings.compiler.cppstd
            del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.with_app:
            self.requires("openssl/1.1.1m")
            self.requires("c-ares/1.18.1")
            self.requires("libev/4.33")
            self.requires("libevent/2.1.12")
            self.requires("libxml2/2.9.12")
        if self.options.with_hpack:
            self.requires("jansson/2.14")
        if self.options.with_jemalloc:
            self.requires("jemalloc/5.2.1")
        if self.options.with_asio:
            self.requires("boost/1.78.0")

    def validate(self):
        if self.options.with_asio and self._is_msvc:
            raise ConanInvalidConfiguration("Build with asio and MSVC is not supported yet, see upstream bug #589")
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "6":
            raise ConanInvalidConfiguration("gcc >= 6.0 required")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_SHARED_LIB"] = self.options.shared
        cmake.definitions["ENABLE_STATIC_LIB"] = not self.options.shared
        cmake.definitions["ENABLE_HPACK_TOOLS"] = self.options.with_hpack
        cmake.definitions["ENABLE_APP"] = self.options.with_app
        cmake.definitions["ENABLE_EXAMPLES"] = False
        cmake.definitions["ENABLE_PYTHON_BINDINGS"] = False
        cmake.definitions["ENABLE_FAILMALLOC"] = False
        # disable unneeded auto-picked dependencies
        cmake.definitions["WITH_LIBXML2"] = False
        cmake.definitions["WITH_JEMALLOC"] = self.options.with_jemalloc
        cmake.definitions["WITH_SPDYLAY"] = False

        cmake.definitions["ENABLE_ASIO_LIB"] = self.options.with_asio

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
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
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
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libnghttp2")
        suffix = "_static" if tools.Version(self.version) > "1.39.2" and not self.options.shared else ""
        self.cpp_info.libs = ["nghttp2" + suffix]
        if self.options.with_asio:
            self.cpp_info.libs.insert(0, "nghttp2_asio")
        if self._is_msvc:
            if not self.options.shared:
                self.cpp_info.defines.append("NGHTTP2_STATICLIB")

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import export_conandata_patches, apply_conandata_patches, get, save, replace_in_file, rmdir, copy
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"


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
        "with_app": False,
        "with_hpack": False,
        "with_jemalloc": False,
        "with_asio": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not (self.options.with_app or self.options.with_hpack or self.options.with_asio):
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")
        if not self.options.with_app:
            del self.options.with_jemalloc

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_app or self.options.with_asio:
            self.requires("openssl/1.1.1s")
        if self.options.with_app:
            self.requires("c-ares/1.18.1")
            self.requires("libev/4.33")
            self.requires("libevent/2.1.12")
            self.requires("libxml2/2.10.3")
            self.requires("zlib/1.2.13")
            if self.options.with_jemalloc:
                self.requires("jemalloc/5.3.0")
        if self.options.with_hpack:
            self.requires("jansson/2.14")
        if self.options.with_asio:
            self.requires("boost/1.81.0")

    def validate(self):
        if self.options.with_asio and is_msvc(self):
            raise ConanInvalidConfiguration("Build with asio and MSVC is not supported yet, see upstream bug #589")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "6":
            raise ConanInvalidConfiguration(f"{self.ref} requires GCC >= 6.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_SHARED_LIB"] = self.options.shared
        tc.variables["ENABLE_STATIC_LIB"] = not self.options.shared
        tc.variables["ENABLE_HPACK_TOOLS"] = self.options.with_hpack
        tc.variables["ENABLE_APP"] = self.options.with_app
        tc.variables["ENABLE_EXAMPLES"] = False
        tc.variables["ENABLE_PYTHON_BINDINGS"] = False
        tc.variables["ENABLE_FAILMALLOC"] = False
        # disable unneeded auto-picked dependencies
        tc.variables["WITH_LIBXML2"] = False
        tc.variables["WITH_JEMALLOC"] = self.options.get_safe("with_jemalloc", False)
        tc.variables["WITH_SPDYLAY"] = False
        tc.variables["ENABLE_ASIO_LIB"] = self.options.with_asio
        if is_apple_os(self):
            # workaround for: install TARGETS given no BUNDLE DESTINATION for MACOSX_BUNDLE executable
            tc.cache_variables["CMAKE_MACOSX_BUNDLE"] = False
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if not self.options.shared:
            # easier to patch here rather than have patch 'nghttp_static_include_directories' for each version
            save(self, os.path.join(self.source_folder, "lib", "CMakeLists.txt"),
                       "target_include_directories(nghttp2_static INTERFACE\n"
                       "${CMAKE_CURRENT_BINARY_DIR}/includes\n"
                       "${CMAKE_CURRENT_SOURCE_DIR}/includes)\n",
                       append=True)
        target_libnghttp2 = "nghttp2" if self.options.shared else "nghttp2_static"
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                              "\n"
                              "link_libraries(\n"
                              "  nghttp2\n",
                              "\n"
                              "link_libraries(\n"
                              "  {} ${{CONAN_LIBS}}\n".format(target_libnghttp2))
        if not self.options.shared:
            replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                                  "\n"
                                  "  add_library(nghttp2_asio SHARED\n",
                                  "\n"
                                  "  add_library(nghttp2_asio\n")
            replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                                  "\n"
                                  "  target_link_libraries(nghttp2_asio\n"
                                  "    nghttp2\n",
                                  "\n"
                                  "  target_link_libraries(nghttp2_asio\n"
                                 f"    {target_libnghttp2}\n")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["nghttp2"].set_property("pkg_config_name", "libnghttp2")
        self.cpp_info.components["nghttp2"].libs = ["nghttp2"]
        if is_msvc(self) and not self.options.shared:
            self.cpp_info.components["nghttp2"].defines.append("NGHTTP2_STATICLIB")

        if self.options.with_asio:
            self.cpp_info.components["nghttp2_asio"].set_property("pkg_config_name", "libnghttp2_asio")
            self.cpp_info.components["nghttp2_asio"].libs = ["nghttp2_asio"]
            self.cpp_info.components["nghttp2_asio"].requires = [
                "nghttp2", "boost::headers", "openssl::openssl",
            ]

        if self.options.with_app:
            self.cpp_info.components["nghttp2_app"].requires = [
                "openssl::openssl", "c-ares::c-ares", "libev::libev",
                "libevent::libevent", "libxml2::libxml2", "zlib::zlib",
            ]
            if self.options.with_jemalloc:
                self.cpp_info.components["nghttp2_app"].requires.append("jemalloc::jemalloc")

        if self.options.with_hpack:
            self.cpp_info.components["nghttp2_hpack"].requires = ["jansson::jansson"]

        if self.options.with_app or self.options.with_hpack:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

        # trick for internal conan usage to pick up in downsteam pc files the pc file including all libs components
        self.cpp_info.set_property("pkg_config_name", "libnghttp2_asio" if self.options.with_asio else "libnghttp2")

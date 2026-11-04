from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, replace_in_file, rmdir, copy
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os


required_conan_version = ">=2"


class Nghttp2Conan(ConanFile):
    name = "libnghttp2"
    description = "HTTP/2 C Library and tools"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nghttp2.org"
    topics = ("http", "http2")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_app": [True, False],
        "with_hpack": [True, False],
        "with_jemalloc": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_app": False,
        "with_hpack": False,
        "with_jemalloc": False,
    }

    implements = ["auto_shared_fpic"]

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_app:
            del self.options.with_jemalloc
        if not (self.options.with_app or self.options.with_hpack):
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_app or self.options.with_hpack:
            self.requires("openssl/[>=1.1 <4]")
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_app:
            self.requires("libev/4.33")
            self.requires("c-ares/[>=1.27 <2]")
            self.requires("libxml2/[>=2.12.5 <3]")
            self.requires("brotli/1.1.0")
            if self.options.with_jemalloc:
                self.requires("jemalloc/5.3.0")
        if self.options.with_hpack:
            self.requires("jansson/2.14")

    def validate(self):
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "6":
            raise ConanInvalidConfiguration(f"{self.ref} requires GCC >= 6.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["ENABLE_DOC"] = False
        if self.options.with_app:
            tc.cache_variables["LIBEV_FOUND"] = True
            tc.cache_variables["LIBCARES_FOUND"] = True
            tc.cache_variables["LIBBROTLIENC_FOUND"] = True
            tc.cache_variables["LIBBROTLIDEC_FOUND"] = True
            tc.cache_variables["LIBXML2_FOUND"] = True
            if self.options.with_jemalloc:
                tc.cache_variables["JEMALLOC_FOUND"] = True
        if self.options.with_hpack:
            tc.cache_variables["JANSSON_FOUND"] = True

        # Disable Python finding so we don't build docs
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Python3"] = True
        if not self.options.with_app:
            # Disable find_package to not scare the user with system libs being picked
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Libevent"] = True  # Examples only
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Libbrotlienc"] = True  # Examples only
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Libbrotlidec"] = True  # Examples only
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Libngtcp2"] = True  # Examples only
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Libngtcp2_crypto_quictls"] = True  # Examples only
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Libnghttp3"] = True  # Examples only
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Libbpf"] = True  # Examples only
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Systemd"] = True  # Examples only
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_LibXml2"] = True  # Examples only
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Libev"] = True  # Examples only
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Libcares"] = True  # Examples only
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Libbrotli"] = True  # Examples only
        elif not self.options.get_safe("with_jemalloc"):
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Jemalloc"] = True

        if not self.options.with_hpack:
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Jansson"] = True  # Examples only

        if not self.options.with_app and not self.options.with_hpack:
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_OpenSSL"] = True  # Examples only
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_ZLIB"] = True  # Examples only


        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["ENABLE_HPACK_TOOLS"] = self.options.with_hpack
        tc.variables["ENABLE_APP"] = self.options.with_app
        tc.variables["ENABLE_EXAMPLES"] = False
        tc.variables["ENABLE_FAILMALLOC"] = False
        # disable unneeded auto-picked dependencies
        tc.variables["WITH_JEMALLOC"] = self.options.get_safe("with_jemalloc", False)
        # To avoid overwriting dll import lib by static lib
        if self.options.shared:
            tc.variables["STATIC_LIB_SUFFIX"] = "-static"
        if is_apple_os(self):
            # workaround for: install TARGETS given no BUNDLE DESTINATION for MACOSX_BUNDLE executable
            tc.cache_variables["CMAKE_MACOSX_BUNDLE"] = False
        tc.generate()

        tc = CMakeDeps(self)
        if self.options.with_app:
            tc.set_property("libev", "cmake_file_name", "Libev")
            tc.set_property("libev", "cmake_additional_variables_prefixes", ["LIBEV"])
            tc.set_property("c-ares", "cmake_file_name", "Libcares")
            tc.set_property("c-ares", "cmake_additional_variables_prefixes", ["LIBCARES"])
            tc.set_property("brotli", "cmake_file_name", "Libbrotlienc")
            tc.set_property("brotli", "cmake_additional_variables_prefixes", ["LIBBROTLIENC", "LIBBROTLIDEC"])
            tc.set_property("libxml2", "cmake_file_name", "LibXml2")
            tc.set_property("libxml2", "cmake_additional_variables_prefixes", ["LIBXML2"])
            if self.options.with_jemalloc:
                tc.set_property("jemalloc", "cmake_file_name", "Jemalloc")
                tc.set_property("jemalloc", "cmake_additional_variables_prefixes", ["JEMALLOC"])
        if self.options.with_hpack:
            tc.set_property("jansson", "cmake_file_name", "Jansson")
            tc.set_property("jansson", "cmake_additional_variables_prefixes", ["JANSSON"])
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()

    def _patch_sources(self):
        target_libnghttp2 = "nghttp2" if self.options.shared else "nghttp2_static"
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                              "\n"
                              "link_libraries(\n"
                              "  nghttp2\n",
                              "\n"
                              "link_libraries(\n"
                              "  {} ${{CONAN_LIBS}}\n".format(target_libnghttp2))
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "add_subdirectory(examples)", "")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "add_subdirectory(tests)", "")

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
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.components["nghttp2"].set_property("pkg_config_name", "libnghttp2")
        self.cpp_info.components["nghttp2"].libs = ["nghttp2"]
        if is_msvc(self) and not self.options.shared:
            self.cpp_info.components["nghttp2"].defines.append("NGHTTP2_STATICLIB")

        if self.options.with_app:
            self.cpp_info.components["nghttp2_app"].requires = [
                "openssl::openssl", "c-ares::c-ares", "libev::libev",
                "libxml2::libxml2", "zlib::zlib", "brotli::brotli"
            ]
            if self.options.with_jemalloc:
                self.cpp_info.components["nghttp2_app"].requires.append("jemalloc::jemalloc")

            if self.settings.os in ("Linux", "FreeBSD"):
                self.cpp_info.components["nghttp2_app"].system_libs.append("pthread")

        if self.options.with_hpack:
            self.cpp_info.components["nghttp2_hpack"].requires = ["jansson::jansson", "openssl::openssl", "zlib::zlib"]

        if self.options.with_app or self.options.with_hpack:
            self.runenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))

        # trick for internal conan usage to pick up in downsteam pc files the pc file including all libs components
        self.cpp_info.set_property("pkg_config_name", "libnghttp2")

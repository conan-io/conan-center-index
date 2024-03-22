import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, rm, load
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class GetDnsConan(ConanFile):
    name = "getdns"
    description = "A modern asynchronous DNS API"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://getdnsapi.net/"
    topics = ("dns", "asynchronous", "event")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tls": ["openssl", "gnutls"],
        "stub_only": ["auto", True, False],
        "with_libev": ["auto", True, False],
        "with_libevent": [True, False],
        "with_libuv": [True, False],
        "with_libidn2": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "stub_only": "auto",
        "tls": "openssl",
        "with_libev": "auto",
        "with_libevent": True,
        "with_libuv": True,
        "with_libidn2": False,  # FIXME: enable once libidn2 has been migrated https://github.com/conan-io/conan-center-index/pull/18642
    }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        self.options.with_libev = True
        # FIXME: uncomment once libunbound is available
        # self.options.stub_only = self.settings.os != "Windows"
        # self.options.with_libev = self.settings.os == "Windows"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")
        if self.options.with_libev:
            self.requires("libev/4.33")
        if self.options.with_libevent:
            self.requires("libevent/2.1.12")
        if self.options.with_libuv:
            self.requires("libuv/1.47.0")
        if self.options.with_libidn2:
            self.requires("libidn2/2.3.0")
        if self.options.tls == "gnutls":
            self.requires("gnutls/3.7.8")
            self.requires("nettle/3.8.1")
            raise ConanInvalidConfiguration("gnutls on CCI does not build the required libdane component")
        if not self.options.stub_only:
            # FIXME: missing libunbound recipe
            raise ConanInvalidConfiguration("libunbound is not (yet) available on cci")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = CMakeToolchain(self)
        tc.variables["OPENSSL_USE_STATIC_LIBS"] = not self.dependencies["openssl"].options.shared
        tc.variables["ENABLE_SHARED"] = self.options.shared
        tc.variables["ENABLE_STATIC"] = not self.options.shared
        tc.variables["ENABLE_STUB_ONLY"] = self.options.stub_only
        tc.variables["BUILD_LIBEV"] = self.options.with_libev
        tc.variables["BUILD_LIBEVENT2"] = self.options.with_libevent
        tc.variables["BUILD_LIBUV"] = self.options.with_libuv
        tc.variables["USE_LIBIDN2"] = self.options.with_libidn2
        tc.variables["USE_GNUTLS"] = self.options.tls == "gnutls"
        # Force use of internal strptime when cross-compiling
        tc.variables["FORCE_COMPAT_STRPTIME"] = True
        tc.variables["BUILD_TESTING"] = False
        # To fix OpenSSL try_compile() checks
        # https://github.com/conan-io/conan/issues/12180
        tc.variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = self.settings.build_type
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("gnutls", "cmake_file_name", "GnuTLS")
        deps.set_property("gnutls", "cmake_target_name", "GnuTLS::GnuTLS")
        deps.set_property("libev", "cmake_file_name", "Libev")
        deps.set_property("libev", "cmake_target_name", "Libev::Libev")
        deps.set_property("libevent", "cmake_file_name", "Libevent2")
        deps.set_property("libevent::core", "cmake_target_name", "Libevent2::Libevent_core")
        deps.set_property("libidn2", "cmake_file_name", "Libidn2")
        deps.set_property("libidn2", "cmake_target_name", "Libidn2::Libidn2")
        deps.set_property("libuv", "cmake_file_name", "Libuv")
        deps.set_property("libuv", "cmake_target_name", "Libuv::Libuv")
        deps.set_property("nettle", "cmake_file_name", "Nettle")
        deps.set_property("nettle", "cmake_target_name", "Nettle::Nettle")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        rm(self, "Find*.cmake", os.path.join(self.source_folder, "cmake", "modules"))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        try:
            cmake.configure(build_script_folder=self.source_path.parent)
        except ConanException:
            log = load(self, os.path.join(self.build_folder, "CMakeFiles/CMakeConfigureLog.yaml"))
            self.output.error(log)
            raise
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        libsuffix = ""
        if is_msvc(self) and not self.options.shared:
            libsuffix = "_static"

        self.cpp_info.components["libgetdns"].libs = ["getdns" + libsuffix]
        self.cpp_info.components["libgetdns"].includedirs.append(os.path.join("include", "getdns"))
        self.cpp_info.components["libgetdns"].set_property("pkg_config_name", "getdns")
        self.cpp_info.components["libgetdns"].requires = ["openssl::openssl"]
        if self.options.with_libidn2:
            self.cpp_info.components["libgetdns"].requires.append("libidn2::libidn2")
        if self.options.tls == "gnutls":
            self.cpp_info.components["libgetdns"].requires.extend(["nettle::nettle", "gnutls::gnutls"])
        if self.settings.os == "Windows":
            self.cpp_info.components["libgetdns"].system_libs.extend(["ws2_32", "crypt32", "gdi32", "iphlpapi", "psapi", "userenv"])

        if self.options.with_libevent:
            self.cpp_info.components["dns_ext_event"].libs = ["getdns_ext_event" + libsuffix]
            self.cpp_info.components["dns_ext_event"].requires = ["libgetdns", "libevent::libevent"]
            self.cpp_info.components["dns_ext_event"].set_property("pkg_config_name", "getdns_ext_event")

        if self.options.with_libev:
            self.cpp_info.components["dns_ext_ev"].libs = ["getdns_ext_ev" + libsuffix]
            self.cpp_info.components["dns_ext_ev"].requires = ["libgetdns", "libev::libev"]
            self.cpp_info.components["dns_ext_ev"].set_property("pkg_config_name", "getdns_ext_ev")

        if self.options.with_libuv:
            self.cpp_info.components["dns_ext_uv"].libs = ["getdns_ext_uv" + libsuffix]
            self.cpp_info.components["dns_ext_uv"].requires = ["libgetdns", "libuv::libuv"]
            self.cpp_info.components["dns_ext_uv"].set_property("pkg_config_name", "getdns_ext_uv")

        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)

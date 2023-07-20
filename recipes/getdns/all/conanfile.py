import glob
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, replace_in_file
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class GetDnsConan(ConanFile):
    name = "getdns"
    description = "A modern asynchronous DNS API"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://getdnsapi.net/"
    topics = ("asynchronous", "event")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tls": [False, "gnutls"],
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
        "tls": False,
        "with_libev": "auto",
        "with_libevent": True,
        "with_libuv": True,
        "with_libidn2": True,
    }

    @property
    def _with_libev(self):
        if self.options.with_libev == "auto":
            return self.settings.os != "Windows"
        else:
            return self.options.with_libev

    @property
    def _stub_only(self):
        if self.options.stub_only == "auto":
            # FIXME: uncomment the next line when libunbound is available
            # return self.settings.os == "Windows"
            return True
        else:
            return self.options.stub_only

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        self.options.stub_only = self._stub_only
        self.options.with_libev = self._with_libev

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")
        if self._with_libev:
            self.requires("libev/4.33")
        if self.options.with_libevent:
            self.requires("libevent/2.1.12")
        if self.options.with_libuv:
            self.requires("libuv/1.45.0")
        if self.options.with_libidn2:
            self.requires("libidn2/2.3.0")
        if self.options.tls == "gnutls":
            self.requires("nettle/3.8.1")
            # FIXME: missing gnutls recipe
            raise ConanInvalidConfiguration("gnutls is not (yet) available on cci")
        if not self._stub_only:
            # FIXME: missing libunbound recipe
            raise ConanInvalidConfiguration("libunbound is not (yet) available on cci")

    def build_requirements(self):
        self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os == "Windows":
            tc.variables["CMAKE_REQUIRED_LIBRARIES"] = "ws2_32"
        tc.variables["OPENSSL_USE_STATIC_LIBS"] = not self.dependencies["openssl"].options.shared
        tc.variables["ENABLE_SHARED"] = self.options.shared
        tc.variables["ENABLE_STATIC"] = not self.options.shared
        tc.variables["ENABLE_STUB_ONLY"] = self._stub_only
        tc.variables["BUILD_LIBEV"] = self._with_libev
        tc.variables["BUILD_LIBEVENT2"] = self.options.with_libevent
        tc.variables["BUILD_LIBUV"] = self.options.with_libuv
        tc.variables["USE_LIBIDN2"] = self.options.with_libidn2
        tc.variables["USE_GNUTLS"] = self.options.tls == "gnutls"
        tc.variables["BUILD_TESTING"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.set_property("libidn2::libidn2", "cmake_target_name", "Libidn2::Libidn2")
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        # Use FindOpenSSL.cmake to let check_function_exists succeed
        # Remove other cmake modules as they use FindPkgConfig
        for fn in glob.glob("Find*cmake"):
            if "OpenSSL" not in fn:
                os.unlink(fn)
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.export_sources_folder)
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
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
        if self.options.with_libidn2:
            self.cpp_info.components["libgetdns"].requires.append("libidn2::libidn2")
        if self.options.tls == "gnutls":
            self.cpp_info.components["libgetdns"].requires.extend(["nettle::nettle", "gnutls::gnutls"])

        if self.options.with_libevent:
            self.cpp_info.components["dns_ex_event"].libs = ["getdns_ex_event" + libsuffix]
            self.cpp_info.components["dns_ex_event"].requires = ["libgetdns", "libevent::libevent"]
            self.cpp_info.components["dns_ex_event"].set_property("pkg_config_name", "getdns_ext_event")

        if self._with_libev:
            self.cpp_info.components["dns_ex_ev"].libs = ["getdns_ex_ev" + libsuffix]
            self.cpp_info.components["dns_ex_ev"].requires = ["libgetdns", "libev::libev"]
            self.cpp_info.components["dns_ex_ev"].set_property("pkg_config_name", "getdns_ext_ev")

        if self.options.with_libuv:
            self.cpp_info.components["dns_ex_uv"].libs = ["getdns_ex_uv" + libsuffix]
            self.cpp_info.components["dns_ex_uv"].requires = ["libgetdns", "libuv::libuv"]
            self.cpp_info.components["dns_ex_uv"].set_property("pkg_config_name", "getdns_ext_uv")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)

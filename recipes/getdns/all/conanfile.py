import os
import glob

from conan import ConanFile
from conan import tools
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version
from conan.tools.files import apply_conandata_patches
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.50.0"

class GetDnsConan(ConanFile):
    name = "getdns"
    description = "A modern asynchronous DNS API"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://getdnsapi.net/"
    topics = ("dns", "asynchronous", "event")
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
        tools.files.copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def layout(self):
        cmake_layout(self, src_folder='src')

    def requirements(self):
        self.requires("openssl/1.1.1q")
        if self._with_libev:
            self.requires("libev/4.33")
        if self.options.with_libevent:
            self.requires("libevent/2.1.12")
        if self.options.with_libuv:
            self.requires("libuv/1.44.1")
        if self.options.with_libidn2:
            self.requires("libidn2/2.3.0")
        if self.options.tls == "gnutls":
            self.requires("nettle/3.6")
            # FIXME: missing gnutls recipe
            raise ConanInvalidConfiguration("gnutls is not (yet) available on cci")
        if not self._stub_only:
            # FIXME: missing libunbound recipe
            raise ConanInvalidConfiguration("libunbound is not (yet) available on cci")

    def build_requirements(self):
        self.tool_requires("pkgconf/1.7.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["OPENSSL_USE_STATIC_LIBS"] = not self.options["openssl"].shared
        toolchain.variables["ENABLE_SHARED"] = self.options.shared
        toolchain.variables["ENABLE_STATIC"] = not self.options.shared
        toolchain.variables["ENABLE_STUB_ONLY"] = self._stub_only
        toolchain.variables["BUILD_LIBEV"] = self._with_libev
        toolchain.variables["BUILD_LIBEVENT2"] = self.options.with_libevent
        toolchain.variables["BUILD_LIBUV"] = self.options.with_libuv
        toolchain.variables["USE_LIBIDN2"] = self.options.with_libidn2
        toolchain.variables["USE_GNUTLS"] = self.options.tls == "gnutls"
        toolchain.variables["BUILD_TESTING"] = False
        toolchain.generate()

        deps = CMakeDeps(self)
        deps.generate()

        pkg = PkgConfigDeps(self)
        pkg.generate()

        # inject pkgconf env vars in build context
        ms = VirtualBuildEnv(self)
        ms.generate(scope="build")
        # also need to inject generators folder into PKG_CONFIG_PATH
        env = Environment()
        env.prepend_path("PKG_CONFIG_PATH", self.generators_folder)
        envvars = env.vars(self, scope="build")
        envvars.save_script("conanbuildenv_pkg_config_path")

    def build(self):
        apply_conandata_patches(self)
        # Use FindOpenSSL.cmake to let check_function_exists succeed
        # Remove other cmake modules as they use FindPkgConfig
        # for fn in glob.glob(os.path.join(self.source_folder, "cmake", "modules", "Find*.cmake")):
        #     if "OpenSSL" not in fn:
        #         os.remove(fn)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = CMake(self)
        cmake.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.options.stub_only = self._stub_only
        self.info.options.with_libev = self._with_libev

    def package_info(self):
        libsuffix = ""
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            libsuffix = "_static"

        self.cpp_info.components["libgetdns"].libs = ["getdns" + libsuffix]
        self.cpp_info.components["libgetdns"].includedirs.append(os.path.join("include", "getdns"))
        self.cpp_info.components["libgetdns"].names["pkg_config"]= "getdns"
        self.cpp_info.components["libgetdns"].requires = ["openssl::openssl"]
        if self.options.with_libidn2:
            self.cpp_info.components["libgetdns"].requires.append("libidn2::libidn2")
        if self.options.tls == "gnutls":
            self.cpp_info.components["libgetdns"].requires.extend(["nettle::nettle", "gnutls::gnutls"])

        if self.options.with_libevent:
            self.cpp_info.components["dns_ex_event"].libs = ["getdns_ex_event" + libsuffix]
            self.cpp_info.components["dns_ex_event"].requires= ["libgetdns", "libevent::libevent"]
            self.cpp_info.components["dns_ex_event"].names["pkg_config"]= "getdns_ext_event"

        if self._with_libev:
            self.cpp_info.components["dns_ex_ev"].libs = ["getdns_ex_ev" + libsuffix]
            self.cpp_info.components["dns_ex_ev"].requires = ["libgetdns", "libev::libev"]
            self.cpp_info.components["dns_ex_ev"].names["pkg_config"]= "getdns_ext_ev"

        if self.options.with_libuv:
            self.cpp_info.components["dns_ex_uv"].libs = ["getdns_ex_uv" + libsuffix]
            self.cpp_info.components["dns_ex_uv"].requires = ["libgetdns", "libuv::libuv"]
            self.cpp_info.components["dns_ex_uv"].names["pkg_config"]= "getdns_ext_uv"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

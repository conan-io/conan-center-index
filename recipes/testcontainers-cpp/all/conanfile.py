import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.1"


# The ConanCenter-shaped recipe: no version attribute (config.yml maps
# versions to this folder), no exports_sources (source() pulls the release
# tarball pinned in conandata.yml), and no dependency options forced — the
# in-repo conanfile.py trims boost/libarchive for its own builds, but on CCI
# the dependency binaries are the ecosystem's defaults.
class TestcontainersCppConan(ConanFile):
    name = "testcontainers-cpp"
    description = ("Native Testcontainers for C++: throwaway Docker containers "
                   "for integration tests, over the Docker Engine HTTP API")
    license = "MIT OR Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cppudge/testcontainers-cpp"
    topics = ("testcontainers", "testing", "containers", "docker", "integration-testing")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    # `tls` gates the https:// transport (OpenSSL); `host_port_forwarding`
    # gates with_exposed_host_port's sshd sidecar tunnel (libssh2, whose
    # crypto backend is OpenSSL). Disabling both removes OpenSSL entirely.
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tls": [True, False],
        "host_port_forwarding": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tls": True,
        "host_port_forwarding": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Beast/Asio/System only — all header-only, so any boost binary works.
        self.requires("boost/1.91.0")
        self.requires("nlohmann_json/3.12.0")
        # tar building/extraction for copy-to/from-container and image builds.
        self.requires("libarchive/3.8.7")
        if self.options.tls or self.options.host_port_forwarding:
            # TLS transport and/or libssh2's crypto backend. openssl is on CCI's
            # version-range allowlist (documented exception range [>=1.1 <4]);
            # the floor here is 3 because that is what the library is built and
            # tested against (1.1 has been EOL since 2023-09).
            self.requires("openssl/[>=3 <4]")
        if self.options.host_port_forwarding:
            # SSH client for the host-port-exposure sidecar tunnel.
            self.requires("libssh2/1.11.1")

    def validate(self):
        # C++20 headers; the floor mirrors what CI actually exercises
        # (gcc 13, msvc 194, apple-clang on macos-14) minus one notch that
        # is known to carry complete-enough C++20.
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 20)
        minimum_versions = {
            "gcc": "12",
            "clang": "15",
            "apple-clang": "15",
            "msvc": "193",
        }
        minimum = minimum_versions.get(str(self.settings.compiler))
        if minimum and Version(self.settings.compiler.version) < minimum:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++20; {self.settings.compiler} "
                f"{self.settings.compiler.version} < {minimum} is not supported")
        if self.options.shared and self.settings.os == "Windows":
            # The sources carry no dllexport/visibility macros, so a Windows
            # DLL would export nothing and consumers could not link.
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support shared builds on Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        # The repo's CMakeLists auto-runs the vendored cmake-conan provider
        # when configured directly; a conan-driven build must not re-enter it.
        tc.cache_variables["SKIP_CONAN_PROVIDER_CMAKE"] = True
        tc.cache_variables["TC_BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        # Mirror the feature options into the CMake build (their CMake
        # defaults are ON; the conan options are the source of truth here).
        tc.cache_variables["TC_TLS"] = bool(self.options.tls)
        tc.cache_variables["TC_HOST_PORT_FORWARDING"] = bool(self.options.host_port_forwarding)
        # Keep install paths, package()'s rmdir, and the default
        # cpp_info.libdirs agreed on "lib" (GNUInstallDirs would pick lib64
        # on some distros).
        tc.cache_variables["CMAKE_INSTALL_LIBDIR"] = "lib"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        # Upstream installs CMake config files for non-Conan consumers;
        # CMakeDeps generates its own, so they must not ship in the package.
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "testcontainers")
        self.cpp_info.set_property("cmake_target_name", "testcontainers::testcontainers")
        self.cpp_info.libs = ["testcontainers"]
        # Scope the transitive link lines to what the static lib really needs:
        # only Boost's HEADERS component (Beast/Asio/System are header-only) —
        # without this, consumers would inherit the boost root target and link
        # every compiled libboost_*.
        self.cpp_info.requires = [
            "boost::headers",
            "nlohmann_json::nlohmann_json",
            "libarchive::libarchive",
        ]
        if self.options.tls:
            self.cpp_info.requires.extend(["openssl::ssl", "openssl::crypto"])
        if self.options.host_port_forwarding:
            # libcrypto also directly (OPENSSL_init_crypto/OPENSSL_thread_stop
            # in HostPortForwarding.cpp), not just through libssh2.
            self.cpp_info.requires.append("libssh2::libssh2")
            if "openssl::crypto" not in self.cpp_info.requires:
                self.cpp_info.requires.append("openssl::crypto")
        if self.settings.os == "Windows":
            # Named-pipe / socket transport.
            self.cpp_info.system_libs = ["ws2_32", "mswsock"]
            if self.options.tls or self.options.host_port_forwarding:
                # OpenSSL's Windows certificate store.
                self.cpp_info.system_libs.append("crypt32")
        else:
            self.cpp_info.system_libs = ["pthread"]

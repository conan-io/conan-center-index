from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.layout import basic_layout, vs_layout
from conan.tools.microsoft import is_msvc, MSBuildToolchain, MSBuildDeps, MSBuild
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, Autotools
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, chdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version

import os

required_conan_version = ">=1.52.0"

class UsocketsConan(ConanFile):
    name = "usockets"
    description = "Miniscule cross-platform eventing, networking & crypto for async applications"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/uNetworking/uSockets"
    topics = ("conan", "socket", "network", "web")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_ssl": [False, "openssl", "wolfssl"],
        "with_libuv": [True, False, "deprecated"],
        "eventloop": ["syscall", "libuv", "gcd", "boost"],
    }
    default_options = {
        "fPIC": True,
        "with_ssl": False,
        "with_libuv": "deprecated",
        "eventloop": "syscall",
    }

    @property
    def _cppstd(self):
        version = False
        if self.options.eventloop == "boost":
            version = "14"

        # OpenSSL wrapper of uSockets uses C++17 features.
        if self.options.with_ssl == "openssl":
            version = "17"

        return version

    def _minimum_compilers_version(self, cppstd):
        standards = {
            "14": {
                "Visual Studio": "15",
                "gcc": "5",
                "clang": "3.4",
                "apple-clang": "10",
            },
            "17": {
                "Visual Studio": "16",
                "gcc": "7",
                "clang": "6",
                "apple-clang": "10",
            },
        }
        return standards.get(cppstd) or {}

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.eventloop = "libuv"

    def configure(self):
        if bool(self._cppstd) == False:
            del self.settings.compiler.cppstd
            del self.settings.compiler.libcxx

        if self.options.with_libuv != "deprecated":
            self.output.warn("with_libuv is deprecated, use 'eventloop' instead.")
            if self.options.with_libuv == True:
                self.options.eventloop = "libuv"
            else:
                self.options.eventloop = "syscall"

    def layout(self):
        if is_msvc(self):
            vs_layout(self)
        else:
            basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1q")
        elif self.options.with_ssl == "wolfssl":
            self.requires("wolfssl/5.4.0")

        if self.options.eventloop == "libuv":
            self.requires("libuv/1.44.1")
        elif self.options.eventloop == "gcd":
            self.requires("libdispatch/5.3.2")
        elif self.options.eventloop == "boost":
            self.requires("boost/1.80.0")

    def package_id(self):
        # Deprecated options
        del self.info.options.with_libuv

    def validate(self):
        if self.options.eventloop == "syscall" and self.info.settings.os == "Windows":
            raise ConanInvalidConfiguration("syscall is not supported on Windows")

        if self.options.eventloop == "gcd" and \
            (self.info.settings.os != "Linux" or self.info.settings.compiler != "clang"):
            raise ConanInvalidConfiguration("eventloop=gcd is only supported on Linux with clang")

        if Version(self.version) < "0.8.0" and self.options.eventloop not in ("syscall", "libuv", "gcd"):
            raise ConanInvalidConfiguration(f"eventloop={self.options.eventloop} is not supported with {self.ref}")

        if Version(self.version) >= "0.5.0" and self.options.with_ssl == "wolfssl":
            raise ConanInvalidConfiguration(f"with_ssl={self.options.with_ssl} is not supported with {self.ref}. https://github.com/uNetworking/uSockets/issues/147")

        if self.options.with_ssl == "wolfssl" and not self.options["wolfssl"].opensslextra:
            raise ConanInvalidConfiguration("wolfssl needs opensslextra option enabled for usockets")

        if not self.options.with_libuv and self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} in Windows uses libuv by default. After 0.8.0, you can choose boost.asio by eventloop=boost.")

        cppstd = self._cppstd
        if cppstd:
            if self.info.settings.compiler.get_safe("cppstd"):
                check_min_cppstd(self, cppstd)

            minimum_version = self._minimum_compilers_version(cppstd).get(str(self.info.settings.compiler), False)
            if minimum_version:
                if Version(self.info.settings.compiler.version) < minimum_version:
                    raise ConanInvalidConfiguration(f"{self.ref} requires C++{cppstd}, which your compiler does not support.")
            else:
                self.output.warn(f"{self.ref} rfquires C++{cppstd}. Your compiler is unknown. Assuming it supports C++{cppstd}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
            deps = MSBuildDeps(self)
            deps.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()
            deps = AutotoolsDeps(self)
            deps.generate()

    def _build_msbuild(self):
        msbuild = MSBuild(self)
        msbuild.build("uSockets.vcxproj")

    def _build_make(self):
        autotools = Autotools(self)
        args = []
        if self.options.with_ssl == "openssl":
            args.append("WITH_OPENSSL=1")
        elif self.options.with_ssl == "wolfssl":
            args.append("WITH_WOLFSSL=1")
        if self.options.eventloop == "libuv":
            args.append("WITH_LIBUV=1")
        elif self.options.eventloop == "gcd":
            args.append("WITH_GCD=1")
        elif self.options.eventloop == "boost":
            args.append("WITH_ASIO=1")
        with chdir(self, self.source_folder):
            autotools.make(target="default", args=args)

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            self._build_msbuild()
        else:
            self._build_make()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"),  src=os.path.join(self.source_folder, "src"),keep_path=True)
        copy(self, pattern="*.a", dst=os.path.join(self.package_folder, "lib"), src=self.source_folder, keep_path=False)
        copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        # drop internal headers
        rmdir(self, os.path.join(self.package_folder, "include", "internal"))

    def package_info(self):
        self.cpp_info.libs = ["uSockets"]
        self.cpp_info.requires = ["boost::headers"]

        if self.options.with_ssl == "openssl":
            self.cpp_info.defines.append("LIBUS_USE_OPENSSL")
        elif self.options.with_ssl == "wolfssl":
            self.cpp_info.defines.append("LIBUS_USE_WOLFSSL")
        else:
            self.cpp_info.defines.append("LIBUS_NO_SSL")

        if self.options.eventloop == "libuv":
            self.cpp_info.defines.append("LIBUS_USE_LIBUV")
        elif self.options.eventloop == "gcd":
            self.cpp_info.defines.append("LIBUS_USE_GCD")
        elif self.options.eventloop == "boost":
            self.cpp_info.defines.append("LIBUS_USE_ASIO")

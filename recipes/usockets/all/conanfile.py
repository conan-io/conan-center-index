from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, chdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
from conans import MSBuild, AutoToolsBuildEnvironment
from conans.tools import vcvars, environment_append, unix_path, get_env

import os
import contextlib

required_conan_version = ">=1.52.0"

class UsocketsConan(ConanFile):
    name = "usockets"
    description = "Miniscule cross-platform eventing, networking & crypto for async applications"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/uNetworking/uSockets"
    topics = ("socket", "network", "web")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_ssl": [False, "openssl", "wolfssl"],
        "eventloop": ["syscall", "libuv", "gcd", "boost"],
    }
    default_options = {
        "fPIC": True,
        "with_ssl": False,
        "eventloop": "syscall",
    }

    @property
    def _minimum_cpp_standard(self):
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.eventloop = "libuv"

    def validate(self):
        if self.options.eventloop == "syscall" and self.info.settings.os == "Windows":
            raise ConanInvalidConfiguration("syscall is not supported on Windows")

        if self.options.eventloop == "gcd" and (self.info.settings.os != "Linux" or self.info.settings.compiler != "clang"):
            raise ConanInvalidConfiguration("eventloop=gcd is only supported on Linux with clang")

        if Version(self.version) < "0.8.0" and self.options.eventloop not in ("syscall", "libuv", "gcd"):
            raise ConanInvalidConfiguration(f"eventloop={self.options.eventloop} is not supported with {self.name}/{self.version}")

        if Version(self.version) >= "0.5.0" and self.options.with_ssl == "wolfssl":
            raise ConanInvalidConfiguration(f"with_ssl={self.options.with_ssl} is not supported with {self.name}/{self.version}. https://github.com/uNetworking/uSockets/issues/147")

        if self.options.with_ssl == "wolfssl" and not self.options["wolfssl"].opensslextra:
            raise ConanInvalidConfiguration("wolfssl needs opensslextra option enabled for usockets")

        cppstd = self._minimum_cpp_standard
        if not cppstd:
            return

        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, cppstd)

        minimum_version = self._minimum_compilers_version(cppstd).get(str(self.info.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++{}, which your compiler does not support.".format(self.name, cppstd))
        else:
            self.output.warn("{0} requires C++{1}. Your compiler is unknown. Assuming it supports C++{1}.".format(self.name, cppstd))

    def configure(self):
        if bool(self._minimum_cpp_standard) == False:
            try:
                del self.settings.compiler.libcxx
            except Exception:
                pass
            try:
                del self.settings.compiler.cppstd
            except Exception:
                pass

    def requirements(self):
        if self.options.with_ssl == "openssl":
            self.requires("openssl/1.1.1s")
        elif self.options.with_ssl == "wolfssl":
            self.requires("wolfssl/5.5.1")

        if self.options.eventloop == "libuv":
            self.requires("libuv/1.44.2")
        elif self.options.eventloop == "gcd":
            self.requires("libdispatch/5.3.2")
        elif self.options.eventloop == "boost":
            self.requires("boost/1.81.0")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)

    def _build_msvc(self):
        with chdir(self, os.path.join(self._source_subfolder)):
            msbuild = MSBuild(self)
            msbuild.build(project_file="uSockets.vcxproj", platforms={"x86": "Win32"})

    @contextlib.contextmanager
    def _build_context(self):
        if is_msvc(self):
            with vcvars(self):
                env = {
                    "CC": "{} cl -nologo".format(unix_path(self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(unix_path(self.deps_user_info["automake"].compile)),
                    "CFLAGS": "-{}".format(self.settings.compiler.runtime),
                    "LD": "link",
                    "NM": "dumpbin -symbols",
                    "STRIP": ":",
                    "AR": "{} lib".format(unix_path(self.deps_user_info["automake"].ar_lib)),
                    "RANLIB": ":",
                }

                if self.options.eventloop == "libuv":
                    env["CPPFLAGS"] = "-I" + unix_path(self.deps_cpp_info["libuv"].include_paths[0]) + " "

                with environment_append(env):
                    yield
        else:
            yield

    def _build_configure(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.fpic = self.options.get_safe("fPIC", False)
        with chdir(self, self._source_subfolder):
            args = ["WITH_LTO=0"]
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

            args.extend(f"{key}={value}" for key, value in autotools.vars.items())
            autotools.make(target="default", args=args)

    def build(self):
        self._patch_sources()
        if Version(self.version) < "0.8.3" and is_msvc(self):
            self._build_msvc()
        else:
            with self._build_context():
                self._build_configure()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self._source_subfolder)
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self._source_subfolder, "src"), keep_path=True)
        copy(self, pattern="*.a", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        # drop internal headers
        rmdir(self, os.path.join(self.package_folder, "include", "internal"))

    def package_info(self):
        self.cpp_info.libs = ["uSockets"]

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

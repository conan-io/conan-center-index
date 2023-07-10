from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, chdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path, MSBuild, MSBuildDeps, MSBuildToolchain
from conan.tools.scm import Version

import os

required_conan_version = ">=1.57.0"

class UsocketsConan(ConanFile):
    name = "usockets"
    description = "Miniscule cross-platform eventing, networking & crypto for async applications"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/uNetworking/uSockets"
    topics = ("socket", "network", "web")
    package_type = "static-library"
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
                "msvc": "191",
                "gcc": "5",
                "clang": "3.4",
                "apple-clang": "10",
            },
            "17": {
                "Visual Studio": "16",
                "msvc": "192",
                "gcc": "7",
                "clang": "6",
                "apple-clang": "10",
            },
        }
        return standards.get(cppstd) or {}

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _uses_msbuild(self):
        return Version(self.version) < "0.8.3" and is_msvc(self)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.eventloop = "libuv"

    def validate(self):
        if self.options.eventloop == "syscall" and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("syscall is not supported on Windows")

        if self.options.eventloop == "gcd" and (self.settings.os != "Linux" or self.settings.compiler != "clang"):
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

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, cppstd)

        minimum_version = self._minimum_compilers_version(cppstd).get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++{}, which your compiler does not support.".format(self.name, cppstd))
        else:
            self.output.warn("{0} requires C++{1}. Your compiler is unknown. Assuming it supports C++{1}.".format(self.name, cppstd))

    def configure(self):
        if bool(self._minimum_cpp_standard) == False:
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        if self.options.with_ssl == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        elif self.options.with_ssl == "wolfssl":
            self.requires("wolfssl/5.6.3")

        if self.options.eventloop == "libuv":
            self.requires("libuv/1.46.0")
        elif self.options.eventloop == "gcd":
            self.requires("libdispatch/5.3.2")
        elif self.options.eventloop == "boost":
            self.requires("boost/1.82.0")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self._uses_msbuild:
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
            if is_msvc(self):
                self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)
        if self._uses_msbuild:
            vcxproj_file = os.path.join(self.source_folder, "uSockets.vcxproj")
            platform_toolset = MSBuildToolchain(self).toolset
            import_conan_generators = ""
            for props_file in ["conantoolchain.props", "conandeps.props"]:
                props_path = os.path.join(self.generators_folder, props_file)
                if os.path.exists(props_path):
                    import_conan_generators += f"<Import Project=\"{props_path}\" />"

            replace_in_file(
                self, vcxproj_file,
                "<PlatformToolset>v141</PlatformToolset>",
                f"<PlatformToolset>{platform_toolset}</PlatformToolset>",
            )
            if import_conan_generators:
                replace_in_file(
                    self, vcxproj_file,
                    '''<Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />''',
                    f'''{import_conan_generators}\n<Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />''',
                )

    def generate(self):
        if self._uses_msbuild:
            tc = MSBuildToolchain(self)
            tc.generate()
            deps = MSBuildDeps(self)
            deps.generate()
        else:
            tc = AutotoolsToolchain(self)
            env = tc.environment()
            if is_msvc(self):
                compile_wrapper = unix_path(self, self.conf.get("user.automake:compile-wrapper", check_type=str))
                ar_wrapper = unix_path(self, self.conf.get("user.automake:lib-wrapper", check_type=str))
                env.define("CC", f"{compile_wrapper} cl -nologo")
                env.define("CXX", f"{compile_wrapper} cl -nologo")
                env.define("LD", f"{compile_wrapper} link -nologo")
                env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
                env.define("NM", "dumpbin -symbols")
                env.define("OBJDUMP", ":")
                env.define("RANLIB", ":")
                env.define("STRIP", ":")

                if self.options.eventloop == "libuv":
                    # Workaround for: https://github.com/conan-io/conan/issues/12784
                    # Otherwise AutotoolsDeps should suffice
                    env.append("CPPFLAGS", "-I" + unix_path(self, self.dependencies["libuv"].cpp_info.includedirs[0]))
            tc.generate(env)

            deps = AutotoolsDeps(self)
            deps.generate()

    def _build_msvc(self):
        with chdir(self, os.path.join(self.source_folder)):
            msbuild = MSBuild(self)
            msbuild.build("uSockets.vcxproj")

    def _build_autotools(self):
        autotools = Autotools(self)
        autotools.fpic = self.options.get_safe("fPIC", False)
        with chdir(self, self.source_folder):
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

            autotools.make(target="default", args=args)

    def build(self):
        self._patch_sources()
        if self._uses_msbuild:
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "src"), keep_path=True)
        copy(self, pattern="*.a", dst=os.path.join(self.package_folder, "lib"), src=self.source_folder, keep_path=False)
        copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.source_folder, keep_path=False)
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

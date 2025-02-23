import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.4.0"


class BlisConan(ConanFile):
    name = "blis"
    description = "BLIS is a software framework for instantiating high-performance BLAS-like dense linear algebra libraries"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/flame/blis"
    topics = ("hpc", "optimization", "matrix", "linear-algebra", "matrix-multiplication", "blas")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "config": [
            # https://github.com/flame/blis/blob/master/docs/ConfigurationHowTo.md#walkthrough
            "auto", "generic",
            # Processor families
            # These will include support for all microarchitectures in the family
            "x86_64", "intel64", "amd64", "amd64_legacy", "arm64", "arm32",
            # intel64
            "skx", "knl", "haswell", "sandybridge", "penryn",
            # amd64
            "zen", "zen2", "zen3",
            # amd64_legacy
            "excavator", "steamroller", "piledriver", "bulldozer",
            # arm64
            "armsve", "firestorm", "thunderx2", "cortexa57", "cortexa53",
            # arm32
            "cortexa15", "cortexa9"
            # other
            "a64fx", "bgq", "power10", "power9",
        ],
        "complex_return": ["gnu", "intel"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "config": "auto",
        "complex_return": "gnu",
    }

    provides = ["blas"]
    languages = ["C"]
    implements = ["auto_shared_fpic"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch == "x86_64":
            self.options.config = "intel64" if is_apple_os(self) else "x86_64"
        elif self.settings.arch == "armv8" and is_apple_os(self):
            self.options.config = "firestorm"
        elif self.settings.arch in ["armv8", "armv8.3", "arm64ec"]:
            self.options.config = "arm64"
        elif str(self.settings.arch).startswith("arm"):
            self.options.config = "arm32"
        else:
            self.options.config = "generic"

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("Only clang-cl, GCC and ICC are supported on Windows")

    def build_requirements(self):
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        # BLIS uses a custom configure script, which does not support all the standard options
        remove = ["--bindir", "--sbindir", "--oldincludedir", "--build", "--host"]
        tc.configure_args = [arg for arg in tc.configure_args if arg.split("=")[0] not in remove]
        tc.configure_args.append("--sharedir=${prefix}/res")
        tc.configure_args.append("--enable-cblas")
        tc.configure_args.append("--enable-rpath")
        if self.settings.build_type in ["Debug", "RelWithDebInfo"]:
            tc.configure_args.append("--enable-debug")
        # tries to use $FC to determine --complex-return if not explicitly set
        tc.configure_args.append(f"--complex-return={self.options.complex_return}")
        tc.configure_args.append(str(self.options.config))
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "res", "pkgconfig"))

    def package_info(self):
        # The project only exports a blis.pc file
        self.cpp_info.set_property("pkg_config_name", "blis")

        # For FindBLAS.cmake compatibility
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "BLAS")
        self.cpp_info.set_property("cmake_module_target_name", "BLAS::BLAS")

        self.cpp_info.libs = ["blis"]
        self.cpp_info.includedirs.append(os.path.join("include", "blis"))
        self.cpp_info.resdirs = ["res"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "rt"])

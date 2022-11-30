from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.files import get, rmdir, rm
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.env import VirtualBuildEnv
import os

required_conan_version = ">=1.47.0"


class FlexConan(ConanFile):
    name = "flex"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/westes/flex"
    description = "Flex, the fast lexical analyzer generator"
    topics = ("lex", "lexer", "lexical analyzer generator")
    license = "BSD-2-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def requirements(self):
        self.requires("m4/1.4.19")

    def build_requirements(self):
        self.build_requires("m4/1.4.19")
        if hasattr(self, "settings_build") and cross_building(self):
            self.build_requires(f"{self.name}/{self.version}")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Flex package is not compatible with Windows. Consider using winflexbison instead.")

    def generate(self):
        tc = AutotoolsToolchain(self)
        def yes_no(v):
            return "yes" if v else "no"
        tc.configure_args.extend([
            f"--enable-shared={yes_no(self.options.shared)}",
            f"--enable-static={yes_no(not self.options.shared)}",
            "--disable-nls",
            "--disable-bootstrap",
            "HELP2MAN=/bin/true",
            "M4=m4",
            # https://github.com/westes/flex/issues/247
            "ac_cv_func_malloc_0_nonnull=yes", "ac_cv_func_realloc_0_nonnull=yes",
            # https://github.com/easybuilders/easybuild-easyconfigs/pull/5792
            "ac_cv_func_reallocarray=no",
        ])
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()

        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self.source_folder, dst="licenses")
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["fl"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)

        lex_path = os.path.join(bindir, "flex").replace("\\", "/")
        self.output.info(f"Setting LEX environment variable: {lex_path}")
        self.env_info.LEX = lex_path

        # Don't produce files in CMakeDeps. Instead set FLEX_ROOT, and the built-in FindFLEX
        # will find the executable, includes, and libraries. Important because the built-in
        # defines a flex_target macro.
        # <PackageName>_ROOT variables are available starting in CMake 3.12
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.names["cmake_find_package"] = "_FLEX"  # Don't replace CMake's built-in
        self.cpp_info.names["cmake_find_package_multi"] = "_FLEX"
        flex_root = self.package_folder
        self.output.info("Setting FLEX_ROOT environment variable: {flex_root}")
        self.env_info.FLEX_ROOT = flex_root

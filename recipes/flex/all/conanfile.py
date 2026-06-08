import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import cross_building
from conan.tools.files import get, rmdir, copy, rm, export_conandata_patches, apply_conandata_patches
from conan.tools.layout import basic_layout
from conan.tools.gnu import AutotoolsToolchain, Autotools

required_conan_version = ">=1.53.0"


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
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Flex requires M4 to be compiled. If consumer does not have M4
        # installed, Conan will need to know that Flex requires it.
        self.requires("m4/1.4.19")

    def build_requirements(self):
        self.tool_requires("m4/1.4.19")
        self.tool_requires("gnu-config/cci.20210814")
        if hasattr(self, "settings_build") and cross_building(self):
            self.tool_requires(f"{self.name}/{self.version}")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Flex package is not compatible with Windows. "
                                            "Consider using winflexbison instead.")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def generate(self):
        at = AutotoolsToolchain(self)
        at.configure_args.extend([
            "--disable-nls",
            "--disable-bootstrap",
            "HELP2MAN=/bin/true",
            "M4=m4",
            # https://github.com/westes/flex/issues/247
            "ac_cv_func_malloc_0_nonnull=yes", "ac_cv_func_realloc_0_nonnull=yes",
            # https://github.com/easybuilders/easybuild-easyconfigs/pull/5792
            "ac_cv_func_reallocarray=no",
        ])
        if is_apple_os(self):
            at.extra_ldflags.append("-headerpad_max_install_names")
        at.generate()

    def _patch_sources_autotools(self):
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                copy(self, os.path.basename(gnu_config),
                     src=os.path.dirname(gnu_config),
                     dst=os.path.join(self.source_folder, "build-aux"))

    def build(self):
        apply_conandata_patches(self)
        self._patch_sources_autotools()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["fl"]
        self.cpp_info.system_libs = ["m"]
        # Avoid CMakeDeps messing with Conan targets
        self.cpp_info.set_property("cmake_find_mode", "none")

        lex_path = os.path.join(self.package_folder, "bin", "flex").replace("\\", "/")
        self.buildenv_info.define("LEX", lex_path)

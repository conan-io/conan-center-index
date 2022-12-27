import functools
import os

from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain
from conan.tools.build.cross_building import cross_building
from conan.tools.files import get, rmdir, copy, rm
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


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

    def requirements(self):
        self.requires("m4/1.4.19")

    def build_requirements(self):
        self.build_requires("m4/1.4.19")
        if cross_building(self):
            self.build_requires(f"{self.name}/{self.version}")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Flex package is not compatible with Windows. "
                                            "Consider using winflexbison instead.")

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        configure_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(not yes_no(self.options.shared)),
            "--disable-nls",
            "--disable-bootstrap",
            "HELP2MAN=/bin/true",
            "M4=m4",
            # https://github.com/westes/flex/issues/247
            "ac_cv_func_malloc_0_nonnull=yes", "ac_cv_func_realloc_0_nonnull=yes",
            # https://github.com/easybuilders/easybuild-easyconfigs/pull/5792
            "ac_cv_func_reallocarray=no",
        ]

        autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        copy("COPYING", src=self.source_folder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["fl"]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        lex_path = os.path.join(bindir, "flex").replace("\\", "/")
        self.output.info("Setting LEX environment variable: {}".format(lex_path))
        self.env_info.LEX = lex_path

import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, chdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout

required_conan_version = ">=1.54.0"


class FirebirdConan(ConanFile):
    name = "firebird"
    description = "Client library for Firebird - a relational database offering many ANSI SQL standard features."
    license = ("LicenseRef-IDPLicense.txt", "LicenseRef-IPLicense.txt")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/FirebirdSQL/firebird"
    topics = ("sql", "database")

    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Based on the following, with CLIENT_ONLY_FLG=Y
        # https://github.com/FirebirdSQL/firebird/blob/v5.0.0-RC2/configure.ac
        # https://github.com/FirebirdSQL/firebird/blob/v5.0.0-RC2/builds/posix/Makefile.in#L185-L239
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("icu/74.2")
        self.requires("termcap/1.3.1")

        # TODO: enable when merged
        # https://github.com/conan-io/conan-center-index/pull/18852
        # self.requires("libtommath/1.2.0")

        # TODO: should potentially unvendor these:
        # https://github.com/FirebirdSQL/firebird/tree/v5.0.0-RC2/extern
        # - SfIO
        # - boost
        # - cloop
        # - decNumber
        # - absl (for int128)
        # - libcds
        # - libtomcrypt
        # - ttmath

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                f"{self.ref} recipe is not yet supported on Windows. Contributions are welcome."
            )

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--enable-client-only")
        tc.configure_args.append("--with-builtin-tommath")
        tc.configure_args.append("--with-builtin-tomcrypt")
        tc.configure_args.append(f"--with-termlib={self.dependencies['termcap'].package_folder}")
        # Disabled because test_package fails with "double free or corruption (out), Aborted (core dumped)"
        # if self.settings.build_type == "Debug":
        #     tc.configure_args.append("--enable-developer")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "extern", "cloop", "Makefile"),
                        "$(LIBS)", "$(LDFLAGS) $(LIBS)")

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        for license_file in ["IDPLicense.txt", "IPLicense.txt"]:
            copy(self, license_file,
                 src=os.path.join(self.source_folder, "builds", "install", "misc"),
                 dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(target="dist")
        # Debug requires --enable-developer
        # build_type = "Debug" if self.settings.build_type == "Debug" else "Release"
        build_type = "Release"
        dist_root = os.path.join(self.source_folder, "gen", build_type, "firebird")
        copy(self,"*", os.path.join(dist_root, "include"), os.path.join(self.package_folder, "include"))
        copy(self,"*", os.path.join(dist_root, "lib"), os.path.join(self.package_folder, "lib"))
        copy(self,"*", os.path.join(dist_root, "bin"), os.path.join(self.package_folder, "bin"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "firebird")
        self.cpp_info.libs = ["fbclient"]
        # TODO: unvendor
        self.cpp_info.libs += ["tomcrypt", "tommath"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])

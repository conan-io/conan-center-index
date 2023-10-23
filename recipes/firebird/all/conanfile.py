import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, chdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
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

    def export_sources(self):
        copy(self, "LICENSE-*", self.recipe_folder, self.export_sources_folder)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # https://github.com/FirebirdSQL/firebird/tree/v4.0.2/extern
        # TODO: should potentially replace these vendored libraries with Conan packages:
        #   - btyacc
        #   - editline
        #   - abseil (for int128)
        #   - libtommath
        #   - re2
        # Not currently available in ConanCenter:
        #   - cloop
        #   - decNumber
        #   - libtomcrypt
        #   - SfIO
        #   - ttmath
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("icu/73.2")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD", "Macos"]:
            raise ConanInvalidConfiguration(f"{self.ref} recipe is not yet supported on {self.settings.os}.")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--with-builtin-tommath")
        tc.configure_args.append("--with-builtin-tomcrypt")
        # Reduce the amount of warnings
        tc.extra_cxxflags.append("-Wno-unused-result")
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def _patch_sources(self):
        # Disable building of examples, plugins and executables.
        # Only executables required for the build are included.
        # https://github.com/FirebirdSQL/firebird/blob/v4.0.2/builds/posix/Makefile.in#L281-L305
        posix_makefile = os.path.join(self.source_folder, "builds/posix/Makefile.in")
        for target in ["examples", "plugins"]:
            replace_in_file(self, posix_makefile, f"$(MAKE) {target}", "")
        replace_in_file(self, posix_makefile, "$(MAKE) utilities", "$(MAKE) isql gbak gfix udfsupport")

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            # https://github.com/FirebirdSQL/firebird/blob/v4.0.3/autogen.sh#L45-L59
            autotools.autoreconf()
            self.run("libtoolize --install --copy --force")
            autotools.configure()
            autotools.make()

    def package(self):
        for license_file in ["IDPLicense.txt", "IPLicense.txt"]:
            copy(self, license_file,
                 src=os.path.join(self.source_folder, "builds", "install", "misc"),
                 dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE-*",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"),
             keep_path=False)
        copy(self,"*",
            src=os.path.join(self.source_folder, f"gen/{self.settings.build_type}/firebird/lib"),
            dst=os.path.join(self.package_folder, "lib"))
        copy(self, "*",
             src=os.path.join(self.source_folder, "src/include"),
             dst=os.path.join(self.package_folder, "include"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "firebird")

        self.cpp_info.libs = ["fbclient", "ib_util", "decFloat", "edit", "re2", "tomcrypt", "tommath"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])

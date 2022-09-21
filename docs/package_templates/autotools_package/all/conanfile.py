from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.files import copy, get, rm, rmdir, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.51.3"


class PackageConan(ConanFile):
    name = "package"
    description = "short description"
    license = "" # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/project/package"
    topics = ("topic1", "topic2", "topic3") # no "conan"  and project name in topics
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_foobar": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_foobar": True,
    }

    # no exports_sources attribute, but export_sources(self) method instead
    # this allows finer grain exportation of patches per version
    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC # once removed by config_options, need try..except for a second del
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx # for plain C projects only
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd # for plain C projects only
        except Exception:
            pass

    def layout(self):
        basic_layout(self, src_folder="src") # src_folder must use the same source folder name the project

    def requirements(self):
        self.requires("dependency/0.8.1") # prefer self.requires method instead of requires attribute
        if self.options.with_foobar:
            self.requires("foobar/0.1.0")

    def validate(self):
        # validate the minimum cpp standard supported. Only for C++ projects
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if self.info.settings.os not in ["Linux", "FreeBSD", "MacOS"]:
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.info.settings.os}.")

    # if another tool than the compiler or autotools is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        self.tool_requires("libtool/x.y.z")
        self.tool_requires("pkgconf/x.y.z")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        # autotools usually uses 'yes' and 'no' to enable/disable options
        yes_no = lambda v: "yes" if v else "no"
        # --fpic is automatically managed when 'fPIC'option is declared
        # --enable/disable-shared is automatically managed when 'shared' option is declared
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--with-foobar=%s" % yes_no(self.options.with_foobar))
        tc.configure_args.append("--enable-tools=no")
        tc.configure_args.append("--enable-manpages=no")
        tc.generate()
        # generate dependencies for pkg-config
        tc = PkgConfigDeps(self)
        tc.generate()
        # generate dependencies for autotools
        tc = AutotoolsDeps(self)
        tc.generate()
        # inject tools_requires env vars in build scope (not needed if there is no tool_requires)
        env = VirtualBuildEnv(self)
        env.generate()
        # inject requires env vars in build scope
        # it's required in case of native build when there is AutotoolsDeps & at least one dependency which might be shared, because configure tries to run a test executable
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

    def build(self):
        # apply patches listed in conandata.yml
        apply_conandata_patches(self)
        autotools = Autotools(self)
        # run autoreconf to generate configure file
        autotools.autoreconf()
        # ./configure + toolchain file
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        autotools.install()

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["package_lib"]

        # if package provides a pkgconfig file (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        self.cpp_info.set_property("pkg_config_name", "package")

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")

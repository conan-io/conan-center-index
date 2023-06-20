from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, chdir, rm, rmdir, copy
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conan.tools.build import cross_building

required_conan_version = ">=1.52.0"

class libxftConan(ConanFile):
    name = "libxft"
    description = 'X FreeType library'
    topics = ("libxft", "x11", "xorg")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.x.org/wiki/"
    license = "X11"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("xorg/system")
        self.requires("freetype/2.13.0", transitive_headers=True)
        self.requires("fontconfig/2.14.2", transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("pkgconf/1.9.3")
        self.tool_requires("xorg-macros/1.19.3")
        self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def generate(self):
        # inject tool_requires env vars in build scope (not needed if there is no tool_requires)
        env = VirtualBuildEnv(self)
        env.generate()
        # inject requires env vars in build scope
        # it's required in case of native build when there is AutotoolsDeps & at least one dependency which might be shared, because configure tries to run a test executable
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend(["--disable-dependency-tracking"])
        if self.options.shared:
            tc.configure_args.extend(["--disable-static", "--enable-shared"])
        else:
            tc.configure_args.extend(["--disable-shared", "--enable-static"])
        tc.generate()

        # generate pkg-config files of dependencies (useless if upstream configure.ac doesn't rely on PKG_CHECK_MODULES macro)
        tc = PkgConfigDeps(self)
        tc.generate()
        # generate dependencies for autotools
        tc = AutotoolsDeps(self)
        tc.generate()


    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()


    def package(self):
        copy(self, pattern="LICENSE", dst="licenses", src=self.source_folder)
        copy(self, pattern="COPYING", dst="licenses", src=self.source_folder)
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", f"{self.package_folder}/lib", recursive=True)
        rmdir(self, f"{self.package_folder}/lib/pkgconfig")
        rmdir(self, f"{self.package_folder}/share")

    def package_info(self):
        self.cpp_info.names['pkg_config'] = "Xft"
        self.cpp_info.set_property("pkg_config_name", "xft")
        self.cpp_info.libs = ["Xft"]

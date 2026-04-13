from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path, MSBuild
import os

required_conan_version = ">=2.0.9"


class PackageConan(ConanFile):
    name = "fix8"
    description = (
        "A modern open source C++ FIX framework featuring complete schema driven customisation,"
        " high performance and fast application development"
    )
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/fix8/fix8"
    topics = ("fix", "fintech", "fixprotocol", "fixengine")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tcmalloc": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_tcmalloc": False,
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")
        self.folders.build = self.folders.source

    def requirements(self):
        self.requires("poco/1.14.2")
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_tcmalloc:
            self.requires("gperftools/2.15")

    def validate(self):
        check_min_cppstd(self, 14)

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        self.tool_requires("automake/1.16.5")
        self.tool_requires("autoconf/2.71")
        self.tool_requires("pkgconf/2.0.3")
        self.tool_requires("m4/1.4.19")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        if not is_msvc(self):
            if not cross_building(self):
                VirtualRunEnv(self).generate(scope="build")

            deps = AutotoolsDeps(self)
            deps.generate()

            tc = AutotoolsToolchain(self)
            if self.options.shared:
                tc.configure_args.extend(["--enable-shared", "--disable-static"])
            else:
                tc.configure_args.extend(["--disable-shared", "--enable-static"])
            tc.generate()
            tc = PkgConfigDeps(self)
            tc.generate()

    def build(self):
        if is_msvc(self):
            os.chdir("msvc")
            msbuild = MSBuild(self)
            self.run('nuget restore')
            msbuild.build("fix8-vc142.sln")
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            copy(self,pattern="*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
            copy(self, pattern="*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, pattern="*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, pattern="*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            copy(self, pattern="*.exe", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "share"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["fix8"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "rt"]

        self.cpp_info.set_property("cmake_target_name", "FIX8::fix8")
        self.cpp_info.set_property("pkg_config_name", "fix8")

        self.output.info(f"Conan package_info for {self.name}/{self.version}:")
        self.output.info(f"  libs: {self.cpp_info.libs}")
        self.output.info(f"  system_libs: {self.cpp_info.system_libs}")
        self.output.info(f"  cmake_target_name: {self.cpp_info.get_property('cmake_target_name')}")
        self.output.info(f"  pkg_config_name: {self.cpp_info.get_property('pkg_config_name')}")

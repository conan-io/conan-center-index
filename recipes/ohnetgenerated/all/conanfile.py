from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.files import get, chdir, copy, mkdir, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, NMakeToolchain
import os

required_conan_version = ">=1.53.0"


class OhNetGeneratedConan(ConanFile):
    name = "ohnetgenerated"
    description = "Generated proxies and providers for ohMedia and UPnP:AV services"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/openhome/ohNetGenerated"
    topics = ("openhome", "ohnet", "ohnetgenerated", "upnp")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def _get_openhome_architecture(self, args):
        if is_apple_os(self):
            if str(self.settings.arch).startswith("armv8"):
                openhome_architecture = "arm64"
                args.extend([f"openhome_architecture={openhome_architecture}", f"detected_openhome_architecture={openhome_architecture}"])
        return args

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("ohnet/[>=1.36.5182]", transitive_headers=True, transitive_libs=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.make_args.append("-j1")
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        targets = "proxies devices"

        include_dir = self.dependencies["ohnet"].cpp_info.includedirs[0]
        lib_dir = self.dependencies["ohnet"].cpp_info.libdirs[0]

        args = [f"inc_build={include_dir}", f"depDirCs={lib_dir}/", f"ohNetLibDir={lib_dir}/"]
        if self.settings.build_type == "Debug":
            args.append("debug=1")

        with chdir(self, self.source_folder):
            if is_msvc(self):
                self.run(f"nmake /f OhNet.mak {' '.join(args)} {targets}")
            else:
                args = self._get_openhome_architecture(args)
                args.append("rsync=no")
                if str(self.settings.compiler.libcxx) == "libc++":
                    args.extend(["CPPFLAGS=-stdlib=libc++", "LDFLAGS=-stdlib=libc++"])
                autotools = Autotools(self)
                autotools.make(args=args, target=targets)

    def package(self):
        targets = "install"

        installlibdir = os.path.join(self.package_folder, "lib")
        installincludedir = os.path.join(self.package_folder, "include")

        include_dir = self.dependencies["ohnet"].cpp_info.includedirs[0]
        lib_dir = self.dependencies["ohnet"].cpp_info.libdirs[0]

        args = [f"inc_build={include_dir}", f"depDirCs={lib_dir}/", f"ohNetLibDir={lib_dir}/"]
        if self.settings.build_type == "Debug":
            args.append("debug=1")

        copy(self, "License.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        with chdir(self, self.source_folder):
            if is_msvc(self):
                self.run(f"nmake /f OhNet.mak {targets} installdir={self.package_folder} installlibdir={installlibdir} installincludedir={installincludedir} {' ' .join(args)}")
            else:
                args.extend([f"prefix={self.package_folder}", f"installlibdir={installlibdir}", f"installincludedir={installincludedir}", "rsync=no"])
                args = self._get_openhome_architecture(args)
                autotools = Autotools(self)
                autotools.make(args=args, target=targets)
                if is_apple_os(self):
                    fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.components["ohNetGeneratedProxies"].libs = ["ohNetGeneratedProxies"]
        self.cpp_info.components["ohNetGeneratedProxies"].set_property("cmake_target_name", "ohNetGeneratedProxies")

        self.cpp_info.components["ohNetGeneratedDevices"].libs = ["ohNetGeneratedDevices"]
        self.cpp_info.components["ohNetGeneratedDevices"].set_property("cmake_target_name", "ohNetGeneratedDevices")

        for component in ["ohNetCore", "OhNetDevices", "ohNetProxies", "TestFramework"]:
            self.cpp_info.components[component].names["cmake_find_package"] = component
            self.cpp_info.components[component].names["cmake_find_package_multi"] = component
            self.cpp_info.components[component].set_property("cmake_target_name", component)

from conan import ConanFile
from conan.tools.files import get, chdir, copy, mkdir, export_conandata_patches, apply_conandata_patches
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, NMakeToolchain
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"


class OhNetConan(ConanFile):
    name = "ohnet"
    description = "OpenHome Networking (ohNet) is a modern, cross platform, multi-language UPnP stack"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/openhome/ohNet"
    topics = ("openhome", "ohnet", "upnp")
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
    short_paths = True

    def _fill_openhome_architecture(self, args):
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

    def validate(self):
        if is_msvc(self) and (self.options.shared or msvc_runtime_flag(self).startswith('MD')):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support shared builds with Visual Studio yet")

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

    def _fill_ohnet_args(self, args):
        if self.settings.build_type == "Debug":
            args.append("debug=1")

        installlibdir = os.path.join(self.package_folder, "lib")
        installincludedir = os.path.join(self.package_folder, "include")

        args.extend([f"prefix={self.package_folder}",f"installdir={self.package_folder}",  f"installlibdir={installlibdir}", f"installincludedir={installincludedir}"])

        if not is_msvc(self):
            args = self._fill_openhome_architecture(args)
            args.append("rsync=no")
            if str(self.settings.compiler.libcxx) == "libc++":
                args.extend(["CPPFLAGS=-stdlib=libc++", "LDFLAGS=-stdlib=libc++"])
        return args

    def build(self):
        apply_conandata_patches(self)
        targets = "ohNetDll TestsNative proxies devices"
        args = []
        self._fill_ohnet_args(args)

        with chdir(self, self.source_folder):
            if is_msvc(self):
                self.run(f"nmake /f OhNet.mak {targets} {' '.join(args)}")
            else:
                autotools = Autotools(self)
                autotools.make(args=args, target=targets)

    def package(self):
        copy(self, "License.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        copy(self, "*", src=os.path.join(self.source_folder, "OpenHome", "Net", "ServiceGen"), dst=os.path.join(self.package_folder, "lib", "ServiceGen"))
        mkdir(self, os.path.join(self.package_folder, "lib", "t4"))

        args = []
        self._fill_ohnet_args(args)

        with chdir(self, self.source_folder):
            if is_msvc(self):
                self.run(f"nmake /f OhNet.mak install {' '.join(args)}")
            else:
                autotools = Autotools(self)
                autotools.make(args=args, target="install-libs install-includes")
                if is_apple_os(self):
                    fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.components["ohNet"].libs = ["ohNet"]
        self.cpp_info.components["ohNet"].builddirs = [os.path.join("lib", "ServiceGen")]
        self.cpp_info.components["ohNet"].set_property("cmake_target_name", "ohNet")
        self.cpp_info.components["ohNet"].defines.extend(["DEFINE_LITTLE_ENDIAN"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ohNet"].system_libs.extend(["pthread", "m"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["ohNet"].system_libs.extend(["iphlpapi", "ws2_32", "dbghelp"])

        self.cpp_info.components["ohNetCore"].libs = ["ohNetCore"]
        self.cpp_info.components["ohNetCore"].builddirs = [os.path.join("lib", "ServiceGen")]
        self.cpp_info.components["ohNetCore"].set_property("cmake_target_name", "ohNetCore")
        self.cpp_info.components["ohNetCore"].defines.extend(["DEFINE_LITTLE_ENDIAN"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ohNetCore"].system_libs.extend(["pthread", "m"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["ohNetCore"].system_libs.extend(["iphlpapi", "ws2_32", "dbghelp"])
        elif self.settings.os == "Macos":
            self.cpp_info.components["ohNetCore"].frameworks.extend(["CoreFoundation", "IOKit", "SystemConfiguration"])

        self.cpp_info.components["ohNetDevices"].libs = ["ohNetDevices"]
        self.cpp_info.components["ohNetDevices"].set_property("cmake_target_name", "ohNetDevices")

        self.cpp_info.components["ohNetProxies"].libs = ["ohNetProxies"]
        self.cpp_info.components["ohNetProxies"].set_property("cmake_target_name", "ohNetProxies")

        self.cpp_info.components["TestFramework"].libs = ["TestFramework"]
        self.cpp_info.components["TestFramework"].set_property("cmake_target_name", "TestFramework")
        self.cpp_info.components["TestFramework"].requires = ["ohNetCore"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "ohNet"
        self.cpp_info.names["cmake_find_package_multi"] = "ohNet"
        self.cpp_info.names["pkg_config"] = "ohNet"

        for component in ["ohNetCore", "OhNetDevices", "ohNetProxies", "TestFramework"]:
            self.cpp_info.components[component].names["cmake_find_package"] = component
            self.cpp_info.components[component].names["cmake_find_package_multi"] = component
            self.cpp_info.components[component].set_property("cmake_target_name", component)

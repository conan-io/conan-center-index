import glob
import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.files import apply_conandata_patches, copy, chdir, export_conandata_patches, get, rename, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path, MSBuild, MSBuildToolchain
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.57.0"


class PcapplusplusConan(ConanFile):
    name = "pcapplusplus"
    package_type = "static-library"
    license = "Unlicense"
    description = "PcapPlusPlus is a multiplatform C++ library for capturing, parsing and crafting of network packets"
    topics = ("pcap", "network", "security", "packet")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/seladb/PcapPlusPlus"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "immediate_mode": [True, False],
    }
    default_options = {
        "fPIC": True,
        "immediate_mode": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("npcap/1.70")
            if self.version < "22.11":
                self.requires("pthreads4w/3.0.0")
        else:
            self.requires("libpcap/1.10.1")

        # TODO: use conan recipe instead of embedded one
        # self.requires("hash-library/8.0")

    def validate(self):
        if self.settings.os == "Windows" and not is_msvc(self):
            raise ConanInvalidConfiguration("Can not build on Windows: only msvc compiler is supported.")
        if self.settings.os not in ("FreeBSD", "Linux", "Macos", "Windows"):
            raise ConanInvalidConfiguration(f"{self.settings.os} is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    @property
    def _configure_sh_script(self):
        return {
            "Android": "configure-android.sh",
            "Linux": "configure-linux.sh",
            "Macos": "configure-mac_os_x.sh",
            "FreeBSD": "configure-freebsd.sh",
        }[str(self.settings.os)]

    def _patch_sources(self):
        if not self.options.get_safe("fPIC") and self.settings.os != "Windows":
            replace_in_file(self, os.path.join(self.source_folder, "PcapPlusPlus.mk.common"),
                                  "-fPIC", "")
        apply_conandata_patches(self)
        if self.settings.os != "Windows":
            rename(self, os.path.join(self.source_folder, self._configure_sh_script), os.path.join(self.source_folder, "configure"))
        else:
            props_file = os.path.join(self.generators_folder, "conantoolchain.props")
            vcxproj_templates = glob.glob(f"{self.source_folder}/mk/vs/*.vcxproj.template")
            for template_file in vcxproj_templates:
                # Load conan-generated conantoolchain.props before Microsoft.Cpp.props 
                # so that we have precedence over PlatformToolset version
                replace_in_file(self, template_file, '<Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />', 
                                f'<Import Project="{props_file}" />\n<Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />')

    def generate(self):
        if self.settings.os == "Windows":
            tc = MSBuildToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.configure_args.clear() # this configure script does not accept the typical arguments
            tc.configure_args.extend([
                "--libpcap-include-dir", unix_path(self, self.dependencies["libpcap"].cpp_info.aggregated_components().includedirs[0]),
                "--libpcap-lib-dir", unix_path(self, self.dependencies["libpcap"].cpp_info.aggregated_components().includedirs[0]),
            ])

            if self.options.immediate_mode:
                tc.configure_args.append("--use-immediate-mode")
            if is_apple_os(self) and "arm" in self.settings.arch:
                tc.configure_args.append("--arm64")
            
            tc.generate()

    def build(self):
        self._patch_sources()
        if self.settings.os == "Windows":
            self._build_windows()
        else:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.configure()
                autotools.make(target="libs")

    def _build_windows(self):
        with chdir(self, self.source_folder):
            config_args = [
                "configure-windows-visual-studio.bat",
                "--pcap-sdk", self.dependencies["npcap"].package_folder,
                "--vs-version", "vs2015", # this will be later overridden by the props file generated by MSBuildToolchain
            ]
            if self.version < "22.11":
                config_args += ["--pthreads-home", self.dependencies["pthreads4w"].package_folder]
            self.run(" ".join(config_args), env="conanbuild")
            msbuild = MSBuild(self)
            targets = ['Common++', 'Packet++', 'Pcap++']
            msbuild.build("mk/vs2015/PcapPlusPlus.sln", targets=targets)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"), keep_path=False)
        copy(self, "*.h", src=os.path.join(self.source_folder,  "Dist", "header"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.a", src=os.path.join(self.source_folder,  "Dist"), dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.lib", src=os.path.join(self.source_folder,  "Dist"), dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["Pcap++", "Packet++", "Common++"]
        if self.version < "22.11" and self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("pthread")
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["CoreFoundation", "Security", "SystemConfiguration"])
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]

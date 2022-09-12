from conan import ConanFile
from conan.tools import files
from conan.tools.microsoft import MSBuild, is_msvc
from conan.tools.microsoft.visual import vs_ide_version
from conan.errors import ConanInvalidConfiguration
from conans import AutoToolsBuildEnvironment
from conans.tools import msvs_toolset
import os

required_conan_version = ">=1.33.0"


class PcapplusplusConan(ConanFile):
    name = "pcapplusplus"
    license = "Unlicense"
    description = "PcapPlusPlus is a multiplatform C++ library for capturing, parsing and crafting of network packets"
    topics = ("conan", "pcapplusplus", "pcap", "network", "security", "packet")
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

    exports_sources = "patches/*"
    generators = "make"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("pthreads4w/3.0.0")
            self.requires("npcap/1.70")
        else:
            self.requires("libpcap/1.9.1")

    def _get_vs_version(self):
        if not is_msvc(self):
            return None
        vs_mapping = {
            "14": "vs2015",
            "15": "vs2017",
            "16": "vs2019",
            # configure-windows-visual-studio.bat does not know vs2022
            # we use vs2019 and change PlatformToolset later
            "17": "vs2019",
        }
        return vs_mapping.get(vs_ide_version(self), None)

    def validate(self):
        if self.settings.os == "Windows" and self._get_vs_version() is None:
            raise ConanInvalidConfiguration("Can not build on Windows: only msvc compiler is supported.")
        if self.settings.os not in ("FreeBSD", "Linux", "Macos", "Windows"):
            raise ConanInvalidConfiguration("%s is not supported" % self.settings.os)

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

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
            files.replace_in_file(self, os.path.join(self._source_subfolder, "PcapPlusPlus.mk.common"),
                                  "-fPIC", "")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            files.patch(self, **patch)

    def build(self):
        self._patch_sources()
        if self.settings.os == "Windows":
            self._build_windows()
        else:
            self._build_posix()

    def _build_windows(self):
        vs_version = self._get_vs_version()
        with files.chdir(self, self._source_subfolder):
            config_args = [
                "configure-windows-visual-studio.bat",
                "--pcap-sdk", self.deps_cpp_info["npcap"].rootpath,
                "--pthreads-home", self.deps_cpp_info["pthreads4w"].rootpath,
                "--vs-version", vs_version,
            ]
            self.run(" ".join(config_args), run_environment=True)
            msbuild = MSBuild(self)
            cmd = msbuild.command(f"mk/{vs_version}/PcapPlusPlus.sln", [
                'Common++', 'Packet++', 'Pcap++'
            ])
            self.run(cmd + " /p:PlatformToolset=" + msvs_toolset(self))

    def _build_posix(self):
        with files.chdir(self._source_subfolder):
            config_args = [
                "./{}".format(self._configure_sh_script),
                "--libpcap-include-dir", files.unix_path(self.deps_cpp_info["libpcap"].include_paths[0]),
                "--libpcap-lib-dir", files.unix_path(self.deps_cpp_info["libpcap"].lib_paths[0]),
            ]
            if self.options.immediate_mode:
                config_args.append("--use-immediate-mode")
            if files.is_apple_os(self.settings.os) and "arm" in self.settings.arch:
                config_args.append("--arm64")

            autotools = AutoToolsBuildEnvironment(self)
            autotools.cxx_flags.extend(["-D{}".format(d) for d in autotools.defines])
            with files.environment_append(autotools.vars):
                self.run(" ".join(config_args), run_environment=True)
                autotools.make(target="libs")

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder, keep_path=False)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "Dist", "header"))
        self.copy("*.a", dst="lib", src=os.path.join(self._source_subfolder, "Dist"), keep_path=False)
        self.copy("*.lib", dst="lib", src=os.path.join(self._source_subfolder, "Dist"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["Pcap++", "Packet++", "Common++"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("pthread")
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["CoreFoundation", "Security", "SystemConfiguration"])
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["wsock32", "ws2_32"]

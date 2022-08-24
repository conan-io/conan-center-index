from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
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
        if self.settings.os != "Windows":
            self.requires("libpcap/1.9.1")

    def validate(self):
        if self.settings.os == "Windows":
            # FIXME: missing winpcap recipe (https://github.com/bincrafters/community/pull/1395)
            raise ConanInvalidConfiguration("Can not build on Windows: Winpcap is not available on cci (yet).")
        if self.settings.os not in ("FreeBSD", "Linux", "Macos"):
            raise ConanInvalidConfiguration("%s is not supported" % self.settings.os)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
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
        if not self.options.get_safe("fPIC"):
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "PcapPlusPlus.mk.common"),
                                  "-fPIC", "")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def build(self):
        self._patch_sources()
        with tools.files.chdir(self, self._source_subfolder):
            config_args = [
                "./{}".format(self._configure_sh_script),
                "--libpcap-include-dir", tools.unix_path(self.deps_cpp_info["libpcap"].include_paths[0]),
                "--libpcap-lib-dir", tools.unix_path(self.deps_cpp_info["libpcap"].lib_paths[0]),
            ]
            if self.options.immediate_mode:
                config_args.append("--use-immediate-mode")
            if tools.is_apple_os(self.settings.os) and "arm" in self.settings.arch:
                config_args.append("--arm64")

            autotools = AutoToolsBuildEnvironment(self)
            autotools.cxx_flags.extend(["-D{}".format(d) for d in autotools.defines])
            with tools.environment_append(autotools.vars):
                self.run(" ".join(config_args), run_environment=True)
                autotools.make(target="libs")

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder, keep_path=False)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "Dist", "header"))
        self.copy("*.a", dst="lib", src=os.path.join(self._source_subfolder, "Dist"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["Pcap++", "Packet++", "Common++"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("pthread")
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["CoreFoundation", "Security", "SystemConfiguration"])

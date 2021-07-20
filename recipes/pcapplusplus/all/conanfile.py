from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os


class PcapplusplusConan(ConanFile):
    name = "pcapplusplus"
    version = "21.05"
    license = "Unlicense"
    description = "PcapPlusPlus is a multiplatform C++ library for capturing, parsing and crafting of network packets"
    topics = ("conan", "pcapplusplus", "pcap", "network", "security", "packet")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/seladb/PcapPlusPlus"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "immediate_mode": [True, False],
    }
    default_options = {
        "immediate_mode": False,
    }
    generators = "make"

    _source_subfolder = "PcapPlusPlus"

    def configure(self):
        if self.settings.os not in ["Macos", "Linux"]:
            raise ConanInvalidConfiguration("%s is not supported" % self.settings.os)

        del self.settings.compiler.libcxx

    def requirements(self):
        if self.settings.os == "Windows":
            # FIXME: missing winpcap recipe (https://github.com/bincrafters/community/pull/1395)
            raise ConanInvalidConfiguration("winpcap is not available on cci (yet)")
        else:
            self.requires("libpcap/1.9.1")

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, 
            strip_root=True,
        )

    def build(self):
        with tools.chdir(self._source_subfolder):
            config_script = "configure-linux.sh" if self.settings.os == "Linux" else "configure-mac_os_x.sh"
            libpcap_include_path = self.deps_cpp_info["libpcap"].include_paths[0]
            libpcap_lib_path = self.deps_cpp_info["libpcap"].lib_paths[0]
            config_command = ("./%s --libpcap-include-dir %s --libpcap-lib-dir %s" % (config_script, libpcap_include_path, libpcap_lib_path))
            if self.options.immediate_mode:
                config_command += " --use-immediate-mode"

            self.run(config_command)

            env_build = AutoToolsBuildEnvironment(self)
            env_build.make(target="libs")

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder, keep_path=False)
        self.copy("*.h", dst="include", src="PcapPlusPlus/Dist/header")
        self.copy("*.a", dst="lib", src="PcapPlusPlus/Dist/", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["Pcap++", "Packet++", "Common++"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.append("CoreFoundation")
            self.cpp_info.frameworks.append("Security")
            self.cpp_info.frameworks.append("SystemConfiguration")

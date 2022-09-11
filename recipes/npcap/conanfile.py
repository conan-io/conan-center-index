from os.path import join
from conans import ConanFile, tools


class NpcapConan(ConanFile):
    name = "npcap"
    description = "Windows port of the libpcap library"
    homepage = "https://npcap.com/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "https://github.com/nmap/npcap/blob/master/LICENSE"
    topics = ("npcap", "pcap")
    settings = {
        "os": ["Windows"],
        "arch": ["x86", "x86_64", "armv8"],
        "build_type": None,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder)
        tools.download(filename="LICENSE", url=[
            f"https://raw.githubusercontent.com/nmap/npcap/v{self.version}/LICENSE",
            "https://raw.githubusercontent.com/nmap/npcap/master/LICENSE"
        ])

    def package(self):

        self.copy("LICENSE", dst="licenses")
        self.copy("*.h", dst="include", src=join(self._source_subfolder, "Include"))

        if self.settings.arch == "x86_64":
            self.copy("*.lib", dst="lib", src=join(self._source_subfolder, "Lib", "x64"))
        elif self.settings.arch == "armv8":
            self.copy("*.lib", dst="lib", src=join(self._source_subfolder, "Lib", "ARM64"))
        else:
            self.copy("*.lib", dst="lib", src=join(self._source_subfolder, "Lib"))

    def package_info(self):
        self.cpp_info.libs = self.collect_libs()

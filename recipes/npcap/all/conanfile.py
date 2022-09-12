from os.path import join
from conan import ConanFile
from conan.tools.files import get, download, copy


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

    # not needed but supress warning message from conan commands
    def layout(self):
        pass

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build(self):
        source = self.conan_data["sources"][self.version]
        get(self, **source['sdk'], destination=self._source_subfolder)
        download(self, filename="LICENSE", **source['license'])

    def package(self):

        copy(self, "LICENSE", dst="licenses")
        copy(self, "*.h", dst="include", src=join(self._source_subfolder, "Include"))

        if self.settings.arch == "x86_64":
            copy(self, "*.lib", dst="lib", src=join(self._source_subfolder, "Lib", "x64"))
        elif self.settings.arch == "armv8":
            copy(self, "*.lib", dst="lib", src=join(self._source_subfolder, "Lib", "ARM64"))
        else:
            copy(self, "*.lib", dst="lib", src=join(self._source_subfolder, "Lib"))

    def package_info(self):
        self.cpp_info.libs = self.collect_libs()

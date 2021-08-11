from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class LinuxHeadersGenericConan(ConanFile):
    name = "linux-headers-generic"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.kernel.org/"
    license = "GPL-2.0-only"
    description = "Generic Linux kernel headers"
    topics = ("linux", "headers", "generic")
    settings = "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        self.build_requires("make/4.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        with tools.chdir(os.path.join(self._source_subfolder)):
            self.run("{} headers".format(tools.get_env("CONAN_MAKE_PROGRAM")))

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("include/*.h", src=os.path.join(self._source_subfolder, "usr"))

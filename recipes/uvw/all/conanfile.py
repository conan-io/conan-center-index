import os
import glob
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class UvwConan(ConanFile):
    name = "uvw"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/skypjack/uvw"
    license = "MIT"
    description = "Header-only, event based, tiny and easy to use libuv wrapper in modern C++."
    topics = (
        "conan",
        "uvw",
        "libuv",
        "io",
        "networking",
        "header-only",
    )
    no_copy_source = True
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _supported_compiler(self):
        compiler = str(self.settings.compiler)
        version = tools.Version(self.settings.compiler.version)
        if compiler == "Visual Studio" and version >= "15":
            return True
        if compiler == "gcc" and version >= "7":
            return True
        if compiler == "clang" and version >= "5":
            return True
        if compiler == "apple-clang" and version >= "10":
            return True
        return False

    def requirements(self):
        if tools.Version(self.version) >= "2.6" and tools.Version(self.version) < "2.7":
            self.requires("libuv/1.38.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        archive_name = glob.glob("{}-{}_libuv-*".format(self.name, self.version))[0]
        os.rename(archive_name, self._source_subfolder)

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        if not self._supported_compiler:
            raise ConanInvalidConfiguration("uvw requires C++17. {} {} does not support it.".format(str(self.settings.compiler), self.settings.compiler.version))

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "src"))
        self.copy("*", dst=os.path.join("include", "uvw"), src=os.path.join(self._source_subfolder, "src", "uvw"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

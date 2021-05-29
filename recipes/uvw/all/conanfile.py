import os
import glob
import re
from conans import ConanFile, tools
from conans.errors import ConanException, ConanInvalidConfiguration


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

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        if not self._supported_compiler:
            raise ConanInvalidConfiguration("uvw requires C++17. {} {} does not support it.".format(str(self.settings.compiler), self.settings.compiler.version))

    @property
    def _required_EXACT_libuv_version(self):
        """ Return *EXACT* libuv version to use with this uvw library """
        match = re.match(r".*libuv[_-]v([0-9]+\.[0-9]+).*", self.conan_data["sources"][self.version]["url"])
        if not match:
            raise ConanException("uvw recipe does not know what version of libuv to use as dependency")
        return tools.Version(match.group(1))

    def requirements(self):
        libuv_version = self._required_EXACT_libuv_version
        self.requires("libuv/{}.{}.0".format(libuv_version.major, libuv_version.minor))

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        archive_name = glob.glob("{}-{}_libuv*".format(self.name, self.version))[0]
        os.rename(archive_name, self._source_subfolder)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "src"))
        self.copy("*", dst=os.path.join("include", "uvw"), src=os.path.join(self._source_subfolder, "src", "uvw"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        # Check whether the version of libuv used as a requirement is ok
        required_version = self._required_EXACT_libuv_version
        tuple_exact = (required_version.major, required_version.minor)

        current_version = tools.Version(self.deps_cpp_info["libuv"].version)
        tuple_current = (current_version.major, current_version.minor)

        if tuple_exact != tuple_current:
            raise ConanException("This version of uvw requires an exact libuv version as dependency: {}.{}".format(required_version.major, required_version.minor))

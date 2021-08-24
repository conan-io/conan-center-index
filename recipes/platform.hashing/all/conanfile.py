from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PlatformInterfacesConan(ConanFile):
    name = "platform.hashing"
    license = "LGPL-3.0-only"
    homepage = "https://github.com/linksplatform/Hashing"
    url = "https://github.com/conan-io/conan-center-index"
    description = "platform.hashing is one of the libraries of the LinksPlatform modular framework, " \
                  "which contains std::hash specializations for:\n" \
                  " - trivial and standard-layout types\n" \
                  " - types constrained by std::ranges::range\n" \
                  " - std::any"
    topics = ("linksplatform", "cpp20", "hashing", "any", "ranges", "native")
    settings = "compiler", "arch"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _internal_cpp_subfolder(self):
        return os.path.join(self._source_subfolder, "cpp", "Platform.Hashing")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "Visual Studio": "16",
            "clang": "11",
            "apple-clang": "11"
        }

    @property
    def _minimum_cpp_standard(self):
        return 20

    def validate(self):
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))

        if not minimum_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))

        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("{}/{} requires c++{}, "
                                            "which is not supported by {} {}.".format(
                self.name, self.version, self._minimum_cpp_standard, self.settings.compiler,
                self.settings.compiler.version))

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)

        if self.settings.arch in ("x86", ):
            raise ConanInvalidConfiguration("{} does not support arch={}".format(self.name, self.settings.arch))

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*.h", dst="include", src=self._internal_cpp_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libdirs = []
        suggested_flags = ""
        if self.settings.compiler != "Visual Studio":
            suggested_flags = {
                "x86_64": "-march=haswell",
                "armv7": "-march=armv7",
                "armv8": "-march=armv8-a",
            }.get(str(self.settings.arch), "")
        self.user_info.suggested_flags = suggested_flags

        if "-march" not in "{} {}".format(tools.get_env("CPPFLAGS", ""), tools.get_env("CXXFLAGS", "")):
            self.output.warn("platform.hashing needs to have `-march=ARCH` added to CPPFLAGS/CXXFLAGS. "
                             "A suggestion is available in deps_user_info[{name}].suggested_flags.".format(name=self.name))

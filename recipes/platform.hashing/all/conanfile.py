from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PlatformInterfacesConan(ConanFile):
    name = "platform.hashing"
    license = "LGPL-3.0-only"
    homepage = "https://github.com/linksplatform/Hashing"
    url = "https://github.com/conan-io/conan-center-index"
    description = "platform.hashing is one of the libraries of the LinksPlatform modular framework," \
                  "which contains std::hash specializations for:" \
                  "trivial and standard-layout types" \
                  "types constrained by std::ranges::range" \
                  "std::any"
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
            raise ConanInvalidConfiguration("platform.Hashing/{} "
                                            "requires C++{} with {}, "
                                            "which is not supported "
                                            "by {} {}.".format(
                self.version, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler,
                self.settings.compiler.version))

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy("*.h", dst="include", src=self._internal_cpp_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            return

        def check_mfpu_flag(flag, safe=False):
            tabulation = ' ' * 24
            cxxflags = tools.get_env("CXXFLAGS", "")
            if not safe and flag not in cxxflags:
                self.output.warn("`{flag}` not detected in cxxflags.\n "
                                 "{tab}Missing a flag can cause undefined behavior.\n "
                                 "{tab}Flag automatically added: `{flag}`"
                                 .format(flag=flag, tab=tabulation))
                self.cpp_info.cxxflags.append(flag)
            return flag in cxxflags

        if "armv7" in self.settings.arch:
            check_mfpu_flag("-mfpu=neon")
        elif "armv8" in self.settings.arch :
            if not check_mfpu_flag("-march=armv8-a+fp+simd+crypto+crc", safe=True):
                self.output.warn("Consider adding it in your profile `crypto` and/or `crc` for more performance "
                                 "if your architecture does support cryptographic and/or CRC32 extensions")
                check_mfpu_flag("-march=armv8-a+fp+simd")

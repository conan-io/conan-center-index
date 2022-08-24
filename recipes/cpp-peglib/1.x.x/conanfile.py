from conan.tools.microsoft import is_msvc
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.45.0"


class CpppeglibConan(ConanFile):
    name = "cpp-peglib"
    description = "A single file C++11 header-only PEG (Parsing Expression Grammars) library."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yhirose/cpp-peglib"
    topics = ("peg", "parser", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15.7",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10"
        }

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 17)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{} {} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name, self.version))
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("{} {} requires C++17, which your compiler does not support.".format(self.name, self.version))

        if self.settings.compiler == "clang" and tools.scm.Version(self.settings.compiler.version) == "7" and \
           tools.stdcpp_library(self) == "stdc++":
            raise ConanInvalidConfiguration("{} {} does not support clang 7 with libstdc++.".format(self.name, self.version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("peglib.h", dst="include", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
            self.cpp_info.cxxflags.append("-pthread")
            self.cpp_info.exelinkflags.append("-pthread")
            self.cpp_info.sharedlinkflags.append("-pthread")
        if is_msvc(self):
            self.cpp_info.cxxflags.append("/Zc:__cplusplus")

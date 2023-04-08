from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.50.0"


class TaoCPPPEGTLConan(ConanFile):
    name = "taocpp-pegtl"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/pegtl"
    description = "Parsing Expression Grammar Template Library"
    topics = ("peg", "header-only", "cpp",
              "parsing", "cpp17", "cpp11", "grammar")
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "boost_filesystem": [True, False],
    }
    default_options = {
        "boost_filesystem": False,
    }

    def requirements(self):
        if self.options.boost_filesystem:
            self.requires("boost/1.78.0")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7" if self.options.boost_filesystem else "8",
            "Visual Studio": "15.7",
            "clang": "6.0",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "17")

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(f"{self.ref} requires C++17, which your compiler does not support.")

        compiler_version = Version(self.settings.compiler.version)
        if self.version == "3.0.0" and self.settings.compiler == "clang" and \
           compiler_version >= "10" and compiler_version < "12":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support filesystem experimental")

        if self.options.boost_filesystem and (self.dependencies["boost"].options.header_only or self.dependencies["boost"].options.without_filesystem):
            raise ConanInvalidConfiguration("{self.ref} requires non header-only boost with filesystem component")

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "pegtl")
        self.cpp_info.set_property("cmake_target_name", "taocpp::pegtl")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        if self.options.boost_filesystem:
            self.cpp_info.components["_taocpp-pegtl"].requires.append("boost::filesystem")
            self.cpp_info.components["_taocpp-pegtl"].defines.append("TAO_PEGTL_BOOST_FILESYSTEM")
        else:
            compiler_version = Version(self.settings.compiler.version)
            if self.settings.compiler == "clang" and compiler_version >= "10" and compiler_version < "12":
                self.cpp_info.components["_taocpp-pegtl"].defines.append("TAO_PEGTL_STD_EXPERIMENTAL_FILESYSTEM")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "pegtl"
        self.cpp_info.filenames["cmake_find_package_multi"] = "pegtl"
        self.cpp_info.names["cmake_find_package"] = "taocpp"
        self.cpp_info.names["cmake_find_package_multi"] = "taocpp"
        self.cpp_info.components["_taocpp-pegtl"].names["cmake_find_package"] = "pegtl"
        self.cpp_info.components["_taocpp-pegtl"].names["cmake_find_package_multi"] = "pegtl"
        self.cpp_info.components["_taocpp-pegtl"].set_property("cmake_target_name", "taocpp::pegtl")

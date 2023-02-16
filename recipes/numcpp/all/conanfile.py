from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class NumCppConan(ConanFile):
    name = "numcpp"
    description = "A Templatized Header Only C++ Implementation of the Python NumPy Library"
    topics = ("python", "numpy", "numeric")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dpilger26/NumCpp"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_boost" : [True, False],
        "threads" : [True, False],
    }
    default_options = {
        "with_boost" : True,
        "threads" : False,
    }

    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 14 if Version(self.version) < "2.9.0" else 17

    @property
    def _compilers_minimum_version(self):
        if self._min_cppstd == 14:
            return {
                "gcc": "5",
                "clang": "3.4",
                "apple-clang": "10",
                "Visual Studio": "14",
                "msvc": "190",
            }
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def config_options(self):
        if Version(self.version) < "2.5.0":
            del self.options.with_boost
            self.options.threads = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_boost", True):
            self.requires("boost/1.80.0", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "NumCpp")
        self.cpp_info.set_property("cmake_target_name", "NumCpp::NumCpp")
        if self.options.get_safe("with_boost", True):
            self.cpp_info.requires = ["boost::headers"]
        else:
            self.cpp_info.defines.append("NUMCPP_NO_USE_BOOST")

        if Version(self.version) < "2.5.0" and not self.options.threads:
            self.cpp_info.defines.append("NO_MULTITHREAD")
        if Version(self.version) >= "2.5.0" and self.options.threads:
            self.cpp_info.defines.append("NUMCPP_USE_MULTITHREAD")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "NumCpp"
        self.cpp_info.names["cmake_find_package_multi"] = "NumCpp"

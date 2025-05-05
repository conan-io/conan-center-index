from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "libinterpolate"
    description = "A C++ interpolation library with a simple interface that supports multiple interpolation methods."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CD3/libInterpolate"
    topics = ("math", "spline", "interpolation", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "7",
            "clang": "4",
            "apple-clang": "10",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.80.0", transitive_headers=True)
        self.requires("eigen/3.3.7", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if Version(self.version) < "2.6.4" and self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported by {self.settings.os}; Try the version >= 2.6.4")
        if Version(self.version) >= "2.6.4" and self.settings.os not in ["Linux", "Windows"]:
            raise ConanInvalidConfiguration(f"{self.ref} is not supported by {self.settings.os}.")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False
        )
        if (
            minimum_version
            and Version(self.settings.compiler.version) < minimum_version
        ):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(
            self,
            pattern="LICENSE.md",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "src"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "libInterpolate")
        self.cpp_info.set_property(
            "cmake_target_name", "libInterpolate::Interpolate"
        )

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "libInterpolate"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libInterpolate"
        self.cpp_info.names["cmake_find_package"] = "libInterpolate"
        self.cpp_info.names["cmake_find_package_multi"] = "libInterpolate"
        self.cpp_info.components["Interpolate"].names["cmake_find_package"] = "Interpolate"
        self.cpp_info.components["Interpolate"].names["cmake_find_package_multi"] = "Interpolate"
        self.cpp_info.components["Interpolate"].requires = ["eigen::eigen","boost::boost"]

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"


class MBitsMstchConan(ConanFile):
    name = "mbits-mstch"
    description = "libmstch implemented in terms of C++17 variant."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mbits-libs/libmstch"
    topics = ("parser", "mstch", "mustache", "libmstch", "libmstch-parser")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "clang": "12",
            "msvc": "192",
            "apple-clang": "11.0.3",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192)
        if not is_msvc(self):
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

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["mstch"]

        self.cpp_info.set_property("cmake_file_name", "mbits-mstch")
        self.cpp_info.set_property("cmake_target_name", "mbits::mstch")

        self.cpp_info.filenames["cmake_find_package"] = "mbits-mstch"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mbits-mstch"
        self.cpp_info.names["cmake_find_package"] = "mbits"
        self.cpp_info.names["cmake_find_package_multi"] = "mbits"
        self.cpp_info.components["mstch"].set_property(
            "cmake_target_name", "mbits::mstch"
        )
        self.cpp_info.components["mstch"].libs = ["mstch"]

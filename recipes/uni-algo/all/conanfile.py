from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import export_conandata_patches, get, copy, rmdir
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"


class UniAlgoConan(ConanFile):
    name = "uni-algo"
    package_type = "library"
    description = "Unicode Algorithms Implementation for C/C++"
    license = ("MIT", "Unlicense")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/uni-algo/uni-algo"
    topics = ("unicode", "utf-8", "utf-16", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "191",
            "gcc": "7",
            "clang": "8",
            "apple-clang": "11",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            self.options.rm_safe("fPIC")
            self.options.rm_safe("shared")
        elif self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        if self.options.header_only:
            basic_layout(self, src_folder="src")
        else:
            cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )
        else:
            check_min_vs(self, int(self._compilers_minimum_version["msvc"]))
            if self.options.get_safe("shared"):
                raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["UNI_ALGO_HEADER_ONLY"] = self.options.header_only
        tc.generate()

    def build(self):
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.options.header_only:
            copy(
                self,
                pattern="*.h",
                dst=os.path.join(self.package_folder, "include"),
                src=os.path.join(self.source_folder, "include"),
            )
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        if self.options.header_only:
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []
        else:
            if self.settings.build_type == "Debug":
                if Version(self.version) < "0.7":
                    self.cpp_info.libs = [f"{self.name}d"]
                else:
                    self.cpp_info.libs = [f"{self.name}-debug"]
            else:
                self.cpp_info.libs = [f"{self.name}"]

        # see https://github.com/uni-algo/uni-algo/blob/v0.7.1/CMakeLists.txt#L75-L109
        self.cpp_info.set_property("cmake_file_name", f"{self.name}")
        self.cpp_info.set_property("cmake_target_name", f"{self.name}::{self.name}")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = f"{self.name}"
        self.cpp_info.filenames["cmake_find_package_multi"] = f"{self.name}"
        self.cpp_info.names["cmake_find_package"] = f"{self.name}"
        self.cpp_info.names["cmake_find_package_multi"] = f"{self.name}"

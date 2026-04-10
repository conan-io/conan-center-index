from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2"


class TaskflowConan(ConanFile):
    name = "taskflow"
    description = (
        "A fast C++ header-only library to help you quickly write parallel "
        "programs with complex task dependencies."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taskflow/taskflow"
    topics = ("tasking", "parallelism", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return "20" if Version(self.version) >= "4.0.0" else "17"

    @property
    def _compilers_minimum_version(self):
        if Version(self.version) >= "4.0.0":
            return {
                "Visual Studio": "16",
                "msvc": "192",
                "gcc": "11",
                "clang": "12",
                "apple-clang": "13",
            }
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "7.3" if Version(self.version) < "3.7.0" else "8.4",
            "clang": "6.0",
            "apple-clang": "10.0",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*",
                  src=os.path.join(self.source_folder, "taskflow"),
                  dst=os.path.join(self.package_folder, "include", "taskflow"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "Taskflow")
        self.cpp_info.set_property("cmake_target_name", "Taskflow::Taskflow")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        if is_msvc(self):
            self.cpp_info.defines.append("_ENABLE_EXTENDED_ALIGNED_STORAGE")

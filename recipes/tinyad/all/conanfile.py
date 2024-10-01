from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.52.0"


class TinyADConan(ConanFile):
    name = "tinyad"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/patr-schm/TinyAD"
    description = "TinyAD is a C++ header-only library for second-order automatic differentiation"
    topics = ("algebra", "linear-algebra", "optimization", "autodiff", "numerical", "header-only")
    package_type = "header-library"
    license = ("MIT")
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires("eigen/3.4.0")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def package(self):
        # The project has a CMakelists.txt file, but it doesn't have "install" logic
        # so we just copy the headers to the package folder
        copy(self, "include/**", src=self.source_folder, dst=self.package_folder)
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TinyAD")
        self.cpp_info.set_property("cmake_target_name", "TinyAD")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if is_msvc(self):
            # https://github.com/patr-schm/TinyAD/blob/29417031c185b6dc27b6d4b684550d844459b735/CMakeLists.txt#L35
            self.cpp_info.cxxflags.append("/bigobj")

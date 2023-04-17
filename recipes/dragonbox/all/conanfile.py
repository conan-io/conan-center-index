from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

import os


required_conan_version = ">=1.53.0"


class DragonboxConan(ConanFile):
    name = "dragonbox"
    description = "Reference implementation of Dragonbox in C++"
    license = ("Apache-2.0", "LLVM-exception", "BSL-1.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jk-jeon/dragonbox"
    topics = ("float-to-string", "grisu", "grisu-exact")
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
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
            if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["DRAGONBOX_INSTALL_TO_CHARS"] = True
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_module_file_name", "dragonbox")
        self.cpp_info.components["_dragonbox"].set_property("cmake_target_name", "dragonbox::dragonbox")
        self.cpp_info.components["dragonbox_to_chars_headers"].set_property("cmake_target_name", "dragonbox::dragonbox_to_chars")
        self.cpp_info.components["dragonbox_to_chars_headers"].libs = ["dragonbox_to_chars"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "dragonbox"
        self.cpp_info.filenames["cmake_find_package_multi"] = "dragonbox"
        self.cpp_info.names["cmake_find_package"] = "dragonbox"
        self.cpp_info.names["cmake_find_package_multi"] = "dragonbox"
        self.cpp_info.components["_dragonbox"].names["cmake_find_package"] = "dragonbox"
        self.cpp_info.components["_dragonbox"].names["cmake_find_package_multi"] = "dragonbox"
        self.cpp_info.components["dragonbox_to_chars_headers"].names["cmake_find_package"] = "dragonbox_to_chars"
        self.cpp_info.components["dragonbox_to_chars_headers"].names["cmake_find_package_multi"] = "dragonbox_to_chars"

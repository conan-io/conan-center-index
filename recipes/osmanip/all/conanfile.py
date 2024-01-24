from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file, save
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc

import os

required_conan_version = ">=1.53.0"

class OsmanipConan(ConanFile):
    name = "osmanip"
    description = (
        "Library with useful output stream tools like: color and style "
        "manipulators, progress bars and terminal graphics."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/JustWhit3/osmanip"
    topics = ("manipulator", "iostream", "output-stream", "iomanip")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        if Version(self.version) < "4.5.0":
            copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # https://github.com/JustWhit3/osmanip/commit/43c8bd8d018fcb3bce6443f7388e042d5457d4fb
        if Version(self.version) < "4.6.0":
            # osmanip/progressbar/progress_bar.hpp includes arsenalgear/constants.hpp
            self.requires("arsenalgear/2.1.1", transitive_headers=True)

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compiler_required_cpp17(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
        }

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compiler_required_cpp17.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if Version(self.version) >= "4.4.0" and self.settings.get_safe("compiler.libcxx") == "libstdc++":
            # test_package segfaults with libstdc++ for some reason
            raise ConanInvalidConfiguration("osmanip >= 4.4.0 doesn't support libstdc++")

        if is_msvc(self):
            raise ConanInvalidConfiguration("MSVC is not yet supported by osmanip recipe. Contributions are welcome.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "4.5.0":
            tc.variables["OSMANIP_VERSION"] = str(self.version)
        else:
            tc.variables["OSMANIP_TESTS"] = False
            tc.variables["FORMAT"] = False
            tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        if Version(self.version) >= "4.5.0":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            " STATIC ", " ")
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "    DESTINATION lib\n",
                            "    RUNTIME DESTINATION bin LIBRARY DESTINATION lib ARCHIVE DESTINATION lib\n")
        save(self, os.path.join(self.source_folder, "examples", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "deps", "doctest", "CMakeLists.txt"), "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["osmanip"]

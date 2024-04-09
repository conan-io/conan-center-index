from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, rm
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class FTXUIConan(ConanFile):
    name = "ftxui"
    description = "C++ Functional Terminal User Interface."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ArthurSonzogni/FTXUI"
    topics = ("ncurses", "terminal", "screen", "tui")
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

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
			"gcc": "8",
			"clang": "7",
			"apple-clang": "12",
			"Visual Studio": "16",
			"msvc": "192",
		}

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if is_msvc(self) and self.options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("shared with static runtime not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # BUILD_SHARED_LIBS and POSITION_INDEPENDENT_CODE are automatically parsed when self.options.shared or self.options.fPIC exist
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["FTXUI_BUILD_DOCS"] = False
        tc.variables["FTXUI_BUILD_EXAMPLES"] = False
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        if Version(self.version) >= "4.1.0":
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if Version(self.version) >= "4.1.1":
            rm(self, "ftxui.pc", os.path.join(self.package_folder, "lib"), )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ftxui")
        if Version(self.version) >= "4.1.0":
            self.cpp_info.set_property("pkg_config_name", "ftxui")

        self.cpp_info.components["ftxui-dom"].set_property("cmake_target_name", "ftxui::dom")
        self.cpp_info.components["ftxui-dom"].libs = ["ftxui-dom"]
        self.cpp_info.components["ftxui-dom"].requires = ["ftxui-screen"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ftxui-dom"].system_libs.append("m")

        self.cpp_info.components["ftxui-screen"].set_property("cmake_target_name", "ftxui::screen")
        self.cpp_info.components["ftxui-screen"].libs = ["ftxui-screen"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ftxui-screen"].system_libs.append("m")

        self.cpp_info.components["ftxui-component"].set_property("cmake_target_name", "ftxui::component")
        self.cpp_info.components["ftxui-component"].libs = ["ftxui-component"]
        self.cpp_info.components["ftxui-component"].requires = ["ftxui-dom"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ftxui-component"].system_libs.append("pthread")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["ftxui-dom"].names["cmake_find_package"] = "dom"
        self.cpp_info.components["ftxui-dom"].names["cmake_find_package_multi"] = "dom"
        self.cpp_info.components["ftxui-screen"].names["cmake_find_package"] = "screen"
        self.cpp_info.components["ftxui-screen"].names["cmake_find_package_multi"] = "screen"
        self.cpp_info.components["ftxui-component"].names["cmake_find_package"] = "component"
        self.cpp_info.components["ftxui-component"].names["cmake_find_package_multi"] = "component"

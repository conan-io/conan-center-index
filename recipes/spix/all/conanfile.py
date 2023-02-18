from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"


class SpixConan(ConanFile):
    name = "spix"
    description = "UI test automation library for QtQuick/QML Apps"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/faaxm/spix"
    topics = ("automation", "qt", "qml", "qt-quick", "qt5", "qtquick", "automated-testing", "qt-qml", "qml-applications")
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
    def _minimum_cpp_standard(self):
        return 14 if self.version == "0.4" else 17

    @property
    def _compilers_minimum_version(self):
        if self.version == "0.4":
            return {
                "Visual Studio": "14",
                "msvc": "190",
                "gcc": "5",
                "clang": "3.4",
                "apple-clang": "10"
            }
        else:
            return {
                "Visual Studio": "15.7",
                "msvc": "192", # FIXME: 15.7 is actually 1914 but needs to be tested
                "gcc": "7",
                "clang": "5",
                "apple-clang": "10",
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

    def requirements(self):
        self.requires("anyrpc/1.0.2")
        self.requires("qt/6.4.2")
        
    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support."
            )

        if Version(self.dependencies["qt"].ref.version).major == 6 and not self.options["qt"].qtshadertools:
            raise ConanInvalidConfiguration(f"{self.ref} requires qt:qtshadertools to get the Quick module")
        if not (self.options["qt"].gui and self.options["qt"].qtdeclarative):
            raise ConanInvalidConfiguration(f"{self.ref} requires qt:gui and qt:qtdeclarative to get the Quick module")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SPIX_BUILD_EXAMPLES"] = False
        tc.variables["SPIX_BUILD_TESTS"] = False
        tc.variables["SPIX_QT_MAJOR"] = Version(self.dependencies["qt"].ref.version).major
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("anyrpc", "cmake_file_name", "AnyRPC")
        deps.set_property("anyrpc", "cmake_target_name", "AnyRPC::anyrpc")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if self.version == "0.4" and Version(self.dependencies["qt"].ref.version).major == 6:
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD 14)", "set(CMAKE_CXX_STANDARD 17)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["Spix"]
        self.cpp_info.set_property("cmake_file_name", "Spix") 
        self.cpp_info.set_property("cmake_target_name", "Spix::Spix")
        
        # TODO remove once conan v2 removed cmake_find_package_*
        self.cpp_info.names["cmake_find_package"] = "Spix"
        self.cpp_info.names["cmake_find_package_multi"] = "Spix"

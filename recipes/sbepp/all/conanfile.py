from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "sbepp"
    description = "C++ implementation of the FIX Simple Binary Encoding"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/OleksandrKvl/sbepp"
    topics = ("trading", "fix", "sbe")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_sbeppc": [True, False]
    }
    default_options = {
        "with_sbeppc": True
    }

    @property
    def _min_cppstd(self):
        if self.options.with_sbeppc:
            return 17
        else:
            return 11

    @property
    def _compilers_minimum_version(self):
        if self.options.with_sbeppc:
            return {
                "gcc": "9",
                "clang": "9",
                "apple-clang": "11"
            }
        else:
            return {
                "gcc": "4.8.1",
                "clang": "3.3",
                "apple-clang": "9.4"
            }

    def export_sources(self):
        copy(self, os.path.join("cmake", "sbeppcTargets.cmake"),
            self.recipe_folder, self.export_sources_folder)
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if not self.info.options.with_sbeppc:
            self.info.clear()
        else:
            del self.info.settings.compiler

    def requirements(self):
        if self.options.with_sbeppc:
            # sbepp/<1.1.0 requires fmt and pugixml with hardcoded versions
            if Version(self.version) < "1.1.0":
                self.requires("fmt/9.1.0")
                self.requires("pugixml/1.12.1")
            else:
                self.requires("fmt/10.1.0")
                self.requires("pugixml/1.13")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if not self.options.with_sbeppc:
            tc.variables["SBEPP_BUILD_SBEPPC"] = False

        tc.generate()

        if self.options.with_sbeppc:
            tc = CMakeDeps(self)
            tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        copy(self, "sbeppcTargets.cmake",
            src=os.path.join(self.source_folder, os.pardir, "cmake"),
            dst=os.path.join(self.package_folder, self._module_path))

    @property
    def _module_path(self):
        return os.path.join("lib", "cmake")

    def package_info(self):
        # provide sbepp::sbeppc target
        build_modules = [
            os.path.join(self._module_path, "sbeppcTargets.cmake")
        ]
        self.cpp_info.builddirs.append(self._module_path)
        self.cpp_info.set_property("cmake_build_modules", build_modules)

        # TODO: to remove in conan v2
        if self.options.with_sbeppc:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

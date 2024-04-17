from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.apple import is_apple_os
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches
import os

required_conan_version = ">=1.53.0"

class LibassertConan(ConanFile):
    name = "libassert"
    description = "The most over-engineered and overpowered C++ assertion library."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jeremy-rifkin/libassert"
    package_type = "library"

    topics = ("assert", "library", "assertions", "stacktrace")
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
            "clang": "9"
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) >= "1.2.2":
            self.requires("cpptrace/0.3.1")
        elif Version(self.version) >= "1.2.1":
            self.requires("cpptrace/0.2.1")

    def validate(self):
        if is_apple_os(self):
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on Mac. Please, update to version >=2.0.0")

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)

        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)

        if not self.options.shared:
            tc.variables["ASSERT_STATIC"] = True
        tc.variables["ASSERT_USE_EXTERNAL_CPPTRACE"] = True
        deps = CMakeDeps(self)
        deps.generate()

        tc.generate()

    def build(self):
        apply_conandata_patches(self)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        if self.settings.os == "Windows" and self.options.shared:
            copy(
                self,
                "*.dll",
                src=self.build_folder,
                dst=os.path.join(self.package_folder, "bin"),
                keep_path=False
            )

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["assert"]

        self.cpp_info.set_property("cmake_file_name", "assert")
        self.cpp_info.set_property("cmake_target_name", "assert::assert")

        # the first version of this library used assert/assert as include folder
        # appending this one but not removing the default to not break consumers
        self.cpp_info.includedirs.append(os.path.join("include", "assert"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "assert"
        self.cpp_info.filenames["cmake_find_package_multi"] = "assert"
        self.cpp_info.names["cmake_find_package"] = "assert"
        self.cpp_info.names["cmake_find_package_multi"] = "assert"
        
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        if Version(self.version) < "1.2.1":
            # pre-cpptrace
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.append("dl")
            if self.settings.os == "Windows":
                self.cpp_info.system_libs.append("dbghelp")

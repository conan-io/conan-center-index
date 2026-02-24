from conan import ConanFile
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
import os

required_conan_version = ">=2.1"

class LibassertConan(ConanFile):
    name = "libassert"
    description = "The most over-engineered C++ assertion library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jeremy-rifkin/libassert"
    topics = ("assert", "library", "assertions", "stacktrace", "diagnostics", "defensive programming", "testing")
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpptrace/[>=1.0.4 <2]", transitive_headers=True, transitive_libs=True)

    def validate(self):
        check_min_cppstd(self, 17)
        check_min_vs(self, 192)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)

        tc.variables["LIBASSERT_USE_EXTERNAL_CPPTRACE"] = True
        deps = CMakeDeps(self)
        deps.generate()

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libassert")
        self.cpp_info.set_property("cmake_target_name", "libassert::assert")
        self.cpp_info.libs = ["assert"]

        # the first version of this library used assert/assert as include folder
        # appending this one but not removing the default to not break consumers
        self.cpp_info.includedirs.append(os.path.join("include", "libassert"))

        if not self.options.shared:
            self.cpp_info.defines.append("LIBASSERT_STATIC_DEFINE")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

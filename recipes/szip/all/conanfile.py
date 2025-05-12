from conan import ConanFile
from conan.errors import ConanException
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, collect_libs, get, copy, replace_in_file
from conan.tools.build import cross_building
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class SzipConan(ConanFile):
    name = "szip"
    description = "C Implementation of the extended-Rice lossless compression " \
                  "algorithm, suitable for use with scientific data."
    license = "Szip License"
    topics = "compression", "decompression"
    homepage = "https://support.hdfgroup.org/doc_resource/SZIP/"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_encoding": [True, False],
        "enable_large_file": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_encoding": False,
        "enable_large_file": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                              "set (CMAKE_POSITION_INDEPENDENT_CODE ON)", "")
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SZIP_ENABLE_ENCODING"] = self.options.enable_encoding
        tc.variables["SZIP_EXTERNALLY_CONFIGURED"] = True
        tc.variables["BUILD_TESTING"] = False
        tc.variables["SZIP_BUILD_FRAMEWORKS"] = False
        tc.variables["SZIP_PACK_MACOSX_FRAMEWORK"] = False
        tc.variables["SZIP_ENABLE_LARGE_FILE"] = self.options.enable_large_file
        if cross_building(self, skip_x64_x86=True) and self.options.enable_large_file:
            # Assume it works, otherwise raise in 'validate' function
            tc.variables["TEST_LFS_WORKS_RUN"] = True
            tc.variables["TEST_LFS_WORKS_RUN__TRYRUN_OUTPUT"] = True
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        if Version(self.version) > "2.1.1": # pylint: disable=conan-unreachable-upper-version
            raise ConanException("CMAKE_POLICY_VERSION_MINIMUM hardcoded to 3.5, check if new version supports CMake 4")
        tc.generate()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "szip")
        self.cpp_info.set_property("cmake_target_name", "szip-shared" if self.options.shared else "szip-static")
        self.cpp_info.libs = collect_libs(self)

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m"])

        if self.options.shared:
            self.cpp_info.defines.append("SZ_BUILT_AS_DYNAMIC_LIB=1")

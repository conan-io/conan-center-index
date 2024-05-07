from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os

required_conan_version = ">=1.54.0"


class OpenclIcdLoaderConan(ConanFile):
    name = "opencl-icd-loader"
    description = "OpenCL ICD Loader."
    license = "Apache-2.0"
    topics = ("opencl", "khronos", "parallel", "icd-loader")
    homepage = "https://github.com/KhronosGroup/OpenCL-ICD-Loader"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_openclon12": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_openclon12": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.disable_openclon12

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"opencl-headers/{self.version}", transitive_headers=True)
        self.requires(f"opencl-clhpp-headers/{self.version}", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        opencl_headers_includedirs = self.dependencies["opencl-headers"].cpp_info.aggregated_components().includedirs
        tc.cache_variables["OPENCL_ICD_LOADER_HEADERS_DIR"] = ";".join(opencl_headers_includedirs)
        if is_msvc(self):
            tc.variables["USE_DYNAMIC_VCXX_RUNTIME"] = not is_msvc_static_runtime(self)
        tc.variables["OPENCL_ICD_LOADER_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["OPENCL_ICD_LOADER_BUILD_TESTING"] = False
        if self.settings.os == "Windows":
            tc.variables["OPENCL_ICD_LOADER_DISABLE_OPENCLON12"] = self.options.disable_openclon12
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "OpenCL")
        self.cpp_info.set_property("cmake_file_name", "OpenCLICDLoader")
        self.cpp_info.set_property("cmake_target_name", "OpenCL::OpenCL")
        self.cpp_info.includedirs = []
        self.cpp_info.libs = ["OpenCL"]
        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs = ["dl", "pthread"]
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs = ["cfgmgr32", "runtimeobject"]

        # TODO: to remove in conan v2
        self.cpp_info.filenames["cmake_find_package"] = "OpenCL"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCLICDLoader"
        self.cpp_info.names["cmake_find_package"] = "OpenCL"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenCL"

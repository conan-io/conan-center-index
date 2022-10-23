from conan import ConanFile, conan_version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


class OpenclIcdLoaderConan(ConanFile):
    name = "opencl-icd-loader"
    description = "OpenCL ICD Loader."
    license = "Apache-2.0"
    topics = ("opencl", "khronos", "parallel", "icd-loader")
    homepage = "https://github.com/KhronosGroup/OpenCL-ICD-Loader"
    url = "https://github.com/conan-io/conan-center-index"

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
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"opencl-headers/{self.version}", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["OPENCL_ICD_LOADER_HEADERS_DIR"] = ";".join(self.deps_cpp_info["opencl-headers"].include_paths)
        if is_msvc(self):
            tc.variables["USE_DYNAMIC_VCXX_RUNTIME"] = not is_msvc_static_runtime(self)
        tc.variables["OPENCL_ICD_LOADER_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["OPENCL_ICD_LOADER_BUILD_TESTING"] = False
        if self.settings.os == "Windows":
            tc.variables["OPENCL_ICD_LOADER_DISABLE_OPENCLON12"] = self.options.disable_openclon12
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
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

        if Version(conan_version).major < 2:
            self.cpp_info.filenames["cmake_find_package"] = "OpenCL"
            self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCLICDLoader"
            self.cpp_info.names["cmake_find_package"] = "OpenCL"
            self.cpp_info.names["cmake_find_package_multi"] = "OpenCL"

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os


required_conan_version = ">=2.0.9"

#
# INFO: Please, remove all comments before pushing your PR!
#


class ExecuTorchConan(ConanFile):
    name = "executorch"
    description = "ExecuTorch is PyTorch's unified solution for deploying AI models on-device"
    # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    # In case not listed there, use "DocumentRef-<license-file-name>:LicenseRef-<package-name>"
    license = "BSD"
    url = "https://github.com/pytorch/executorch"
    homepage = "https://docs.pytorch.org/executorch"
    # no "conan" and project name in topics. Use topics from the upstream listed on GH
    topics = ("topic1", "topic2", "topic3")
    # package_type should usually be "library", "shared-library" or "static-library"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cadence": [True,False],
        "cortex_m": [True,False],
        "mps": [True,False],
        "neutron": [True,False],
        "openvino": [True,False],
        "qnn": [True,False],
        "vgf": [True,False],
        "vulkan": [True,False],
        "xnnpack": [True,False],
        "logging": [True,False],
        "log_level": ["debug", "info", "error","fatal"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cadence": False,
        "cortex_m": False,
        "mps": False,
        "neutron": False,
        "openvino": False,
        "qnn": False,
        "vgf": False,
        "vulkan": True,
        "xnnpack": True,
        "logging": False,
        "log_level": "debug"
    }
    # In case having config_options() or configure() method, the logic should be moved to the specific methods.
    implements = ["auto_shared_fpic"]

    # no exports_sources attribute, but export_sources(self) method instead
    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        # Keep this logic only in case configure() is needed e.g pure-c project.
        # Otherwise remove configure() and auto_shared_fpic will manage it.
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # for plain C projects only
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        pass

    def validate(self):
        # validate the minimum cpp standard supported. For C++ projects only.
        check_min_cppstd(self, 17)
        # in case it does not work in another configuration, it should be validated here. Always comment the reason including the upstream issue.
        # INFO: Upstream does not support DLL: See <URL>
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    # if a tool other than the compiler or CMake newer than 3.15 is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <3.29]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Using patches is always the last resort to fix issues. If possible, try to fix the issue in the upstream project.
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["EXECUTORCH_BUILD_CADENCE"] = self.options.cadence
        tc.cache_variables["EXECUTORCH_BUILD_COREML"] = self.options.coreml
        tc.cache_variables["EXECUTORCH_BUILD_CORTEX_M"] = self.options.cortex_m
        tc.cache_variables["EXECUTORCH_BUILD_MPS"] = self.options.mps
        tc.cache_variables["EXECUTORCH_BUILD_NEURON"] = self.options.neuron
        tc.cache_variables["EXECUTORCH_BUILD_OPENVINO"] = self.options.openvino
        tc.cache_variables["EXECUTORCH_BUILD_QNN"] = self.options.qnn
        tc.cache_variables["EXECUTORCH_BUILD_VGF"] = self.options.vgf
        tc.cache_variables["EXECUTORCH_BUILD_VULKAN"] = self.options.vulkan
        tc.cache_variables["EXECUTORCH_BUILD_XNNPACK"] = self.options.xnnpack

        if is_msvc(self):
            tc.cache_variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.generate()

        # # In case there are dependencies listed under requirements, CMakeDeps should be used
        # deps = CMakeDeps(self)
        # # You can override the CMake package and target names if they don't match the names used in the project
        # deps.set_property("fontconfig", "cmake_file_name", "Fontconfig")
        # deps.set_property("fontconfig", "cmake_target_name", "Fontconfig::Fontconfig")
        # deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        # Some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        # Consider disabling these at first to verify that the package_info() output matches the info exported by the project.
        # rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # rmdir(self, os.path.join(self.package_folder, "share"))
        # rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        # library name to be packaged
        self.cpp_info.libs = ["executorch"]
        # if package provides a CMake config file (package-config.cmake or packageConfig.cmake, with package::package target, usually installed in <prefix>/lib/cmake/<package>/)
        self.cpp_info.set_property("cmake_file_name", "ExecuTorch")
        self.cpp_info.set_property("cmake_target_name", "executorch::executorch")

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")

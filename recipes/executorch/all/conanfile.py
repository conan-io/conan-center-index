import subprocess
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    rm,
    rmdir,
)
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os
from conan.tools.scm import Git


required_conan_version = ">=2.0.9"

#
# INFO: Please, remove all comments before pushing your PR!
#


class ExecuTorchConan(ConanFile):
    name = "executorch"
    description = (
        "ExecuTorch is PyTorch's unified solution for deploying AI models on-device"
    )
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

        # Backends
        "cadence": [True, False],
        "coreml": [True, False],
        "cortex_m": [True, False],
        "mps": [True, False],
        "neuron": [True, False],
        "openvino": [True, False],
        "qnn": [True, False],
        "vgf": [True, False],
        "vulkan": [True, False],
        "xnnpack": [True, False],

        # Extensions
        "extension_apple": [True, False],
        "extension_data_loader": [True, False],
        "extension_flat_tensor": [True, False],
        "extension_llm": [True, False],
        "extension_llm_apple": [True, False],
        "extension_llm_runner": [True, False],
        "extension_module": [True, False],
        "extension_tensor": [True, False],
        "extension_training": [True, False],
        "extension_evalue_util": [True, False],
        "extension_runner_util": [True, False],

        # Logging
        "logging": [True, False],
        "log_level": ["debug", "info", "error", "fatal"],

        "build_executor_runner" :[True,False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,

        # Backends
        "cadence": False,
        "coreml": False,
        "cortex_m": False,
        "mps": False,
        "neuron": False,
        "openvino": False,
        "qnn": False,
        "vgf": False,
        "vulkan": False,
        "xnnpack": True,

        # Extensions
        "extension_apple": False,
        "extension_data_loader": False,
        "extension_flat_tensor": False,
        "extension_llm": False,
        "extension_llm_apple": False,
        "extension_llm_runner": False,
        "extension_module": False,
        "extension_tensor": True,
        "extension_training": False,
        "extension_evalue_util": False,
        "extension_runner_util": False,

        # Logging
        "logging": False,
        "log_level": "debug",

        "build_executor_runner" : False
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
        # src_folder needs to be named "executorch" due to https://github.com/pytorch/executorch/issues/6475
        cmake_layout(self, src_folder="executorch")

    def requirements(self):
        if self.options.vulkan:
            self.requires("vulkan-headers/1.4.313.0")

    def validate(self):
        # validate the minimum cpp standard supported. For C++ projects only.
        # check_min_cppstd(self, 17)
        # in case it does not work in another configuration, it should be validated here. Always comment the reason including the upstream issue.
        # INFO: Upstream does not support DLL: See <URL>
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} can not be built as shared on Visual Studio and msvc."
            )

    # if a tool other than the compiler or CMake newer than 3.15 is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        self.tool_requires("cmake/[>=3.29 <4]")

    def source(self):
        git = Git(self)
        git.clone(url=self.url, target=".")
        git.checkout(f"v{self.version}")
        git.run("submodule update --init --recursive")
        # get(self, **self.conan_data["sources"][self.version], strip_root=True)
        subprocess.check_call(["./install_executorch.sh"], cwd=self.source_folder)
        # subprocess.check_call(["git", "init"],cwd=self.source_folder)
        # subprocess.check_call(["git", "submodule", "update", "--init" ,"--recursive"],cwd=self.source_folder)
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
        tc.cache_variables[
            "EXECUTORCH_BUILD_EXTENSION_APPLE"
        ] = self.options.extension_apple
        tc.cache_variables[
            "EXECUTORCH_BUILD_EXTENSION_DATA_LOADER"
        ] = self.options.extension_data_loader
        tc.cache_variables[
            "EXECUTORCH_BUILD_EXTENSION_FLAT_TENSOR"
        ] = self.options.extension_flat_tensor
        tc.cache_variables[
            "EXECUTORCH_BUILD_EXTENSION_LLM"
        ] = self.options.extension_llm
        tc.cache_variables[
            "EXECUTORCH_BUILD_EXTENSION_LLM_APPLE"
        ] = self.options.extension_llm_apple
        tc.cache_variables[
            "EXECUTORCH_BUILD_EXTENSION_LLM_RUNNER"
        ] = self.options.extension_llm_runner
        tc.cache_variables[
            "EXECUTORCH_BUILD_EXTENSION_MODULE"
        ] = self.options.extension_module
        tc.cache_variables[
            "EXECUTORCH_BUILD_EXTENSION_TENSOR"
        ] = self.options.extension_tensor
        tc.cache_variables[
            "EXECUTORCH_BUILD_EXTENSION_TRAINING"
        ] = self.options.extension_training
        tc.cache_variables[
            "EXECUTORCH_BUILD_EXTENSION_EVALUE_UTIL"
        ] = self.options.extension_evalue_util
        tc.cache_variables[
            "EXECUTORCH_BUILD_EXTENSION_RUNNER_UTIL"
        ] = self.options.extension_runner_util

        tc.cache_variables["EXECUTORCH_BUILD_EXECUTOR_RUNNER"] = self.options.build_executor_runner

        if is_msvc(self):
            tc.cache_variables[
                "USE_MSVC_RUNTIME_LIBRARY_DLL"
            ] = not is_msvc_static_runtime(self)
        tc.generate()

        # # In case there are dependencies listed under requirements, CMakeDeps should be used
        deps = CMakeDeps(self)
        # # You can override the CMake package and target names if they don't match the names used in the project
        # deps.set_property("fontconfig", "cmake_file_name", "Fontconfig")
        # deps.set_property("fontconfig", "cmake_target_name", "Fontconfig::Fontconfig")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()

        # Some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        # Consider disabling these at first to verify that the package_info() output matches the info exported by the project.
        # rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # rmdir(self, os.path.join(self.package_folder, "share"))
        # rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        # Match the installed config name: lib/cmake/ExecuTorch/executorch-config.cmake
        self.cpp_info.set_property("cmake_file_name", "executorch")

        #
        # --- Core libraries (always installed) ---
        #

        core = self.cpp_info.components["executorch_core"]
        core.libs = ["executorch_core"]
        core.set_property("cmake_target_name", "executorch_core")

        main = self.cpp_info.components["executorch"]
        main.libs = ["executorch"]
        main.requires = ["executorch_core"]
        main.set_property("cmake_target_name", "executorch::executorch")

        #
        # --- Backend interface umbrella (always installed) ---
        #

        backends = self.cpp_info.components["executorch_backends"]
        backends.libs = []  # Interface target
        backends.set_property("cmake_target_name", "executorch::backends")

        #
        # --- Extensions interface umbrella (always installed) ---
        #

        extensions = self.cpp_info.components["executorch_extensions"]
        extensions.libs = []  # Interface target
        extensions.set_property("cmake_target_name", "executorch::extensions")

        #
        # --- Kernels interface umbrella (always installed) ---
        #

        kernels = self.cpp_info.components["executorch_kernels"]
        kernels.libs = []  # Interface target
        kernels.set_property("cmake_target_name", "executorch::kernels")


        #
        # ---------- OPTIONAL BACKEND TARGETS ----------
        #
        # These are installed only if the corresponding option is ON.
        #

        if self.options.xnnpack:
            c = self.cpp_info.components["xnnpack_backend"]
            c.libs = ["xnnpack_backend"]
            backends.requires.append("xnnpack_backend")

        if self.options.vulkan:
            for name in ["vulkan_backend", "vulkan_schema"]:
                c = self.cpp_info.components[name]
                c.libs = [name]
                c.set_property("cmake_target_name", name)
                backends.requires.append(name)

        if self.options.coreml:
            c = self.cpp_info.components["coremldelegate"]
            c.libs = ["coremldelegate"]
            backends.requires.append("coremldelegate")

        if self.options.mps:
            c = self.cpp_info.components["mpsdelegate"]
            c.libs = ["mpsdelegate"]
            backends.requires.append("mpsdelegate")

        if self.options.neuron:
            c = self.cpp_info.components["neuron_backend"]
            c.libs = ["neuron_backend"]
            backends.requires.append("neuron_backend")

        if self.options.openvino:
            c = self.cpp_info.components["openvino_backend"]
            c.libs = ["openvino_backend"]
            backends.requires.append("openvino_backend")

        if self.options.qnn:
            c = self.cpp_info.components["qnn_executorch_backend"]
            c.libs = ["qnn_executorch_backend"]
            backends.requires.append("qnn_executorch_backend")

        if self.options.vgf:
            c = self.cpp_info.components["vgf_backend"]
            c.libs = ["vgf_backend"]
            backends.requires.append("vgf_backend")

        # if self.options.cadence:
        #     # Cadence installs targets from its own subdir.
        #     c = self.cpp_info.components["cadence_backend"]
        #     # You'll need to confirm the exact lib name inside backends/cadence
        #     c.libs = ["cadence_ops_lib"]
        #     c.set_property("cmake_target_name", "cadence_ops_lib")
        #     backends.requires.append("cadence_backend")


        #
        # ---------- OPTIONAL EXTENSION TARGETS ----------
        #

        if self.options.extension_data_loader:
            c = self.cpp_info.components["extension_data_loader"]
            c.libs = ["extension_data_loader"]
            extensions.requires.append("extension_data_loader")

        if self.options.extension_flat_tensor:
            c = self.cpp_info.components["extension_flat_tensor"]
            c.libs = ["extension_flat_tensor"]
            extensions.requires.append("extension_flat_tensor")

        if self.options.extension_module:
            c = self.cpp_info.components["extension_module_static"]
            c.libs = ["extension_module_static"]
            extensions.requires.append("extension_module_static")

        if self.options.extension_tensor:
            c = self.cpp_info.components["extension_tensor"]
            c.libs = ["extension_tensor"]
            extensions.requires.append("extension_tensor")

        if self.options.extension_training:
            c = self.cpp_info.components["extension_training"]
            c.libs = ["extension_training"]
            extensions.requires.append("extension_training")

        if self.options.extension_llm:
            c = self.cpp_info.components["tokenizers"]
            c.libs = ["tokenizers"]
            extensions.requires.append("tokenizers")

        if self.options.extension_llm_runner:
            c = self.cpp_info.components["extension_llm_runner"]
            c.libs = ["extension_llm_runner"]
            extensions.requires.append("extension_llm_runner")

        if self.options.extension_runner_util:
            c = self.cpp_info.components["extension_runner_util"]
            c.libs = ["extension_runner_util"]
            extensions.requires.append("extension_runner_util")

        if self.options.extension_evalue_util:
            c = self.cpp_info.components["extension_evalue_util"]
            c.libs = ["extension_evalue_util"]
            # Not added to executorch_extensions by upstream

        # # --- interface umbrella targets from upstream ---
        # for name in ("backends", "extensions", "kernels"):
        #     comp = self.cpp_info.components[name]
        #     # expose exactly: executorch::backends, executorch::extensions, executorch::kernels
        #     comp.set_property("cmake_target_name", f"executorch::{name}")
        #     # When a consumer links an umbrella, make sure the main runtime is in the graph
        #     comp.requires = ["executorch"]

        
         # Common Unix system libs
        if str(self.settings.os) in ["Linux", "FreeBSD"]:
            for name in self.cpp_info.components.keys():
                comp = self.cpp_info.components[name]
                comp.system_libs.extend(["m", "pthread", "dl"])

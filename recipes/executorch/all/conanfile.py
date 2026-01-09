import platform
import shutil
import subprocess
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cmd_args_to_string
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
from conan.tools.system import PipEnv
from conan.tools.env.environment import Environment

required_conan_version = ">=2.0.9"


class ExecuTorchConan(ConanFile):
    name = "executorch"
    description = (
        "ExecuTorch is PyTorch's unified solution for deploying AI models on-device"
    )
    license = "BSD"
    url = "https://github.com/pytorch/executorch"
    homepage = "https://docs.pytorch.org/executorch"

    topics = ("machine-learning", "mobile", "embedded",
              "deep-learning", "neural-network", "gpu", "tensor")

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

        "build_executor_runner": [True, False]
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

        "build_executor_runner": False
    }
    # In case having config_options() or configure() method, the logic should be moved to the specific methods.
    implements = ["auto_shared_fpic"]

    # no exports_sources attribute, but export_sources(self) method instead
    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        # src_folder needs to be named "executorch" due to https://github.com/pytorch/executorch/issues/6475
        cmake_layout(self, src_folder="executorch")

    def requirements(self):
        if self.options.vulkan:
            self.requires("vulkan-headers/1.4.313.0")

    def validate(self):
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
        if '.' in self.version:
            git.checkout(f"v{self.version}")
        else:
            git.checkout(f"{self.version}")
        git.run("submodule update --init --recursive")

    def get_system_python(self):
        python = "python" if platform.system() == "Windows" else "python3"
        default_python = shutil.which(python)
        return os.path.realpath(default_python) if default_python else None
    
    def get_default_python(self):
        return self.conf.get("tools.system.pipenv:python_interpreter") or self.get_system_python()
    
    def add_dir_to_path(self,bin_dir,env_name="conan_env"):
        env = Environment()
        env.prepend_path("PATH", bin_dir)
        env.vars(self).save_script(env_name)

    def get_env_bin_dir(self,env_dir):
        return os.path.join(env_dir,"Scripts" if platform.system() == "Windows" else "bin")
    
    def get_env_python(self,env_dir):
        return os.path.join(self.get_env_bin_dir(env_dir), "python.exe" if platform.system() == "Windows" else "python")
    
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

        deps = CMakeDeps(self)
        deps.generate()

        # setup an env to install uv into
        python = self.get_default_python()

        uv_install_env_dir = os.path.join(self.build_folder,'.uv_install_env')

        # use default python to make an env
        self.run(cmd_args_to_string([python, '-m', 'venv', uv_install_env_dir]))

        # install uv in the env we just made
        self.run(cmd_args_to_string([self.get_env_python(uv_install_env_dir),'-m','pip', 'install', 'uv']))

        uv_env_name = 'uv_env'
        uv_env_dir = os.path.join(self.build_folder,f'.{uv_env_name}')

        # use the uv env we just made to create another env with the python version we need
        self.run(cmd_args_to_string([self.get_env_python(uv_install_env_dir),'-m', 'uv', 'venv','--seed','--python','3.12.2',uv_env_dir]))

        # use the env we just made to install the executorch requirements
        self.run(cmd_args_to_string([self.get_env_python(uv_env_dir),os.path.join(self.source_folder,'install_requirements.py')]),cwd=self.source_folder)

        # add the env with the required packages to path
        self.add_dir_to_path(self.get_env_bin_dir(uv_env_dir))
        

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

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "executorch")

        core = self.cpp_info.components["executorch_core"]
        core.libs = ["executorch_core"]
        core.set_property("cmake_target_name", "executorch_core")
        core.includedirs = [
            # https://github.com/pytorch/executorch/blob/351815f4836c1752baabbe06de9a49ce103e67b5/CMakeLists.txt#L300
            os.path.join("include", "executorch", "runtime",
                         "core", "portable_type", "c10"),
            # Trial and error
            os.path.join("include", "executorch", "runtime",
                         "core", "portable_type", "c10", "torch"),
        ]
        core.defines = ["C10_USING_CUSTOM_GENERATED_MACROS"]
        main = self.cpp_info.components["executorch"]
        main.libs = ["executorch"]
        main.requires = ["executorch_core"]
        main.set_property("cmake_target_name", "executorch")
        main.defines = ["C10_USING_CUSTOM_GENERATED_MACROS"]

        backends = self.cpp_info.components["executorch_backends"]
        backends.libs = []  # Interface target
        backends.set_property("cmake_target_name", "executorch::backends")

        extensions = self.cpp_info.components["executorch_extensions"]
        extensions.libs = []  # Interface target
        extensions.set_property("cmake_target_name", "executorch::extensions")

        kernels = self.cpp_info.components["executorch_kernels"]
        kernels.libs = []  # Interface target
        kernels.set_property("cmake_target_name", "executorch::kernels")

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
            # https://github.com/pytorch/executorch/blob/351815f4836c1752baabbe06de9a49ce103e67b5/backends/apple/coreml/CMakeLists.txt#L111
            core.includedirs.append(os.path.join(
                "include", "executorch", "backends", "apple", "coreml", "runtime", "util"))
            # https://github.com/pytorch/executorch/blob/351815f4836c1752baabbe06de9a49ce103e67b5/backends/apple/coreml/CMakeLists.txt#L146
            core.includedirs.append(os.path.join(
                "include", "executorch", "backends", "apple", "coreml", "runtime", "inmemoryfs"))

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

        if str(self.settings.os) in ["Linux", "FreeBSD"]:
            for name in self.cpp_info.components.keys():
                comp = self.cpp_info.components[name]
                comp.system_libs.extend(["m", "pthread", "dl"])

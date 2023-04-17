from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir, save
import os
import textwrap

required_conan_version = ">=1.51.3"


class TensorpipeConan(ConanFile):
    name = "tensorpipe"
    description = "The TensorPipe project provides a tensor-aware channel to " \
                  "transfer rich objects from one process to another while " \
                  "using the fastest transport for the tensors contained " \
                  "therein (e.g., CUDA device-to-device copy)."
    license = "BSD-3-Clause"
    topics = ("tensor", "cuda")
    homepage = "https://github.com/pytorch/tensorpipe"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cuda": [True, False],
        "cuda_ipc": [True, False],
        "ibv": [True, False],
        "shm": [True, False],
        "cma": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cuda": False,
        "cuda_ipc": True,
        "ibv": True,
        "shm": True,
        "cma": True,
    }

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.ibv
            del self.options.shm
            del self.options.cma

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.cuda:
            del self.options.cuda_ipc

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libnop/cci.20200728")
        self.requires("libuv/1.44.2")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support Windows")
        if self.options.cuda:
            raise ConanInvalidConfiguration("cuda recipe not yet available in CCI")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TP_USE_CUDA"] = self.options.cuda
        tc.variables["TP_ENABLE_IBV"] = self.options.get_safe("ibv", False)
        tc.variables["TP_ENABLE_SHM"] = self.options.get_safe("shm", False)
        tc.variables["TP_ENABLE_CMA"] = self.options.get_safe("cma", False)
        tc.variables["TP_ENABLE_CUDA_IPC"] = self.options.get_safe("cuda_ipc", False)
        tc.variables["TP_BUILD_BENCHMARK"] = False
        tc.variables["TP_BUILD_PYTHON"] = False
        tc.variables["TP_BUILD_TESTING"] = False
        tc.variables["TP_BUILD_LIBUV"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "tensorpipe", "CMakeLists.txt")
        replace_in_file(self, cmakelists, "find_package(uv REQUIRED)", "find_package(libuv REQUIRED CONFIG)")
        replace_in_file(
            self,
            cmakelists,
            "target_link_libraries(tensorpipe PRIVATE uv::uv)",
            "target_link_libraries(tensorpipe PRIVATE $<IF:$<TARGET_EXISTS:uv>,uv,uv_a>)",
        )
        replace_in_file(
            self,
            cmakelists,
            "target_include_directories(tensorpipe PUBLIC $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/third_party/libnop/include>)",
            "find_package(libnop REQUIRED CONFIG)\ntarget_link_libraries(tensorpipe PUBLIC libnop::libnop)",
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"tensorpipe": "Tensorpipe::Tensorpipe"},
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Tensorpipe")
        self.cpp_info.set_property("cmake_target_name", "tensorpipe")
        self.cpp_info.libs = ["tensorpipe"]
        if is_apple_os(self):
            self.cpp_info.frameworks = ["CoreFoundation", "IOKit"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Tensorpipe"
        self.cpp_info.names["cmake_find_package_multi"] = "Tensorpipe"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

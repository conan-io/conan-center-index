from conan import ConanFile, tools
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get

required_conan_version = ">=2.0.0"

class WasmXrplfConan(ConanFile):
    name = "wasm-xrplf"
    description = "XRPLF wasm VM implementation(wamr fork)"
    license = "Apache-2.0"
    url = "https://github.com/ripple/wasm-micro-runtime.git"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["WAMR_BUILD_INTERP"] = 1
        tc.variables["WAMR_BUILD_FAST_INTERP"] = 1
        tc.variables["WAMR_BUILD_INSTRUCTION_METERING"] = 1
        tc.variables["WAMR_BUILD_AOT"] = 0
        tc.variables["WAMR_BUILD_JIT"] = 0
        tc.variables["WAMR_BUILD_FAST_JIT"] = 0
        tc.variables["WAMR_BUILD_SIMD"] = 0
        tc.variables["WAMR_BUILD_LIB_PTHREAD"] = 0
        tc.variables["WAMR_BUILD_LIB_WASI_THREADS"] = 0
        tc.variables["WAMR_BUILD_TAIL_CALL"] = 1
        tc.variables["WAMR_BUILD_BULK_MEMORY"] = 0
        tc.variables["WAMR_DISABLE_HW_BOUND_CHECK"] = 1
        tc.variables["WAMR_DISABLE_STACK_HW_BOUND_CHECK"] = 1
        tc.variables["WAMR_BH_LOG"] = "wamr_log_to_rippled"
        
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["iwasm"]
        self.cpp_info.names["cmake_find_package"] = "wasm-xrplf"
        self.cpp_info.names["cmake_find_package_multi"] = "wasm-xrplf"

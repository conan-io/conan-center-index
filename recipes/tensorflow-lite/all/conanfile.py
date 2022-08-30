from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import files, build
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os
import textwrap


required_conan_version = ">=1.50.2"

class TensorflowLiteConan(ConanFile):
    name = "tensorflow-lite"
    license = "Apache-2.0"
    homepage = "https://www.tensorflow.org/lite/guide"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("TensorFlow Lite is a set of tools that enables on-device machine learning "
                   "by helping developers run their models on mobile, embedded, and IoT devices.")
    topics = ("machine-learning", "neural-networks", "deep-learning")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ruy": [True, False],
        "with_nnapi": [True, False],
        "with_mmap": [True, False],
        "with_xnnpack": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ruy": False,
        "with_nnapi": False,
        "with_mmap": True,
        "with_xnnpack": True
    }

    short_paths = True

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "Visual Studio": "14",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_nnapi
            del self.options.with_mmap
        if self.settings.os == "Macos":
            del self.options.with_nnapi

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("abseil/20211102.0")
        self.requires("eigen/3.4.0")
        self.requires("farmhash/cci.20190513")
        self.requires("fft/cci.20061228")
        self.requires("flatbuffers/2.0.5")
        self.requires("gemmlowp/cci.20210928")
        self.requires("opencl-headers/2022.05.18")
        self.requires("vulkan-headers/1.3.221")
        if self.settings.arch in ("x86", "x86_64"):
            self.requires("intel-neon2sse/cci.20210225")
        if self.options.with_ruy or True: # Upstream always calls find_package
            self.requires("ruy/cci.20220628")
        if self.options.with_xnnpack:
            self.requires("xnnpack/cci.20220621")

        if self.options.with_xnnpack or self.options.get_safe("with_nnapi", False):
            self.requires("fp16/cci.20210320")

    def build_requirements(self):
        self.tool_requires("cmake/3.24.0")

    def layout(self):
        cmake_layout(self)
        # TODO: once https://github.com/conan-io/conan/pull/11889 is available
        self.folders.build = f"build_folder/{self.settings.build_type}" # conflict with upstream files
        self.folders.generators = "build_folder/generators" # conflict with upstream files

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TFLITE_ENABLE_RUY"] = self.options.with_ruy,
        tc.variables["TFLITE_ENABLE_NNAPI"] = self.options.get_safe("with_nnapi", False),
        tc.variables["TFLITE_ENABLE_XNNPACK"] = self.options.with_xnnpack,
        tc.variables["TFLITE_ENABLE_MMAP"] = self.options.get_safe("with_mmap", False)
        tc.variables["TFLITE_ENABLE_GPU"] = False,
        tc.variables["TFLITE_ENABLE_INSTALL"] = True,

        tc.cache_variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True,
        if self.settings.arch == "armv8":
            # Not defined by Conan for Apple Silicon. See https://github.com/conan-io/conan/pull/8026
            tc.cache_variables["CMAKE_SYSTEM_PROCESSOR"] = "arm64"

        # Custom FindModules use a "populate" this will skip the logic to vendor deps
        tc.variables["abseil-cpp_POPULATED"] = True
        tc.variables["clog_POPULATED"] = True
        tc.variables["cpuinfo_POPULATED"] = True
        # tc.variables["egl_headers_POPULATED"] = True
        tc.variables["eigen_POPULATED"] = True
        tc.variables["farmhash_POPULATED"] = True
        tc.variables["fft2d_POPULATED"] = True
        tc.variables["flatbuffers_POPULATED"] = True
        tc.variables["fp16_headers_POPULATED"] = True
        tc.variables["gemmlowp_POPULATED"] = True
        tc.variables["neon2sse_POPULATED"] = True
        tc.variables["opencl_headers_POPULATED"] = True
        # tc.variables["opengl_headers_POPULATED"] = True
        tc.variables["ruy_POPULATED"] = True
        tc.variables["vulkan_headers_POPULATED"] = True
        tc.variables["xnnpack_POPULATED"] = True
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            build.check_min_cppstd(self, 17)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(f"{self.name} requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.name} requires C++17, which your compiler does not support.")

    def build(self):
        files.apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join("tensorflow", "lite"))
        cmake.build()

    def _create_cmake_module_alias_target(self, module_file):
        aliased = "tensorflowlite::tensorflowlite"
        alias = "tensorflow::tensorflowlite"
        content = textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        files.save(self, module_file, content)

    @property
    def _module_file(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package(self):
        files.copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        self._create_cmake_module_alias_target(os.path.join(self.package_folder, self._module_file))

        files.copy(self, "*.h", src=os.path.join(self.source_folder, "tensorflow", "lite"), dst=os.path.join(self.package_folder, "include", "tensorflow", "lite"))
        files.copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"))
        files.copy(self, "*.so", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"))
        files.copy(self, "*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"))
        files.copy(self, "*.lib", src=os.path.join(self.build_folder), dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        files.copy(self, "*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tensorflowlite")
        self.cpp_info.set_property("cmake_target_name", "tensorflow::tensorflowlite")

        self.cpp_info.names["cmake_find_package"] = "tensorflowlite"
        self.cpp_info.names["cmake_find_package_multi"] = "tensorflowlite"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file]

        defines = []
        if not self.options.shared:
            defines.append("TFL_STATIC_LIBRARY_BUILD")
        if self.options.with_ruy:
            defines.append("TFLITE_WITH_RUY")

        self.cpp_info.defines = defines
        self.cpp_info.libs = ["tensorflow-lite"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")

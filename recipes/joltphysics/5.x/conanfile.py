from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, rm, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os

required_conan_version = ">=2.0.9"


class JoltPhysicsConan(ConanFile):
    name = "joltphysics"
    description = (
        "A multi core friendly rigid body physics and collision detection "
        "library, written in C++, suitable for games and VR applications."
    )
    license = "MIT"
    topics = ("physics", "simulation", "physics-engine", "physics-simulation", "rigid-body", "game", "collision")
    homepage = "https://github.com/jrouwe/JoltPhysics"
    url = "https://github.com/conan-io/conan-center-index"

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
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["TARGET_UNIT_TESTS"] = False
        tc.cache_variables["TARGET_HELLO_WORLD"] = False
        tc.cache_variables["TARGET_PERFORMANCE_TEST"] = False
        tc.cache_variables["TARGET_SAMPLES"] = False
        tc.cache_variables["TARGET_VIEWER"] = False
        tc.cache_variables["CROSS_PLATFORM_DETERMINISTIC"] = False
        tc.cache_variables["INTERPROCEDURAL_OPTIMIZATION"] = False
        tc.cache_variables["GENERATE_DEBUG_SYMBOLS"] = False
        tc.cache_variables["ENABLE_ALL_WARNINGS"] = False
        tc.cache_variables["OVERRIDE_CXX_FLAGS"] = False
        tc.cache_variables["DEBUG_RENDERER_IN_DEBUG_AND_RELEASE"] = False
        tc.cache_variables["PROFILER_IN_DEBUG_AND_RELEASE"] = False
        if is_msvc(self):
            tc.cache_variables["USE_STATIC_MSVC_RUNTIME_LIBRARY"] = is_msvc_static_runtime(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "Build"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.cmake", os.path.join(self.package_folder, "include", "Jolt"))

    def package_info(self):
        self.cpp_info.libs = ["Jolt"]
        self.cpp_info.set_property("cmake_file_name", "Jolt")
        self.cpp_info.set_property("cmake_target_name", "Jolt::Jolt")
        # INFO: The CMake option ENABLE_OBJECT_STREAM is enabled by default and defines JPH_OBJECT_STREAM as public
        # https://github.com/jrouwe/JoltPhysics/blob/v5.2.0/Build/CMakeLists.txt#L95C8-L95C28
        self.cpp_info.defines = ["JPH_OBJECT_STREAM"]
        # INFO: Public defines exposed in include/Jolt/Jolt.cmake
        # https://github.com/jrouwe/JoltPhysics/blob/v5.2.0/Build/CMakeLists.txt#L51
        if self.settings.arch in ["x86_64", "x86"]:
            self.cpp_info.defines.extend(["JPH_USE_AVX2", "JPH_USE_AVX", "JPH_USE_SSE4_1",
                                          "JPH_USE_SSE4_2", "JPH_USE_LZCNT", "JPH_USE_TZCNT",
                                          "JPH_USE_F16C", "JPH_USE_FMADD"])
        if is_msvc(self):
            # INFO: Floating point exceptions are enabled by default
            # https://github.com/jrouwe/JoltPhysics/blob/v5.2.0/Build/CMakeLists.txt#L37
            # https://github.com/jrouwe/JoltPhysics/blob/v5.2.0/Jolt/Jolt.cmake#L529
            self.cpp_info.defines.append("JPH_FLOATING_POINT_EXCEPTIONS_ENABLED")

        if self.options.shared:
            # https://github.com/jrouwe/JoltPhysics/blob/v5.2.0/Jolt/Jolt.cmake#L495
            self.cpp_info.defines.append("JPH_SHARED_LIBRARY")

        # https://github.com/jrouwe/JoltPhysics/blob/v5.2.0/Build/CMakeLists.txt#L48
        # https://github.com/jrouwe/JoltPhysics/blob/v5.2.0/Jolt/Jolt.cmake#L554
        self.cpp_info.defines.append("JPH_OBJECT_LAYER_BITS=16")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")

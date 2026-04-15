from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.1"

class MujocoConan(ConanFile):
    name = "mujoco"
    description = "Multi-Joint dynamics with Contact. A general purpose physics simulator."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google-deepmind/mujoco"
    topics = ("physics", "simulation", "robotics", "dynamics")
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

    def validate(self):
        check_min_cppstd(self, 20)

        # Only shared libraries are supported on non-Emscripten platforms
        # Note: Static build support is being developed upstream:
        # https://github.com/google-deepmind/mujoco/pull/2693
        if self.settings.os != "Emscripten" and not self.options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} only supports shared libraries on non-Emscripten platforms. Build it with -o {self.ref}:shared=True"
            )

        # MuJoCo's mjtNum is double; libccd must match to avoid precision mismatch.
        if not self.dependencies["libccd"].options.enable_double_precision:
            raise ConanInvalidConfiguration('Dependency libccd requires double precision. Build it with -o "libccd/*:enable_double_precision=True"')

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("lodepng/cci.20230410")
        self.requires("qhull/8.0.2")
        self.requires("tinyxml2/11.0.0")
        self.requires("tinyobjloader/2.0.0-rc10")
        self.requires("libccd/2.1", options={"enable_double_precision": True})
        self.requires("marchingcubecpp/0.0.0.cci.20260224")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["MUJOCO_BUILD_EXAMPLES"] = False
        tc.cache_variables["MUJOCO_BUILD_SIMULATE"] = False
        tc.cache_variables["MUJOCO_BUILD_STUDIO"] = False
        tc.cache_variables["MUJOCO_BUILD_TESTS"] = False
        tc.cache_variables["MUJOCO_TEST_PYTHON_UTIL"] = False
        tc.cache_variables["MUJOCO_WITH_USD"] = False
        tc.cache_variables["MUJOCO_USE_FILAMENT"] = False
        tc.cache_variables["CMAKE_INTERPROCEDURAL_OPTIMIZATION"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["mujoco"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])

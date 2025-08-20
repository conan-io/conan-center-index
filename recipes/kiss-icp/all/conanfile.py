from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, apply_conandata_patches
import os

required_conan_version = ">=2.1.0"


class KissIcpConan(ConanFile):
    name = "kiss-icp"
    description = "A LiDAR odometry pipeline that just works"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/PRBonn/kiss-icp"
    topics = ("robotics", "ros", "slam", "ros2", "3d-mapping", "lidar-slam")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self)

        self.folders.source = "."
        self.folders.build = "build"
        self.folders.generators = self.folders.build

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)
        self.requires("sophus/1.22.10", transitive_headers=True)
        self.requires("onetbb/2020.3.3", transitive_headers=True)
        self.requires("tsl-robin-map/1.3.0", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)
    
    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="cpp/kiss_icp")
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="**/*.h", src=os.path.join(self.source_folder, "cpp/kiss_icp"), dst=os.path.join(self.package_folder, "include/kiss_icp"))
        copy(self, pattern="**/*.hpp", src=os.path.join(self.source_folder, "cpp/kiss_icp"), dst=os.path.join(self.package_folder, "include/kiss_icp"))
        copy(self, pattern="**/*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="**/*.so", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="**/*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="**/*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, pattern="**/*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)


    def package_info(self):
        self.cpp_info.libs = ["kiss_icp_core", "kiss_icp_metrics", "kiss_icp_pipeline"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.requires = ["eigen::eigen3", "sophus::sophus", "onetbb::onetbb", "tsl-robin-map::tsl-robin-map"]

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file
import os

required_conan_version = ">=2.1.0"


class KissIcpConan(ConanFile):
    name = "kiss-icp"
    description = "A LiDAR odometry pipeline that just works"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/PRBonn/kiss-icp"
    topics = ("robotics", "ros", "slam", "ros2", "3d-mapping", "lidar-slam")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)   
        self.requires("sophus/1.22.10", transitive_headers=True)
        self.requires("tsl-robin-map/1.3.0", transitive_headers=True)
        self.requires("onetbb/2022.3.0")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)
        self._patch_sources()

    def _patch_sources(self):
        # Remove hardcoded settings
        cmake_file = os.path.join(self.source_folder, "cpp", "kiss_icp", "CMakeLists.txt")
        replace_in_file(self, cmake_file, "set(CMAKE_BUILD_TYPE Release)", "")
        replace_in_file(self, cmake_file, "set(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")        
    
    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        # Configure to use system dependencies (Conan)
        tc.cache_variables["USE_SYSTEM_EIGEN3"] = True
        tc.cache_variables["USE_SYSTEM_SOPHUS"] = True
        tc.cache_variables["USE_SYSTEM_TSL-ROBIN-MAP"] = True
        tc.cache_variables["USE_SYSTEM_TBB"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="cpp/kiss_icp")
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="**/*.h", src=os.path.join(self.source_folder, "cpp/kiss_icp"), dst=os.path.join(self.package_folder, "include", "kiss_icp"), keep_path=True)
        copy(self, pattern="**/*.hpp", src=os.path.join(self.source_folder, "cpp/kiss_icp"), dst=os.path.join(self.package_folder, "include", "kiss_icp"), keep_path=True)
        copy(self, pattern="**/*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="**/*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)


    def package_info(self):
        self.cpp_info.components["core"].libs = ["kiss_icp_core"]
        self.cpp_info.components["core"].set_property("cmake_target_name", "kiss-icp::kiss_icp_core")
        self.cpp_info.components["core"].requires = ["eigen::eigen", "sophus::sophus", "onetbb::onetbb", "tsl-robin-map::tsl-robin-map"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["core"].system_libs = ["m"]
        
        self.cpp_info.components["metrics"].libs = ["kiss_icp_metrics"]
        self.cpp_info.components["metrics"].set_property("cmake_target_name", "kiss-icp::kiss_icp_metrics")
        self.cpp_info.components["metrics"].requires = ["eigen::eigen"]
        
        self.cpp_info.components["pipeline"].libs = ["kiss_icp_pipeline"]
        self.cpp_info.components["pipeline"].set_property("cmake_target_name", "kiss-icp::kiss_icp_pipeline")
        self.cpp_info.components["pipeline"].requires = ["core"]

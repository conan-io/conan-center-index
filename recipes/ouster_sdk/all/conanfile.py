import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir, rm
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"

class PackageConan(ConanFile):
    name = "ouster_sdk"
    description = "Ouster SDK - tools for working with Ouster Lidars"
    license = "BSD 3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ouster-lidar/ouster_example"
    topics = ("ouster", "lidar", "driver", "hardware", "point cloud", "3d", "robotics", "automotive")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_osf": [True, False],
        "build_pcap": [True, False],
        "build_viz": [True, False],
        "eigen_max_align_bytes": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_osf": True,
        "build_pcap": True,
        "build_viz": False,
        "eigen_max_align_bytes": False,
    }
    options_description = {
        "build_osf": "Build Ouster OSF library.",
        "build_pcap": "Build pcap utils.",
        "build_viz": "Build Ouster visualizer.",
        "eigen_max_align_bytes": "Eigen max aligned bytes.",
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Used in ouster/types.h
        self.requires("eigen/3.4.0", transitive_headers=True)
        # Used in ouster/sensor_http.h
        self.requires("jsoncpp/1.9.5", transitive_headers=True)
        self.requires("spdlog/1.12.0")
        self.requires("fmt/10.1.0")
        self.requires("libcurl/8.2.1")

        if self.options.build_pcap:
            self.requires("libtins/4.5")

        if self.options.build_osf:
            # Used in fb_generated/*.h
            self.requires("flatbuffers/23.5.26", transitive_headers=True)
            self.requires("libpng/1.6.40")
            self.requires("zlib/1.2.13")

        if self.options.build_viz:
            self.requires("glad/0.1.36")
            self.requires("glfw/3.3.8")
            if self.settings.os != "Windows":
                self.requires("xorg/system")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_VIZ"] = self.options.build_viz
        tc.cache_variables["BUILD_PCAP"] = self.options.build_pcap
        tc.cache_variables["BUILD_OSF"] = self.options.build_osf
        tc.cache_variables["OUSTER_USE_EIGEN_MAX_ALIGN_BYTES_32"] = self.options.eigen_max_align_bytes
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("flatbuffers", "cmake_target_name", "flatbuffers::flatbuffers")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OusterSDK")
        self.cpp_info.set_property("cmake_target_name", "OusterSDK::OusterSDK")

        self.cpp_info.components["ouster_client"].set_property("cmake_target_name", "OusterSDK::ouster_client")
        self.cpp_info.components["ouster_client"].libs = ["ouster_client"]
        self.cpp_info.components["ouster_client"].includedirs.append(
            os.path.join("include", "optional-lite")
        )
        self.cpp_info.components["ouster_client"].requires = [
            "eigen::eigen",
            "jsoncpp::jsoncpp",
            "spdlog::spdlog",
            "fmt::fmt",
            "libcurl::libcurl",
        ]

        if self.options.build_osf:
            self.cpp_info.components["ouster_osf"].set_property("cmake_target_name", "OusterSDK::ouster_osf")
            self.cpp_info.components["ouster_osf"].libs = ["ouster_osf"]
            self.cpp_info.components["ouster_osf"].requires = [
                "ouster_client",
                "flatbuffers::flatbuffers",
                "libpng::libpng",
                "zlib::zlib",
            ]

        if self.options.build_pcap:
            self.cpp_info.components["ouster_pcap"].set_property("cmake_target_name", "OusterSDK::ouster_pcap")
            self.cpp_info.components["ouster_pcap"].libs = ["ouster_pcap"]
            self.cpp_info.components["ouster_pcap"].requires = [
                "ouster_client",
                "libtins::libtins",
            ]

        if self.options.build_viz:
            self.cpp_info.components["ouster_viz"].set_property("cmake_target_name", "OusterSDK::ouster_viz")
            self.cpp_info.components["ouster_viz"].libs = ["ouster_viz"]
            self.cpp_info.components["ouster_viz"].requires = [
                "ouster_client",
                "glad::glad",
                "glfw::glfw",
            ]
            if self.settings.os != "Windows":
                self.cpp_info.components["ouster_viz"].requires.append("xorg::xorg")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "OusterSDK"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OusterSDK"
        self.cpp_info.names["cmake_find_package"] = "OusterSDK"
        self.cpp_info.names["cmake_find_package_multi"] = "OusterSDK"


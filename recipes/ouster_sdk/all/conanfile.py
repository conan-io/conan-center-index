import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, copy, rmdir, rm, save, replace_in_file, export_conandata_patches, apply_conandata_patches
from conan.tools.scm import Version

required_conan_version = ">=2.0.6"

class OusterSdkConan(ConanFile):
    name = "ouster_sdk"
    description = "Ouster SDK - tools for working with Ouster Lidars"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ouster-lidar/ouster-sdk"
    topics = ("ouster", "lidar", "driver", "hardware", "point cloud", "3d", "robotics", "automotive")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_sensor": [True, False],
        "build_osf": [True, False],
        "build_pcap": [True, False],
        "build_viz": [True, False],
        "build_mapping": [True, False],
        "eigen_max_align_bytes": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_sensor": True,
        "build_osf": True,
        "build_pcap": True,
        "build_viz": False,
        "build_mapping": True,
        "eigen_max_align_bytes": False,
    }
    options_description = {
        "build_sensor": "Build Ouster Sensor library.",
        "build_osf": "Build Ouster OSF library.",
        "build_pcap": "Build pcap utils.",
        "build_viz": "Build Ouster visualizer.",
        "build_mapping": "Build Ouster mapping library.",
        "eigen_max_align_bytes": "Force maximum alignment of Eigen data to 32 bytes.",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        # build_sensor and build_mapping are only available in 0.15.0+
        if Version(self.ref.version) < "0.15.0":
            del self.options.build_sensor
            del self.options.build_mapping

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Used in ouster/types.h
        self.requires("eigen/3.4.0", transitive_headers=True)
        # Replaces vendored optional-lite
        self.requires("optional-lite/3.6.0", transitive_headers=True)

        # libcurl moved to ouster_sensor in 0.15.0+
        if Version(self.version) < "0.15.0" or self.options.build_sensor:
                self.requires("libcurl/[>=7.78 <9]")

        if self.options.build_pcap:
            self.requires("libtins/4.5")
            self.requires("libpcap/1.10.5")

        # libpng is required by both ouster_osf and ouster_viz (0.15.0+)
        needs_libpng = self.options.build_osf or (Version(self.version) >= "0.15.0" and self.options.build_viz)
        if needs_libpng:
            self.requires("libpng/[>=1.6 <2]", transitive_libs=True)

        if self.options.build_osf:
            # Used in fb_generated/*.h
            self.requires("flatbuffers/24.3.7", transitive_headers=True)
            # 0.12.0+ shared_library uses private libpng in ouster_osf and result in missing symbols
            # 0.11.0 and earlier used private libpng in ouster_osf
            self.requires("zlib/[>=1.2.11 <2]", transitive_libs=True)

        if self.options.build_viz:
            self.requires("glfw/3.4")
            self.requires("glad/2.0.8")

        if Version(self.version) >= "0.15.0" and self.options.build_mapping:
            # Required for ouster_mapping module (0.15.0+)
            self.requires("ceres-solver/2.1.0")
            self.requires("kiss-icp/1.2.3")
            self.requires("sophus/1.22.10")

    def validate(self):
        check_min_cppstd(self, 14)

        if self.options.build_osf and not self.options.build_pcap:
            raise ConanInvalidConfiguration("build_osf=True requires build_pcap=True")

        if self.options.shared and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Shared builds are not supported on Windows")

    def build_requirements(self):
        if self.options.build_osf:
            self.tool_requires("flatbuffers/<host_version>")
        # ouster_mapping requires CMake 3.16.3+
        if Version(self.version) >= "0.15.0" and self.options.build_mapping:
            self.tool_requires("cmake/[>=3.16.3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_VIZ"] = self.options.build_viz
        tc.cache_variables["BUILD_PCAP"] = self.options.build_pcap
        tc.cache_variables["BUILD_OSF"] = self.options.build_osf
        if Version(self.version) >= "0.15.0":
            tc.cache_variables["BUILD_SENSOR"] = self.options.build_sensor
            tc.cache_variables["BUILD_MAPPING"] = self.options.build_mapping
        tc.cache_variables["OUSTER_USE_EIGEN_MAX_ALIGN_BYTES_32"] = self.options.eigen_max_align_bytes
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.cache_variables["BUILD_SHARED_LIBRARY"] = self.options.shared
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("flatbuffers", "cmake_target_name", "flatbuffers::flatbuffers")
        if Version(self.version) >= "0.15.0" and self.options.build_mapping:
            deps.set_property("kiss-icp", "cmake_file_name", "KissIcp")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        # Unvendor optional-lite
        rmdir(self, os.path.join(self.source_folder, "ouster_client", "include", "optional-lite"))
        replace_in_file(self, os.path.join(self.source_folder, "ouster_client", "CMakeLists.txt"),
                        " include/optional-lite", "")
        save(self, os.path.join(self.source_folder, "ouster_client", "CMakeLists.txt"),
             "find_package(optional-lite REQUIRED)\n"
             "target_link_libraries(ouster_client PUBLIC nonstd::optional-lite)\n",
             append=True)


    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        if self.options.shared:
            # INFO: Version 0.14.0+ produces both shared and static libraries when shared=True
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OusterSDK")
        self.cpp_info.set_property("cmake_target_name", "OusterSDK::OusterSDK")
        produce_library = not self.options.shared

        self.cpp_info.components["ouster_client"].set_property("cmake_target_name", "OusterSDK::ouster_client")
        self.cpp_info.components["ouster_client"].libs = ["ouster_client"] if produce_library else []
        self.cpp_info.components["ouster_client"].requires = [
            "eigen::eigen",
            "optional-lite::optional-lite",
        ]
        # libcurl moved to ouster_sensor in 0.15.0+
        if Version(self.version) < "0.15.0":
            self.cpp_info.components["ouster_client"].requires.append("libcurl::libcurl")
        if self.settings.os == "Windows":
            self.cpp_info.components["ouster_client"].system_libs = ["ws2_32"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ouster_client"].system_libs = ["pthread"]
        if self.options.eigen_max_align_bytes:
            self.cpp_info.components["ouster_client"].defines = ["EIGEN_MAX_ALIGN_BYTES=32"]

        # ouster_sensor component (0.15.0+)
        if Version(self.version) >= "0.15.0" and self.options.build_sensor:
            self.cpp_info.components["ouster_sensor"].set_property("cmake_target_name", "OusterSDK::ouster_sensor")
            self.cpp_info.components["ouster_sensor"].libs = ["ouster_sensor"] if produce_library else []
            self.cpp_info.components["ouster_sensor"].requires = [
                "ouster_client",
                "eigen::eigen",
                "libcurl::libcurl",
            ]
            if self.settings.os == "Windows":
                self.cpp_info.components["ouster_sensor"].system_libs = ["ws2_32"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["ouster_sensor"].system_libs = ["pthread"]

        if self.options.build_osf:
            self.cpp_info.components["ouster_osf"].set_property("cmake_target_name", "OusterSDK::ouster_osf")
            self.cpp_info.components["ouster_osf"].libs = ["ouster_osf"] if produce_library else []
            self.cpp_info.components["ouster_osf"].includedirs.append(os.path.join("include", "fb_generated"))
            self.cpp_info.components["ouster_osf"].requires = [
                "ouster_client",
                "ouster_pcap",
                "flatbuffers::flatbuffers",
                "libpng::libpng",
                "zlib::zlib",
            ]

        if self.options.build_pcap:
            self.cpp_info.components["ouster_pcap"].set_property("cmake_target_name", "OusterSDK::ouster_pcap")
            self.cpp_info.components["ouster_pcap"].libs = ["ouster_pcap"] if produce_library else []
            self.cpp_info.components["ouster_pcap"].requires = [
                "ouster_client",
                "libtins::libtins",
                "libpcap::libpcap",
            ]
            if self.settings.os == "Windows":
                self.cpp_info.components["ouster_pcap"].system_libs = ["ws2_32"]

        if self.options.build_viz:
            self.cpp_info.components["ouster_viz"].set_property("cmake_target_name", "OusterSDK::ouster_viz")
            self.cpp_info.components["ouster_viz"].libs = ["ouster_viz"] if produce_library else []
            self.cpp_info.components["ouster_viz"].requires = [
                "ouster_client",
                "glfw::glfw",
                "glad::glad",
            ]
            # 0.15.0+ ouster_viz requires PNG
            if Version(self.version) >= "0.15.0":
                self.cpp_info.components["ouster_viz"].requires.append("libpng::libpng")

        if Version(self.version) >= "0.15.0" and self.options.build_mapping:
            self.cpp_info.components["ouster_mapping"].set_property("cmake_target_name", "OusterSDK::ouster_mapping")
            self.cpp_info.components["ouster_mapping"].libs = ["ouster_mapping"] if produce_library else []
            self.cpp_info.components["ouster_mapping"].requires = [
                "ouster_client",
                "ouster_osf",  # ouster_mapping requires ouster_osf
                "ceres-solver::ceres",
                "kiss-icp::core",
                "kiss-icp::pipeline",
                "sophus::sophus",
            ]

            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["ouster_mapping"].system_libs = ["gomp"]

        if self.options.shared:
            self.cpp_info.components["shared_library"].set_property("cmake_target_name", "OusterSDK::shared_library")
            self.cpp_info.components["shared_library"].libs = ["shared_library"]
            self.cpp_info.components["shared_library"].requires = ["ouster_client"]
            if Version(self.version) >= "0.15.0" and self.options.build_sensor:
                self.cpp_info.components["shared_library"].requires.append("ouster_sensor")
            if self.options.build_osf:
                self.cpp_info.components["shared_library"].requires.append("ouster_osf")
            if self.options.build_pcap:
                self.cpp_info.components["shared_library"].requires.append("ouster_pcap")
            if self.options.build_viz:
                self.cpp_info.components["shared_library"].requires.append("ouster_viz")
            if Version(self.version) >= "0.15.0" and self.options.build_mapping:
                self.cpp_info.components["shared_library"].requires.append("ouster_mapping")

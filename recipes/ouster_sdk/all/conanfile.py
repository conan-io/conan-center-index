import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, copy, rmdir, rm, save, replace_in_file, export_conandata_patches, apply_conandata_patches

required_conan_version = ">=2.1"


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

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Used in ouster/core/types.h
        self.requires("eigen/3.4.0", transitive_headers=True)
        # Replaces vendored optional-lite
        self.requires("optional-lite/3.6.0", transitive_headers=True)
        # Replaces vendored robin-map, used in ouster/core/voxel_hash_map.h
        self.requires("tsl-robin-map/1.3.0", transitive_headers=True)
        self.requires("libzip/1.11.4")
        self.requires("openssl/[>=1.1 <4]")

        # libcurl is used by ouster_sensor and to read remote OSF files
        if self.options.build_sensor or self.options.build_osf:
            self.requires("libcurl/[>=7.78 <9]")

        if self.options.build_pcap:
            self.requires("libtins/4.5")
            self.requires("libpcap/1.10.5")

        # libpng is required by both ouster_osf and ouster_viz
        if self.options.build_osf or self.options.build_viz:
            self.requires("libpng/[>=1.6 <2]", transitive_libs=True)

        if self.options.build_osf:
            # Used in ouster/osf/reader_base.h
            self.requires("flatbuffers/24.3.25", transitive_headers=True)
            self.requires("zlib/[>=1.2.11 <2]", transitive_libs=True)
            # Required by the bundled zpng encoder
            self.requires("zstd/[>=1.5 <1.6]")

        if self.options.build_viz:
            self.requires("glfw/3.4")
            self.requires("glad/2.0.8")

        if self.options.build_mapping:
            self.requires("ceres-solver/2.1.0")
            self.requires("onetbb/2023.1.0")
            # Replaces vendored Sophus, built with basic logging as upstream does
            self.requires("sophus/1.22.10", options={"with_fmt": False})

    def validate(self):
        check_min_cppstd(self, 14)

        if self.options.build_mapping and not self.options.build_osf:
            raise ConanInvalidConfiguration("build_mapping=True requires build_osf=True")

        if self.options.shared and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Shared builds are not supported on Windows")

    def build_requirements(self):
        if self.options.build_osf:
            self.tool_requires("flatbuffers/<host_version>")
        # ouster_algorithm and ouster_mapping require CMake 3.16.3+
        self.tool_requires("cmake/[>=3.16.3 <5]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SENSOR"] = self.options.build_sensor
        tc.cache_variables["BUILD_PCAP"] = self.options.build_pcap
        tc.cache_variables["BUILD_OSF"] = self.options.build_osf
        tc.cache_variables["BUILD_VIZ"] = self.options.build_viz
        tc.cache_variables["BUILD_MAPPING"] = self.options.build_mapping
        tc.cache_variables["BUILD_SHARED_LIBRARY"] = self.options.shared
        tc.cache_variables["OUSTER_USE_EIGEN_MAX_ALIGN_BYTES_32"] = self.options.eigen_max_align_bytes
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_PYTHON_MODULE"] = False
        tc.cache_variables["BUILD_PERCEPTION"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("flatbuffers", "cmake_target_name", "flatbuffers::flatbuffers")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        # Unvendor optional-lite
        rmdir(self, os.path.join(self.source_folder, "ouster_core", "include", "optional-lite"))
        replace_in_file(self, os.path.join(self.source_folder, "ouster_core", "CMakeLists.txt"),
                        " include/optional-lite", "")
        save(self, os.path.join(self.source_folder, "ouster_core", "CMakeLists.txt"),
             "find_package(optional-lite REQUIRED)\n"
             "target_link_libraries(ouster_core PUBLIC nonstd::optional-lite)\n",
             append=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        for license_file in ("LICENSE", "LICENSE-bin", "COPYRIGHT"):
            copy(self, license_file, dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        if self.options.shared:
            # INFO: the build always produces the static libraries, they are absorbed by shared_library
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OusterSDK")
        self.cpp_info.set_property("cmake_target_name", "OusterSDK::OusterSDK")
        # When shared_library is built, every component is absorbed into it and no
        # static archive is packaged
        produce_library = not self.options.shared

        # Version information, always linked into ouster_core
        self.cpp_info.components["ouster_build"].set_property("cmake_target_name", "OusterSDK::ouster_build")
        self.cpp_info.components["ouster_build"].libs = ["ouster_build"] if produce_library else []

        # Vendored NMEA parser, no ConanCenter recipe available
        self.cpp_info.components["nmea"].set_property("cmake_target_name", "OusterSDK::nmea")
        self.cpp_info.components["nmea"].libs = ["nmea"] if produce_library else []

        self.cpp_info.components["ouster_core"].set_property("cmake_target_name", "OusterSDK::ouster_core")
        self.cpp_info.components["ouster_core"].libs = ["ouster_core"] if produce_library else []
        self.cpp_info.components["ouster_core"].requires = [
            "ouster_build",
            "nmea",
            "eigen::eigen",
            "optional-lite::optional-lite",
            "tsl-robin-map::tsl-robin-map",
            "libzip::libzip",
            "openssl::crypto",
        ]
        if self.settings.os == "Windows":
            self.cpp_info.components["ouster_core"].system_libs = ["ws2_32"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ouster_core"].system_libs = ["pthread"]
        if self.options.eigen_max_align_bytes:
            self.cpp_info.components["ouster_core"].defines = ["EIGEN_MAX_ALIGN_BYTES=32"]

        self.cpp_info.components["ouster_algorithm"].set_property("cmake_target_name", "OusterSDK::ouster_algorithm")
        self.cpp_info.components["ouster_algorithm"].libs = ["ouster_algorithm"] if produce_library else []
        self.cpp_info.components["ouster_algorithm"].requires = [
            "ouster_core",
            "eigen::eigen",
        ]

        if self.options.build_sensor:
            self.cpp_info.components["ouster_sensor"].set_property("cmake_target_name", "OusterSDK::ouster_sensor")
            self.cpp_info.components["ouster_sensor"].libs = ["ouster_sensor"] if produce_library else []
            self.cpp_info.components["ouster_sensor"].requires = [
                "ouster_core",
                "eigen::eigen",
                "libcurl::libcurl",
            ]
            if self.settings.os == "Windows":
                self.cpp_info.components["ouster_sensor"].system_libs = ["ws2_32"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["ouster_sensor"].system_libs = ["pthread"]

        if self.options.build_pcap:
            self.cpp_info.components["ouster_pcap"].set_property("cmake_target_name", "OusterSDK::ouster_pcap")
            self.cpp_info.components["ouster_pcap"].libs = ["ouster_pcap"] if produce_library else []
            self.cpp_info.components["ouster_pcap"].requires = [
                "ouster_core",
                "libtins::libtins",
                "libpcap::libpcap",
            ]
            if self.settings.os == "Windows":
                self.cpp_info.components["ouster_pcap"].system_libs = ["ws2_32"]

        if self.options.build_osf:
            # Bundled zstd-based image encoder used by ouster_osf
            self.cpp_info.components["zpng"].set_property("cmake_target_name", "OusterSDK::zpng")
            self.cpp_info.components["zpng"].libs = ["zpng"] if produce_library else []
            self.cpp_info.components["zpng"].requires = ["zstd::zstd"]

            self.cpp_info.components["ouster_osf"].set_property("cmake_target_name", "OusterSDK::ouster_osf")
            self.cpp_info.components["ouster_osf"].libs = ["ouster_osf"] if produce_library else []
            self.cpp_info.components["ouster_osf"].requires = [
                "ouster_core",
                "zpng",
                "flatbuffers::flatbuffers",
                "libcurl::libcurl",
                "libpng::libpng",
                "zlib::zlib",
                "zstd::zstd",
            ]

        if self.options.build_viz:
            self.cpp_info.components["ouster_viz"].set_property("cmake_target_name", "OusterSDK::ouster_viz")
            self.cpp_info.components["ouster_viz"].libs = ["ouster_viz"] if produce_library else []
            self.cpp_info.components["ouster_viz"].requires = [
                "ouster_core",
                "glfw::glfw",
                "glad::glad",
                "libpng::libpng",
            ]
            if self.settings.os == "Macos":
                self.cpp_info.components["ouster_viz"].frameworks = ["AppKit"]

        if self.options.build_mapping:
            self.cpp_info.components["ouster_mapping"].set_property("cmake_target_name", "OusterSDK::ouster_mapping")
            self.cpp_info.components["ouster_mapping"].libs = ["ouster_mapping"] if produce_library else []
            self.cpp_info.components["ouster_mapping"].requires = [
                "ouster_algorithm",
                "ouster_core",
                "ouster_osf",
                "ceres-solver::ceres",
                "onetbb::libtbb",
                "sophus::sophus",
            ]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["ouster_mapping"].system_libs = ["gomp"]

        if self.options.shared:
            self.cpp_info.components["shared_library"].set_property("cmake_target_name", "OusterSDK::shared_library")
            self.cpp_info.components["shared_library"].libs = ["shared_library"]
            self.cpp_info.components["shared_library"].requires = ["ouster_core", "ouster_algorithm"]
            if self.options.build_sensor:
                self.cpp_info.components["shared_library"].requires.append("ouster_sensor")
            if self.options.build_osf:
                self.cpp_info.components["shared_library"].requires.append("ouster_osf")
            if self.options.build_pcap:
                self.cpp_info.components["shared_library"].requires.append("ouster_pcap")
            if self.options.build_viz:
                self.cpp_info.components["shared_library"].requires.append("ouster_viz")
            if self.options.build_mapping:
                self.cpp_info.components["shared_library"].requires.append("ouster_mapping")

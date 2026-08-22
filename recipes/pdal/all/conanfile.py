import os
import shutil
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, apply_conandata_patches, export_conandata_patches, load, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime

required_conan_version = ">=2.1"


class PdalConan(ConanFile):
    name = "pdal"
    description = "PDAL is Point Data Abstraction Library. GDAL for point cloud data."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pdal.io"
    topics = ("gdal", "point-cloud-data", "lidar")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_xml": [True, False],
        "with_zlib": [True, False],
        "with_lzma": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "with_xml": True,
        "with_zlib": True,
        "with_lzma": True,
        "with_zstd": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("gdal/[>=3.4 <4]")
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("libgeotiff/1.7.1")
        self.requires("proj/9.3.1")
        if self.options.with_xml:
            self.requires("libxml2/[>=2.12.5 <3]")
        if self.options.with_zstd:
            self.requires("zstd/[>=1.5 <1.6]")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_lzma:
            self.requires("xz_utils/[>=5.4.5 <6]")

    def validate(self):
        check_min_cppstd(self, 17)
        if is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("It does not support static runtime. Use -s compiler.runtime=shared")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        # Make it explicit so cross-builds can still locate the built tool.
        dimbuilder_suffix = ".exe" if self.settings.os == "Windows" else ""
        tc.cache_variables["DIMBUILDER_EXECUTABLE"] = os.path.join(self.build_folder, "bin", f"dimbuilder{dimbuilder_suffix}").replace("\\", "/")
        tc.cache_variables["WITH_TESTS"] = False
        tc.cache_variables["WITH_ZSTD"] = self.options.with_zstd
        tc.cache_variables["WITH_ZLIB"] = self.options.with_zlib
        tc.cache_variables["WITH_LZMA"] = self.options.with_lzma
        tc.cache_variables["WITH_BACKTRACE"] = False
        tc.cache_variables["WITH_GCS"] = False
        tc.cache_variables["WITH_COMPLETION"] = False
        tc.cache_variables["BUILD_DOCS"] = False
        tc.cache_variables["BUILD_TOOLS_LASDUMP"] = False
        tc.cache_variables["BUILD_TOOLS_LASDUMP"] = False
        tc.cache_variables["ZSTD_FOUND"] = self.options.with_zstd
        tc.cache_variables["LIBXML2_FOUND"] = self.options.with_xml
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_LibXml2"] = not self.options.with_xml
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Libexecinfo"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Libunwind"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        shutil.copy(os.path.join(self.source_folder, "vendor", "arbiter", "LICENSE"), os.path.join(self.package_folder, "licenses", "arbiter_LICENSE.txt"))
        shutil.copy(os.path.join(self.source_folder, "vendor", "utfcpp", "LICENSE"), os.path.join(self.package_folder, "licenses", "utfcpp_LICENSE.txt"))
        content = load(self, os.path.join(self.source_folder, "vendor", "eigen", "Eigen", "Core"))
        save(self, os.path.join(self.package_folder, "licenses", "eigen_LICENSE.txt"), content[:content.find("\n\n") + 1])
        content = load(self, os.path.join(self.source_folder, "vendor", "gtest", "include", "gtest", "gtest.h"))
        save(self, os.path.join(self.package_folder, "licenses", "gtest_LICENSE.txt"), content[:content.find("\n\n") + 1])
        content = load(self, os.path.join(self.source_folder, "vendor", "h3", "include", "h3api.h"))
        save(self, os.path.join(self.package_folder, "licenses", "h3_LICENSE.txt"), content[:content.find("*/\n") + 3])
        content = load(self, os.path.join(self.source_folder, "vendor", "kazhdan", "Factor.cpp"))
        save(self, os.path.join(self.package_folder, "licenses", "kazhdan_LICENSE.txt"), content[3:content.find("*/\n")])
        content = load(self, os.path.join(self.source_folder, "vendor", "lazperf", "lazperf.hpp"))
        save(self, os.path.join(self.package_folder, "licenses", "lazperf_LICENSE.txt"), content[3:content.find("*/\n")])
        content = load(self, os.path.join(self.source_folder, "vendor", "lepcc", "src", "LEPCC.h"))
        save(self, os.path.join(self.package_folder, "licenses", "lepcc_LICENSE.txt"), content[3:content.find("*/\n")])
        content = load(self, os.path.join(self.source_folder, "vendor", "nanoflann", "nanoflann.hpp"))
        save(self, os.path.join(self.package_folder, "licenses", "nanoflann_LICENSE.txt"), content[:content.find("*/\n") + 3])
        content = load(self, os.path.join(self.source_folder, "vendor", "nlohmann", "nlohmann", "json.hpp"))
        save(self, os.path.join(self.package_folder, "licenses", "nlohmann_json_LICENSE.txt"), content[:content.find("*/\n") + 3])
        content = load(self, os.path.join(self.source_folder, "vendor", "schema-validator", "json-schema.hpp"))
        save(self, os.path.join(self.package_folder, "licenses", "schema-validator_LICENSE.txt"), content[:content.find("*/\n") + 3])

        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PDAL")
        self.cpp_info.set_property("pkg_config_name", "pdal")
        self.cpp_info.libs = ["pdalcpp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["shlwapi", "ws2_32"]

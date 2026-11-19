from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir

import os

required_conan_version = ">=2.0.0"


class OpenTimelineIOConan(ConanFile):
    name = "opentimelineio"
    description = "Open Source API and interchange format for editorial timeline information."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AcademySoftwareFoundation/OpenTimelineIO"
    topics = ("opentimelineio", "video", "aswf")
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        check_min_cppstd(self, 17)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("imath/[>=3.1.9 <4]", transitive_headers=True)
        self.requires("rapidjson/cci.20250205")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.18.2 <5]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["OTIO_FIND_IMATH"] = True
        tc.cache_variables["OTIO_FIND_RAPIDJSON"] = True
        tc.cache_variables["OTIO_AUTOMATIC_SUBMODULES"] = False
        tc.cache_variables["OTIO_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["BUILD_TESTING"] = False
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "NOTICE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)
        # Remove cmake files installed to the "share" folder.
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.os == "Windows" and self.options.shared:
            # Upstream installs DLLs into lib/
            lib_folder = os.path.join(self.package_folder, "lib")
            copy(self, "*.dll", src=lib_folder, dst=os.path.join(self.package_folder, "bin"))
            rm(self, "*.dll", lib_folder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenTimelineIO")

        # Upstream sets a "d" DEBUG_POSTFIX on Windows
        postfix = "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""
        # Upstream exports these as PUBLIC definitions (*_EXPORTS avoids dllimport on constexpr data in shared builds)
        kind = "EXPORTS" if self.options.shared else "STATIC"

        opentime = self.cpp_info.components["opentime"]
        opentime.set_property("cmake_target_name", "OTIO::opentime")
        opentime.libs = [f"opentime{postfix}"]
        opentime.defines = [f"OPENTIME_{kind}"]

        opentimelineio = self.cpp_info.components["opentimelineio"]
        opentimelineio.set_property("cmake_target_name", "OTIO::opentimelineio")
        opentimelineio.libs = [f"opentimelineio{postfix}"]
        opentimelineio.defines = [f"OTIO_{kind}"]
        opentimelineio.requires = ["opentime", "imath::imath", "rapidjson::rapidjson"]

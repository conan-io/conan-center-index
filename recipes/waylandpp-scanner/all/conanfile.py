from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    copy,
    get,
    rm,
    rmdir,
)
from conan.tools.gnu import PkgConfigDeps
import os


required_conan_version = ">=2.0.9"


class WaylandppScannerConan(ConanFile):
    name = "waylandpp-scanner"
    description = "Standalone package for wayland-scanner++"
    package_type = "application"
    license = "DocumentRef-LICENSE:LicenseRef-waylandpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NilsBrause/waylandpp"
    topics = ("wayland", "protocol", "compositor", "display")
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("pugixml/1.15")

    def validate(self):
        check_min_cppstd(self, 11)
        if self.settings.os not in ("Linux", "Android"):
            raise ConanInvalidConfiguration(
                f"{self.ref} only supports Linux or Android"
            )

    def build_requirements(self):
        # https://github.com/NilsBrause/waylandpp/issues/97
        self.tool_requires("cmake/[>=3.22.6]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables.update({"BUILD_SCANNER": True, "BUILD_LIBRARIES": False})
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "waylandpp")
        self.cpp_info.set_property("pkg_config_name", "wayland-scanner++")
        self.cpp_info.set_property("component_version", self.version)
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        pkgconfig_variables = {
            "datarootdir": "${prefix}/share",
            "pkgdatadir": "${prefix}/share/waylandpp",
            "wayland_scannerpp": "${prefix}/bin/wayland-scanner++",
        }

        self.cpp_info.components["wayland-scanner++"].set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items()),
        )

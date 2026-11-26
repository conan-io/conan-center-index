from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    copy,
    export_conandata_patches,
    get,
    rm,
    rmdir,
)
from conan.tools.gnu import PkgConfigDeps
import os


required_conan_version = ">=2.0.9"


class WaylandppConan(ConanFile):
    name = "waylandpp"
    description = "An easy to use C++ API for Wayland"
    package_type = "library"
    license = "DocumentRef-LICENSE:LicenseRef-waylandpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NilsBrause/waylandpp"
    topics = ("wayland", "protocol", "compositor", "display")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_server": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_server": True,
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("wayland/1.23.92", transitive_headers=True)
        self.requires("wayland-protocols/1.45")

    def validate(self):
        check_min_cppstd(self, 11)
        if self.settings.os not in ("Linux", "Android"):
            raise ConanInvalidConfiguration(
                f"{self.ref} only supports Linux or Android"
            )

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires(f"waylandpp-scanner/{self.version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def waylandpp_scanner_path(self):
        wayland_scanner = self.dependencies.build["waylandpp-scanner"]
        wayland_bin_dir = wayland_scanner.cpp_info.bindirs[0]
        return os.path.join(wayland_bin_dir, "wayland-scanner++")

    def generate(self):
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables.update(
            {
                "BUILD_DOCUMENTATION": False,
                "INSTALL_EXPERIMENTAL_PROTOCOLS": False,
                "USE_SYSTEM_PROTOCOLS": True,
                "BUILD_LIBRARIES": True,
                "BUILD_SCANNER": False,
                "BUILD_SERVER": self.options.with_server,
                "WAYLAND_SCANNERPP": self.waylandpp_scanner_path,
            }
        )
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
        client_components = [
            {
                "name": "wayland-client++",
                "dependencies": ["wayland::wayland-client"],
                "system_libs": ["m"],
            },
            {
                "name": "wayland-egl++",
                "dependencies": ["wayland::wayland-egl", "wayland-client++"],
            },
            {
                "name": "wayland-cursor++",
                "dependencies": ["wayland::wayland-cursor", "wayland-client++"],
            },
            {
                "name": "wayland-client-extra++",
                "dependencies": ["wayland::wayland-client", "wayland-client++"],
            },
            {
                "name": "wayland-client-staging++",
                "dependencies": ["wayland::wayland-client", "wayland-client++"],
            },
            {
                "name": "wayland-client-unstable++",
                "dependencies": ["wayland::wayland-client", "wayland-client++"],
            },
        ]

        server_components = [
            {
                "name": "wayland-server++",
                "dependencies": ["wayland::wayland-server"],
                "system_libs": ["m"],
            },
            {
                "name": "wayland-server-extra++",
                "dependencies": ["wayland::wayland-server", "wayland-server++"],
                "system_libs": ["m"],
            },
            {
                "name": "wayland-server-staging++",
                "dependencies": ["wayland::wayland-server", "wayland-server++"],
                "system_libs": ["m"],
            },
            {
                "name": "wayland-server-unstable++",
                "dependencies": ["wayland::wayland-server", "wayland-server++"],
                "system_libs": ["m"],
            },
        ]

        components = client_components
        if self.options.with_server:
            components += server_components

        for component in components:
            name = component["name"]
            component_info = self.cpp_info.components[name]
            component_info.libs = [name]
            component_info.set_property("pkg_config_name", name)
            component_info.set_property("component_version", self.version)
            component_info.set_property("cmake_target_name", f"Waylandpp::{name}")
            component_info.requires = component["dependencies"] + [
                "wayland-protocols::wayland-protocols"
            ]
            if "system_libs" in component:
                component_info.system_libs = component["system_libs"]

            pkgconfig_variables = {
                "datarootdir": "${prefix}/share",
                "pkgdatadir": "${prefix}/share/waylandpp",
            }

            self.cpp_info.components[name].set_property(
                "pkg_config_custom_content",
                "\n".join(
                    f"{key}={value}" for key, value in pkgconfig_variables.items()
                ),
            )

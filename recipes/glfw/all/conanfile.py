from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.60.0 <2 || >=2.0.5"


class GlfwConan(ConanFile):
    name = "glfw"
    description = "GLFW is a free, Open Source, multi-platform library for OpenGL, OpenGL ES and Vulkan" \
                  "application development. It provides a simple, platform-independent API for creating" \
                  "windows, contexts and surfaces, reading input, handling events, etc."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/glfw/glfw"
    topics = ("graphics", "opengl", "vulkan", "opengl-es")
    package_type = "library"
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "vulkan_static": [True, False],
        "with_x11": [True, False],
        "with_wayland": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "vulkan_static": False,
        "with_x11": True,
        "with_wayland": False,
    }

    @property
    def _has_build_profile(self):
        return hasattr(self, "settings_build")

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        if self.settings.os != "Linux":
            self.options.rm_safe("with_wayland")
        if self.settings.os not in ["Linux", "FreeBSD"] or Version(self.version) <= "3.3.8":
            self.options.rm_safe("with_x11")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

        if self.options.get_safe("with_wayland"):
            self.options["xkbcommon"].with_wayland = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opengl/system")
        if self.options.vulkan_static:
            self.requires("vulkan-loader/1.3.268.0")
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.get_safe("with_x11", True):
                self.requires("xorg/system")
        if self.options.get_safe("with_wayland"):
            self.requires("wayland/1.22.0")
            self.requires("xkbcommon/1.6.0")

    def validate(self):
        if self.options.get_safe("with_wayland") and not self.dependencies["xkbcommon"].options.with_wayland:
            raise ConanInvalidConfiguration(f"{self.ref} requires the with_wayland option in xkbcommon to be enabled when the with_wayland option is enabled")

    def build_requirements(self):
        if self.options.get_safe("with_wayland"):
            self.tool_requires("wayland-protocols/1.33")
            if self._has_build_profile:
                self.tool_requires("wayland/<host_version>")
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if self.options.get_safe("with_wayland") and not self._has_build_profile:
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = CMakeToolchain(self)
        tc.cache_variables["GLFW_BUILD_DOCS"] = False
        tc.cache_variables["GLFW_BUILD_EXAMPLES"] = False
        tc.cache_variables["GLFW_BUILD_TESTS"] = False
        tc.cache_variables["GLFW_INSTALL"] = True
        if Version(self.version) > "3.3.8":
            tc.cache_variables["GLFW_BUILD_X11"] = self.options.get_safe("with_x11", False)
            tc.cache_variables["GLFW_BUILD_WAYLAND"] = self.options.get_safe("with_wayland", False)
        else:
            tc.cache_variables["GLFW_USE_WAYLAND"] = self.options.get_safe("with_wayland", False)
        tc.variables["GLFW_VULKAN_STATIC"] = self.options.vulkan_static
        if is_msvc(self):
            tc.cache_variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.generate()
        cmake_deps = CMakeDeps(self)
        if self.options.get_safe("with_wayland"):
            cmake_deps.set_property("xkbcommon", "cmake_file_name", "XKBCommon")
        cmake_deps.generate()
        if self.options.get_safe("with_wayland"):
            pkg_config_deps = PkgConfigDeps(self)
            if self._has_build_profile:
                pkg_config_deps.build_context_activated = ["wayland-protocols"]
            else:
                # Manually generate pkgconfig file of wayland-protocols since
                # PkgConfigDeps.build_context_activated can't work with legacy 1 profile
                wp_prefix = self.dependencies.build["wayland-protocols"].package_folder
                wp_version = self.dependencies.build["wayland-protocols"].ref.version
                wp_pkg_content = textwrap.dedent(f"""\
                    prefix={wp_prefix}
                    datarootdir=${{prefix}}/res
                    pkgdatadir=${{datarootdir}}/wayland-protocols
                    Name: Wayland Protocols
                    Description: Wayland protocol files
                    Version: {wp_version}
                """)
                save(self, os.path.join(self.generators_folder, "wayland-protocols.pc"), wp_pkg_content)
            pkg_config_deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # don't force PIC
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                              "POSITION_INDEPENDENT_CODE ON", "")
        # don't force static link to libgcc if MinGW
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                              "target_link_libraries(glfw PRIVATE \"-static-libgcc\")", "")

        # Allow to link vulkan-loader into shared glfw
        if self.options.vulkan_static:
            cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
            replace_in_file(
                self,
                cmakelists,
                'message(FATAL_ERROR "You are trying to link the Vulkan loader static library into the GLFW shared library")',
                "",
            )
            vulkan_lib = self.dependencies["vulkan-loader"].cpp_info.libs[0]
            replace_in_file(
                self,
                cmakelists,
                'list(APPEND glfw_PKG_DEPS "vulkan")',
                f'list(APPEND glfw_PKG_DEPS "vulkan")\nlist(APPEND glfw_LIBRARIES "{vulkan_lib}")',
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"glfw": "glfw::glfw"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "glfw3")
        self.cpp_info.set_property("cmake_target_name", "glfw")
        self.cpp_info.set_property("pkg_config_name", "glfw3")
        libname = "glfw"
        if self.settings.os == "Windows" or not self.options.shared:
            libname += "3"
        if self.settings.os == "Windows" and self.options.shared:
            libname += "dll"
            self.cpp_info.defines.append("GLFW_DLL")
        self.cpp_info.libs = [libname]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl", "rt"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("gdi32")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend([
                "AppKit", "Cocoa", "CoreFoundation", "CoreGraphics",
                "CoreServices", "Foundation", "IOKit",
            ])

        # backward support of cmake_find_package, cmake_find_package_multi & pkg_config generators
        self.cpp_info.filenames["cmake_find_package"] = "glfw3"
        self.cpp_info.filenames["cmake_find_package_multi"] = "glfw3"
        self.cpp_info.names["cmake_find_package"] = "glfw"
        self.cpp_info.names["cmake_find_package_multi"] = "glfw"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "glfw3"

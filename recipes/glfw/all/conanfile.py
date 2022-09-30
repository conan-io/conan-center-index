from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os
import textwrap

required_conan_version = ">=1.47.0"


class GlfwConan(ConanFile):
    name = "glfw"
    description = "GLFW is a free, Open Source, multi-platform library for OpenGL, OpenGL ES and Vulkan" \
                  "application development. It provides a simple, platform-independent API for creating" \
                  "windows, contexts and surfaces, reading input, handling events, etc."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/glfw/glfw"
    topics = ("graphics", "opengl", "vulkan", "opengl-es")

    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "vulkan_static": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "vulkan_static": False,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def requirements(self):
        self.requires("opengl/system")
        if self.options.vulkan_static:
            self.requires("vulkan-loader/1.3.216.0")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GLFW_BUILD_EXAMPLES"] = False
        tc.variables["GLFW_BUILD_TESTS"] = False
        tc.variables["GLFW_BUILD_DOCS"] = False
        tc.variables["GLFW_INSTALL"] = True
        tc.variables["GLFW_VULKAN_STATIC"] = self.options.vulkan_static
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # don't force PIC
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                              "POSITION_INDEPENDENT_CODE ON", "")
        # Allow to link vulkan-loader into shared glfw
        if self.options.vulkan_static:
            cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
            replace_in_file(self, cmakelists,
                                  'message(FATAL_ERROR "You are trying to link the Vulkan loader static library into the GLFW shared library")',
                                  "")
            replace_in_file(self, cmakelists,
                                  'list(APPEND glfw_PKG_DEPS "vulkan")',
                                  ('list(APPEND glfw_PKG_DEPS "vulkan")\n'
                                   'list(APPEND glfw_LIBRARIES "{}")').format(self.deps_cpp_info["vulkan-loader"].libs[0]))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
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
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "glfw3")
        self.cpp_info.set_property("cmake_target_name", "glfw")
        self.cpp_info.set_property("pkg_config_name", "glfw3")
        libname = "glfw"
        if self.settings.os == "Windows" or not self.options.shared:
            libname += "3"
        if is_msvc(self) and self.options.shared:
            libname += "dll"
        self.cpp_info.libs = [libname]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl", "rt"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("gdi32")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["Cocoa", "IOKit", "CoreFoundation"])

        # backward support of cmake_find_package, cmake_find_package_multi & pkg_config generators
        self.cpp_info.filenames["cmake_find_package"] = "glfw3"
        self.cpp_info.filenames["cmake_find_package_multi"] = "glfw3"
        self.cpp_info.names["cmake_find_package"] = "glfw"
        self.cpp_info.names["cmake_find_package_multi"] = "glfw"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "glfw3"

        # FIXME: shouldn't be necessary.
        # It's a workaround to support conan v1 generators
        self.cpp_info.requires.append("opengl::opengl")
        if self.options.vulkan_static:
            self.cpp_info.requires.append("vulkan-loader::vulkan-loader")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.requires.append("xorg::xorg")

import os
import glob
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.28.0"


class GlfwConan(ConanFile):
    name = "glfw"
    description = "GLFW is a free, Open Source, multi-platform library for OpenGL, OpenGL ES and Vulkan" \
                  "application development. It provides a simple, platform-independent API for creating" \
                  "windows, contexts and surfaces, reading input, handling events, etc."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/glfw/glfw"
    topics = ("conan", "gflw", "opengl", "vulkan", "opengl-es")

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

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("opengl/system")
        if self.options.vulkan_static:
            self.requires("vulkan-loader/1.2.162.0")
        if self.settings.os == "Linux":
            self.requires("xorg/system")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # don't force PIC
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                              "POSITION_INDEPENDENT_CODE ON", "")
        # Allow to link vulkan-loader into shared glfw
        if self.options.vulkan_static:
            cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
            tools.replace_in_file(cmakelists,
                                  'message(FATAL_ERROR "You are trying to link the Vulkan loader static library into the GLFW shared library")',
                                  "")
            tools.replace_in_file(cmakelists,
                                  'list(APPEND glfw_PKG_DEPS "vulkan")',
                                  ('list(APPEND glfw_PKG_DEPS "vulkan")\n'
                                   'list(APPEND glfw_LIBRARIES "{}")').format(self.deps_cpp_info["vulkan-loader"].libs[0]))

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["GLFW_BUILD_EXAMPLES"] = False
            self._cmake.definitions["GLFW_BUILD_TESTS"] = False
            self._cmake.definitions["GLFW_BUILD_DOCS"] = False
            self._cmake.definitions["GLFW_INSTALL"] = True
            self._cmake.definitions["GLFW_VULKAN_STATIC"] = self.options.vulkan_static
            if self.settings.compiler == "Visual Studio":
                self._cmake.definitions["USE_MSVC_RUNTIME_LIBRARY_DLL"] = "MD" in self.settings.compiler.runtime
            self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_subfolder, self._module_file),
            {"glfw": "glfw::glfw"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += (
                "if(TARGET {aliased} AND NOT TARGET {alias})\n"
                "    add_library({alias} INTERFACE IMPORTED)\n"
                "    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})\n"
                "endif()\n"
            ).format(alias=alias, aliased=aliased)
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return "conan-official-{}-targets.cmake".format(self.name)

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "glfw3"
        self.cpp_info.filenames["cmake_find_package_multi"] = "glfw3"
        self.cpp_info.names["cmake_find_package"] = "glfw"
        self.cpp_info.names["cmake_find_package_multi"] = "glfw"
        self.cpp_info.names["pkg_config"] = "glfw3"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules = [os.path.join(self._module_subfolder, self._module_file)]
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m", "pthread", "dl", "rt"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("gdi32")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["Cocoa", "IOKit", "CoreFoundation"])

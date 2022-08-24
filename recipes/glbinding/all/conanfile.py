from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.43.0"


class GlbindingConan(ConanFile):
    name = "glbinding"
    description = "A C++ binding for the OpenGL API, generated using the gl.xml specification."
    license = "MIT"
    topics = ("glbinding", "opengl", "binding")
    homepage = "https://glbinding.org/"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # Don't force PIC
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "cmake", "CompileOptions.cmake"),
                              "POSITION_INDEPENDENT_CODE ON", "")
        # Don't replace /W3 by /W4
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "cmake", "CompileOptions.cmake"),
                              "/W4", "")
        # No whole program optimization
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "cmake", "CompileOptions.cmake"),
                              "/GL", "")
        # Don't populate rpath
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "if(NOT SYSTEM_DIR_INSTALL)", "if(0)")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["OPTION_SELF_CONTAINED"] = False
        cmake.definitions["OPTION_BUILD_TESTS"] = False
        cmake.definitions["OPTION_BUILD_DOCS"] = False
        cmake.definitions["OPTION_BUILD_TOOLS"] = False
        cmake.definitions["OPTION_BUILD_EXAMPLES"] = False
        cmake.definitions["OPTION_BUILD_WITH_BOOST_THREAD"] = False
        cmake.definitions["OPTION_BUILD_CHECK"] = False
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "glbinding")

        suffix = "d" if self.settings.build_type == "Debug" else ""
        # glbinding
        self.cpp_info.components["_glbinding"].set_property("cmake_target_name", "glbinding::glbinding")
        self.cpp_info.components["_glbinding"].libs = ["glbinding" + suffix]
        self.cpp_info.components["_glbinding"].requires = ["khrplatform"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_glbinding"].system_libs = ["dl", "pthread"]
        # glbinding-aux
        self.cpp_info.components["glbinding-aux"].set_property("cmake_target_name", "glbinding::glbinding-aux")
        self.cpp_info.components["glbinding-aux"].libs = ["glbinding-aux" + suffix]
        self.cpp_info.components["glbinding-aux"].requires = ["_glbinding"]
        # KHRplatform
        self.cpp_info.components["khrplatform"].set_property("cmake_target_name", "glbinding::KHRplatform")
        self.cpp_info.components["khrplatform"].libdirs = []

        # workaround to propagate all components in CMakeDeps generator
        self.cpp_info.set_property("cmake_file_name", "glbinding::glbinding-aux")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "glbinding"
        self.cpp_info.names["cmake_find_package_multi"] = "glbinding"
        self.cpp_info.components["_glbinding"].names["cmake_find_package"] = "glbinding"
        self.cpp_info.components["_glbinding"].names["cmake_find_package_multi"] = "glbinding"
        self.cpp_info.components["glbinding-aux"].names["cmake_find_package"] = "glbinding-aux"
        self.cpp_info.components["glbinding-aux"].names["cmake_find_package_multi"] = "glbinding-aux"
        self.cpp_info.components["khrplatform"].names["cmake_find_package"] = "KHRplatform"
        self.cpp_info.components["khrplatform"].names["cmake_find_package_multi"] = "KHRplatform"

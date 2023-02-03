from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir
import os

required_conan_version = ">=1.50.0"


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

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OPTION_SELF_CONTAINED"] = False
        tc.variables["OPTION_BUILD_TESTS"] = False
        tc.variables["OPTION_BUILD_DOCS"] = False
        tc.variables["OPTION_BUILD_TOOLS"] = False
        tc.variables["OPTION_BUILD_EXAMPLES"] = False
        tc.variables["OPTION_BUILD_WITH_BOOST_THREAD"] = False
        tc.variables["OPTION_BUILD_CHECK"] = False
        # TODO: might be a good idea to fix upstream CMakeLists to not rely on
        # WriteCompilerDetectionHeader, and just use cxx_std_11 compile feature
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0120"] = "OLD"
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        compile_options = os.path.join(self.source_folder, "cmake", "CompileOptions.cmake")
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # Don't force PIC
        replace_in_file(self, compile_options, "POSITION_INDEPENDENT_CODE ON", "")
        # Don't replace /W3 by /W4
        replace_in_file(self, compile_options, "/W4", "")
        # No whole program optimization
        replace_in_file(self, compile_options, "/GL", "")
        # Don't populate rpath
        replace_in_file(self, cmakelists, "if(NOT SYSTEM_DIR_INSTALL)", "if(0)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

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
        self.cpp_info.set_property("cmake_target_name", "glbinding::glbinding-aux")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "glbinding"
        self.cpp_info.names["cmake_find_package_multi"] = "glbinding"
        self.cpp_info.components["_glbinding"].names["cmake_find_package"] = "glbinding"
        self.cpp_info.components["_glbinding"].names["cmake_find_package_multi"] = "glbinding"
        self.cpp_info.components["glbinding-aux"].names["cmake_find_package"] = "glbinding-aux"
        self.cpp_info.components["glbinding-aux"].names["cmake_find_package_multi"] = "glbinding-aux"
        self.cpp_info.components["khrplatform"].names["cmake_find_package"] = "KHRplatform"
        self.cpp_info.components["khrplatform"].names["cmake_find_package_multi"] = "KHRplatform"

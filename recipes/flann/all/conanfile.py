from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rm, rmdir, save
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.50.0"


class FlannConan(ConanFile):
    name = "flann"
    description = "Fast Library for Approximate Nearest Neighbors"
    topics = ("flann", "nns", "nearest-neighbor-search", "knn", "kd-tree")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.cs.ubc.ca/research/flann/"
    license = "BSD-3-Clause"

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

    def requirements(self):
        self.requires("lz4/1.9.3")

    def validate(self):
        if Version(self.version) >= "1.9.2" and self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_C_BINDINGS"] = True
        # Only build the C++ libraries
        tc.variables["BUILD_DOC"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_MATLAB_BINDINGS"] = False
        tc.variables["BUILD_PYTHON_BINDINGS"] = False
        # OpenMP support can be added later if needed
        tc.variables["USE_OPENMP"] = False
        # Generate a relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        # remove embedded lz4
        rmdir(self, os.path.join(self.source_folder, "src", "cpp", "flann", "ext"))

        if Version(self.version) < "1.9.2":
            # Workaround issue with empty sources for a CMake target
            flann_cpp_dir = os.path.join(self.source_folder, "src", "cpp")
            save(self, os.path.join(flann_cpp_dir, "empty.cpp"), "\n")

            replace_in_file(self,
                os.path.join(flann_cpp_dir, "CMakeLists.txt"),
                'add_library(flann_cpp SHARED "")',
                'add_library(flann_cpp SHARED empty.cpp)'
            )
            replace_in_file(self,
                os.path.join(flann_cpp_dir, "CMakeLists.txt"),
                'add_library(flann SHARED "")',
                'add_library(flann SHARED empty.cpp)'
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # Remove vc runtimes
        if self.settings.os == "Windows":
            if self.options.shared:
                for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
                    rm(self, dll_pattern_to_remove, os.path.join(self.package_folder, "bin"))
            else:
                rmdir(self, os.path.join(self.package_folder, "bin"))
        # Remove static/dynamic libraries depending on the build mode
        libs_pattern_to_remove = ["*flann_cpp_s.*", "*flann_s.*"] if self.options.shared else ["*flann_cpp.*", "*flann.*"]
        for lib_pattern_to_remove in libs_pattern_to_remove:
            rm(self, lib_pattern_to_remove, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "Flann")
        self.cpp_info.set_property("cmake_file_name", "flann")
        self.cpp_info.set_property("pkg_config_name", "flann")

        # flann_cpp
        flann_cpp_lib = "flann_cpp" if self.options.shared else "flann_cpp_s"
        self.cpp_info.components["flann_cpp"].set_property("cmake_target_name", "flann::{}".format(flann_cpp_lib))
        self.cpp_info.components["flann_cpp"].libs = [flann_cpp_lib]
        if not self.options.shared and tools_legacy.stdcpp_library(self):
            self.cpp_info.components["flann_cpp"].system_libs.append(tools_legacy.stdcpp_library(self))
        self.cpp_info.components["flann_cpp"].requires = ["lz4::lz4"]

        # flann
        flann_c_lib = "flann" if self.options.shared else "flann_s"
        self.cpp_info.components["flann_c"].set_property("cmake_target_name", "flann::{}".format(flann_c_lib))
        self.cpp_info.components["flann_c"].libs = [flann_c_lib]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["flann_c"].system_libs.append("m")
        if not self.options.shared:
            self.cpp_info.components["flann_c"].defines.append("FLANN_STATIC")
        self.cpp_info.components["flann_c"].requires = ["flann_cpp"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Flann"
        self.cpp_info.names["cmake_find_package_multi"] = "flann"
        self.cpp_info.components["flann_cpp"].names["cmake_find_package"] = flann_cpp_lib
        self.cpp_info.components["flann_cpp"].names["cmake_find_package_multi"] = flann_cpp_lib
        self.cpp_info.components["flann_c"].names["cmake_find_package"] = flann_c_lib
        self.cpp_info.components["flann_c"].names["cmake_find_package_multi"] = flann_c_lib

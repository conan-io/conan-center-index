import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, save, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class IgnitionMathConan(ConanFile):
    name = "ignition-math"
    description = "Math classes and functions for robot applications"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gazebosim.org/libs/math"
    topics = ("ignition", "math", "robotics", "gazebo")

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

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warning(f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support.")
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires c++17 support. "
                    f"The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it.")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)
        self.requires("swig/4.1.1")

    def validate(self):
        if is_apple_os(self) and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("sorry, M1 builds are not currently supported, giving up!")

    def build_requirements(self):
        if Version(self.version) <= "6.8":
            self.tool_requires("ignition-cmake/2.5.0")
        else:
            self.tool_requires("ignition-cmake/2.10.0")
        self.tool_requires("doxygen/1.9.4")
        self.tool_requires("swig/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.build_context_activated = ["ignition-cmake"]
        deps.build_context_build_modules = ["ignition-cmake"]
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "src", "ruby", "CMakeLists.txt"), "${SWIG_USE_FILE}", "UseSWIG")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _create_cmake_module_variables(self, module_file, version):
        content = textwrap.dedent(f"""\
            set(ignition-math{version.major}_VERSION_MAJOR {version.major})
            set(ignition-math{version.major}_VERSION_MINOR {version.minor})
            set(ignition-math{version.major}_VERSION_PATCH {version.patch})
            set(ignition-math{version.major}_VERSION_STRING "{version.major}.{version.minor}.{version.patch}")
            set(ignition-math{version.major}_INCLUDE_DIRS "${{CMAKE_CURRENT_LIST_DIR}}/../../include/ignition/math{version.major}")
        """)
        save(self, module_file, content)

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        self._create_cmake_module_variables(os.path.join(self.package_folder, self._module_file_rel_path), Version(self.version))

        # Remove MS runtime files
        for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
            rm(self, dll_pattern_to_remove, os.path.join(self.package_folder, "bin"), recursive=True)

    @property
    def _module_file_rel_dir(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_file_rel_dir, f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        version_major = str(Version(self.version).major)
        lib_name = f"ignition-math{version_major}"

        # Based on https://github.com/gazebosim/gz-math/blob/ignition-math6_6.10.0/examples/CMakeLists.txt
        self.cpp_info.set_property("cmake_file_name", lib_name)
        self.cpp_info.set_property("cmake_target_name", f"{lib_name}::{lib_name}")

        main_component = self.cpp_info.components[lib_name]
        main_component.libs = [lib_name]
        main_component.includedirs.append(os.path.join("include", "ignition", "math" + version_major))
        main_component.requires = ["swig::swig", "eigen::eigen"]

        eigen3_component = self.cpp_info.components["eigen3"]
        eigen3_component.includedirs.append(os.path.join("include", "ignition", "math" + version_major))
        eigen3_component.requires = ["eigen::eigen"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = lib_name
        self.cpp_info.names["cmake_find_package_multi"] = lib_name
        self.cpp_info.names["cmake_paths"] = lib_name
        main_component.names["cmake_find_package"] = lib_name
        main_component.names["cmake_find_package_multi"] = lib_name
        main_component.names["cmake_paths"] = lib_name
        main_component.builddirs = [self._module_file_rel_dir]
        main_component.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        main_component.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        main_component.build_modules["cmake_paths"] = [self._module_file_rel_path]
        eigen3_component.names["cmake_find_package"] = "eigen3"
        eigen3_component.names["cmake_find_package_multi"] = "eigen3"
        eigen3_component.names["cmake_paths"] = "eigen3"
        eigen3_component.builddirs = [self._module_file_rel_dir]
        eigen3_component.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        eigen3_component.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        eigen3_component.build_modules["cmake_paths"] = [self._module_file_rel_path]

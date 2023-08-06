import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir, replace_in_file, load, save
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class IgnitionToolsConan(ConanFile):
    name = "ignition-tools"
    description = "Ignition entry point for using all the suite of ignition tools."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ignitionrobotics.org/libs/tools"
    topics = ("ignition", "robotics", "tools", "gazebo")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("backward-cpp/1.6")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warning(
                f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support."
            )
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires c++17 support. "
                    f"The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["USE_SYSTEM_BACKWARDCPP"] = True
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["BUILD_TESTING"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        for cmakelists in self.source_path.rglob("CMakeLists.txt"):
            replace_in_file(self, cmakelists, "${CMAKE_SOURCE_DIR}", "${PROJECT_SOURCE_DIR}", strict=False)
            replace_in_file(self, cmakelists, "${CMAKE_BINARY_DIR}", "${PROJECT_BINARY_DIR}", strict=False)
        # Generating ign.rb fails on Windows, do it outside of CMake in package() instead
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                        "# Two steps to create `ign`", "return() #")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        cmake = CMake(self)
        cmake.install()

        # Generate ign.rb
        ign_rb_content = load(self, os.path.join(self.source_folder, "src", "ign.in"))
        ign_rb_content = ign_rb_content.replace("@CMAKE_INSTALL_PREFIX@", self.package_folder.replace("\\", "/"))
        ign_rb_content = ign_rb_content.replace("@ENV_PATH_DELIMITER@", os.pathsep)
        suffix = ".rb" if self.settings.os == "Windows" else ""
        ign_rb_path = os.path.join(self.package_folder, "bin", f"ign{suffix}")
        save(self, ign_rb_path, ign_rb_content)
        self._chmod_plus_x(ign_rb_path)

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # Remove MS runtime files
        for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
            rm(self, dll_pattern_to_remove, os.path.join(self.package_folder, "bin"), recursive=True)

    def package_info(self):
        self.cpp_info.includedirs = []

        version_major = Version(self.version).major
        pkg_name = f"ignition-tools{version_major}"
        self.cpp_info.set_property("cmake_file_name", pkg_name)
        self.cpp_info.set_property("cmake_target_name", f"{pkg_name}::{pkg_name}")

        component = self.cpp_info.components["libignition-tools"]
        component.includedirs = []
        component.libs = ["ignition-tools-backward"]
        component.requires = ["backward-cpp::backward-cpp"]
        component.set_property("cmake_target_name", pkg_name)
        component.set_property("pkg_config_name", pkg_name)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = pkg_name
        self.cpp_info.names["cmake_find_package_multi"] = pkg_name
        component.names["cmake_find_package"] = pkg_name
        component.names["cmake_find_package_multi"] = pkg_name

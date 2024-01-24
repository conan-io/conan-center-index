import os
import textwrap

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, save, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LibE57FormatConan(ConanFile):
    name = "libe57format"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/asmaloney/libE57Format"
    description = "Library for reading & writing the E57 file format"
    topics = ("e57", "io", "point-cloud")

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("xerces-c/3.2.5")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16.3 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()
        tc = CMakeToolchain(self)
        tc.variables["E57_BUILD_SHARED"] = self.options.shared
        tc.variables["E57_BUILD_TEST"] = False
        tc.variables["USING_STATIC_XERCES"] = not self.dependencies["xerces-c"].options.shared
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "POSITION_INDEPENDENT_CODE ON", "")
        if Version(self.version) >= "3.0":
            # Disable compiler warnings, which cause older versions of GCC to fail due to unrecognized flags
            replace_in_file(self, os.path.join(self.source_folder, "cmake", "CompilerWarnings.cmake"),
                            " -W", " # -W")
            # Disable warnings as errors
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "set_warning_as_error()", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"E57Format": "E57Format::E57Format"}
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
        self.cpp_info.set_property("cmake_file_name", "e57format")
        self.cpp_info.set_property("cmake_target_name", "E57Format")
        suffix = "-d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"E57Format{suffix}"]
        if self.settings.os in ["Linux", "FreeBSD"] and not self.options.shared:
            self.cpp_info.system_libs.extend(["m", "pthread"])

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "e57format"
        self.cpp_info.filenames["cmake_find_package_multi"] = "e57format"
        self.cpp_info.names["cmake_find_package"] = "E57Format"
        self.cpp_info.names["cmake_find_package_multi"] = "E57Format"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

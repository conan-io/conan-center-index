from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, save
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os
import textwrap

required_conan_version = ">=1.53.0"


class Argtable3Conan(ConanFile):
    name = "argtable3"
    description = "A single-file, ANSI C, command-line parsing library that parses GNU-style command-line options."
    license = "BSD-3-clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.argtable.org/"
    topics = ("command", "line", "argument", "parse", "parsing", "getopt")

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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ARGTABLE3_ENABLE_TESTS"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        # The initial space is important (the cmake script does OFFSET 0)
        save(self, os.path.join(self.build_folder, "version.tag"), f" {self.version}.0\n")
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

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

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # These targets were for versions < 3.2.1 (newer create argtable3::argtable3)
        target_name = "argtable3" if self.options.shared else "argtable3_static"
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {target_name: "argtable3::argtable3"}
        )

    def package_info(self):
        suffix = ""
        if not self.options.shared:
            suffix += "_static"
        if Version(self.version) >= "3.2.1" and self.settings.build_type == "Debug":
            suffix += "d"
        self.cpp_info.libs = [f"argtable3{suffix}"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("m")

        self.cpp_info.set_property("cmake_file_name", "Argtable3")
        self.cpp_info.set_property("cmake_target_name", "argtable3::argtable3")
        # These targets were for versions < 3.2.1 (newer create argtable3::argtable3)
        self.cpp_info.set_property("cmake_target_aliases", ["argtable3" if self.options.shared else "argtable3_static"])

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Argtable3"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Argtable3"
        self.cpp_info.names["cmake_find_package"] = "argtable3"
        self.cpp_info.names["cmake_find_package_multi"] = "argtable3"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

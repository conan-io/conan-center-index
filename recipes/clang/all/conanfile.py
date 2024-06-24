import json
import re
import textwrap
from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir, save, load
from conan.tools.microsoft import check_min_vs, is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"

class ClangConan(ConanFile):
    name = "clang"
    description = "The Clang project provides a language front-end and tooling infrastructure for languages in the C language family"
    license = "Apache-2 with LLVM-exception"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://clang.llvm.org/"
    topics = ("clang", "llvm", "compiler")
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
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }

    @property
    def _clang_source_folder(self):
        return Path(self.source_folder) / "clang"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"llvm-core/{self.version}", transitive_headers=True)

    def build_requirements(self):
        # needed to build c-index-test but not actually required by any components
        self.test_requires(f"libxml2/[>2.12.4 <3]")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        sources = self.conan_data["sources"][self.version]
        get(self, **sources["clang"], destination="clang", strip_root=True)
        get(self, **sources["cmake"], destination="cmake", strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LLVM_INCLUDE_TESTS"] = False
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        cmake_lists = self._clang_source_folder / "CMakeLists.txt"
        replace_in_file(self, cmake_lists,
                        """list(APPEND CMAKE_MODULE_PATH "${LLVM_DIR}")""",
                        """list(APPEND CMAKE_MODULE_PATH "${LLVM_DIR};${LLVM_CMAKE_DIR}")""",
                        strict=False
                        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder="clang")
        cmake.build()

    def _parse_clang_components(self):
        def _sanitized_dependencies(dependencies):
            for dep in dependencies:
                if dep.startswith("LLVM"):
                    yield f"llvm-core::{dep}"
                else:
                    yield dep

        targets = load(self, self.package_folder / self._cmake_build_folder_rel_path / "ClangTargets.cmake")

        match_libraries = re.compile(r'''^add_library\((\S+).*\)$''', re.MULTILINE)
        libraries = set(match_libraries.findall(targets))

        match_dependencies = re.compile(
            r'''^set_target_properties\((\S+).*\n?\s*INTERFACE_LINK_LIBRARIES\s+"(\S+)"''', re.MULTILINE)

        components = {}
        for component, dependencies in match_dependencies.findall(targets):
            if component in libraries:
                components.update({
                    component: {
                        "requires": list(_sanitized_dependencies(dependencies.split(";")))
                }
                })

        return components

    @property
    def _cmake_build_folder_rel_path(self):
        return Path("lib") / "cmake" / "clang"

    @property
    def _build_module_file_rel_path(self):
        return self._cmake_build_folder_rel_path / f"conan-official-{self.name}-variables.cmake"

    @property
    def _components_path(self):
        return Path(self.package_folder) / self._cmake_build_folder_rel_path / "components.json"

    def _create_cmake_build_module(self, module_file):
        package_folder = Path(self.package_folder)
        content = textwrap.dedent(f"""\
            set(CLANG_INSTALL_PREFIX "{str(package_folder)}")
            set(CLANG_CMAKE_DIR "{str(package_folder / self._cmake_build_folder_rel_path)}")
            if (NOT TARGET clang-tablegen-targets)
              add_custom_target(clang-tablegen-targets)
            endif()
            list(APPEND CMAKE_MODULE_PATH "${{LLVM_CMAKE_DIR}}")
            # should have been be included by AddClang but isn't
            include(AddLLVM)
           """)
        save(self, module_file, content)

    def _write_components(self):
        components = self._parse_clang_components()
        with open(self._components_path, "w", encoding="utf-8") as fp:
            json.dump(components, fp)

    def _read_components(self):
        with open(self._components_path, "r", encoding="utf-8") as fp:
            return json.load(fp)

    def package(self):
        copy(self, "LICENSE.TXT", self._clang_source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        package_folder = Path(self.package_folder)
        self._create_cmake_build_module(package_folder / self._build_module_file_rel_path)
        self._write_components()

        cmake_folder = package_folder / self._cmake_build_folder_rel_path
        rm(self, "ClangConfig*", cmake_folder)
        rm(self, "ClangTargets*", cmake_folder)
        rmdir(self, package_folder / "share")

    def package_info(self):
        def _add_no_rtti_flag(component):
            if is_msvc(self):
                component.cxxflags.append("/GS-")
            else:
                component.cxxflags.append("-fno-rtti")

        def _lib_name_from_component(name):
            replacements = {
                "libclang": "clang"
            }
            return replacements.get(name, name)

        self.cpp_info.set_property("cmake_file_name", "Clang")
        self.cpp_info.set_property("cmake_build_modules",
                                   [self._build_module_file_rel_path,
                                    self._cmake_build_folder_rel_path / "AddClang.cmake"]
                                   )

        self.cpp_info.builddirs.append(self._build_module_file_rel_path)
        llvm = self.dependencies["llvm-core"]
        if not llvm.options.rtti:
            _add_no_rtti_flag(self.cpp_info)

        components = self._read_components()
        for component, data in components.items():
            self.cpp_info.components[component].set_property("cmake_target_name", component)
            self.cpp_info.components[component].libs = [_lib_name_from_component(component)]
            self.cpp_info.components[component].requires = data["requires"]
            if not llvm.options.rtti:
                _add_no_rtti_flag(self.cpp_info.components[component])

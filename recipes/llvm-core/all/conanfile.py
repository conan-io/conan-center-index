import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualRunEnv
from conan.tools.files import apply_conandata_patches, collect_libs, get, rmdir, save, copy, export_conandata_patches, load
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

import json
import os
from pathlib import Path
import re

required_conan_version = ">=1.62.0"


class LLVMCoreConan(ConanFile):
    name = "llvm-core"
    description = (
        "A toolkit for the construction of highly optimized compilers,"
        "optimizers, and runtime environments."
    )
    license = "Apache-2.0 WITH LLVM-exception"
    topics = ("llvm", "compiler")
    homepage = "https://llvm.org"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "components": ["ANY"],
        "targets": ["ANY"],
        "exceptions": [True, False],
        "rtti": [True, False],
        "threads": [True, False],
        "lto": ["On", "Off", "Full", "Thin"],
        "static_stdlib": [True, False],
        "unwind_tables": [True, False],
        "expensive_checks": [True, False],
        "use_perf": [True, False],
        "use_sanitizer": [
            "Address",
            "Memory",
            "MemoryWithOrigins",
            "Undefined",
            "Thread",
            "DataFlow",
            "Address;Undefined",
            "None"
        ],
        "with_ffi": [True, False],
        "with_terminfo": [True, False],
        "with_zlib": [True, False],
        "with_xml2": [True, False],
        "with_z3": [True, False],
        "use_llvm_cmake_files": [True, False],
        "ram_per_compile_job": ["ANY"],
        "ram_per_link_job": ["ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "components": "all",
        "targets": "all",
        "exceptions": True,
        "rtti": True,
        "threads": True,
        "lto": "Off",
        "static_stdlib": False,
        "unwind_tables": True,
        "expensive_checks": False,
        "use_perf": False,
        "use_sanitizer": "None",
        "with_ffi": False,
        "with_terminfo": False, # differs from LLVM default
        "with_xml2": True,
        "with_z3": True,
        "with_zlib": True,
        "use_llvm_cmake_files": False, # no longer used but retained for backwards compatibility
        # creating job pools with current free memory
        "ram_per_compile_job": "2048",
        "ram_per_link_job": "16384"
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }

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
        if self.options.with_ffi:
            self.requires("libffi/3.4.4")
        if self.options.with_zlib:
            self.requires("zlib/1.3.1")
        if self.options.with_xml2:
            self.requires("libxml2/2.12.4")
        if self.options.with_z3:
            self.requires("z3/4.12.4")

    def build_requirements(self):
        self.tool_requires("ninja/1.11.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self._is_windows:
            if self.options.shared:  # Shared builds disabled just due to the CI
                raise ConanInvalidConfiguration("Shared builds not currently supported on Windows")

        if self.options.exceptions and not self.options.rtti:
            raise ConanInvalidConfiguration("Cannot enable exceptions without rtti support")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self, generator="Ninja")
        # https://releases.llvm.org/12.0.0/docs/CMake.html
        # https://releases.llvm.org/13.0.0/docs/CMake.html
        cmake_definitions = {
            "LLVM_TARGETS_TO_BUILD": self.options.targets,
            # See comment below on LLVM shared library builds
            "LLVM_BUILD_LLVM_DYLIB": self.options.shared,
            "LLVM_LINK_LLVM_DYLIB": self.options.shared,
            "LLVM_DYLIB_COMPONENTS": self.options.components,
            "LLVM_ABI_BREAKING_CHECKS": "WITH_ASSERTS",
            "LLVM_INCLUDE_TOOLS": True,
            "LLVM_INCLUDE_EXAMPLES": False,
            "LLVM_INCLUDE_TESTS": False,
            "LLVM_ENABLE_IDE": False,
            "LLVM_ENABLE_EH": self.options.exceptions,
            "LLVM_ENABLE_RTTI": self.options.rtti,
            "LLVM_ENABLE_THREADS": self.options.threads,
            "LLVM_ENABLE_LTO": self.options.lto,
            "LLVM_STATIC_LINK_CXX_STDLIB": self.options.static_stdlib,
            "LLVM_ENABLE_UNWIND_TABLES": self.options.unwind_tables,
            "LLVM_ENABLE_EXPENSIVE_CHECKS": self.options.expensive_checks,
            "LLVM_ENABLE_ASSERTIONS": self.settings.build_type,
            "LLVM_USE_PERF": self.options.use_perf,
            "LLVM_ENABLE_Z3_SOLVER": self.options.with_z3,
            "LLVM_ENABLE_FFI": self.options.with_ffi,
            "LLVM_ENABLE_ZLIB": "FORCE_ON" if self.options.with_zlib else False,
            "LLVM_ENABLE_LIBXML2": "FORCE_ON" if self.options.with_xml2 else False,
            "LLVM_ENABLE_TERMINFO": self.options.with_terminfo,
        }
        if self.options.ram_per_compile_job != "auto":
            cmake_definitions["LLVM_RAM_PER_COMPILE_JOB"] = self.options.ram_per_compile_job
        if self.options.ram_per_link_job != "auto":
            cmake_definitions["LLVM_RAM_PER_LINK_JOB"] = self.options.ram_per_link_job

        is_platform_ELF_based = self.settings.os in [
            "Linux", "Android", "FreeBSD", "SunOS", "AIX", "Neutrino", "VxWorks"
        ]
        if is_platform_ELF_based:
            self.output.info(f"ELF Platform Detected, optimizing memory usage during debug build linking.")
            cmake_definitions["LLVM_USE_SPLIT_DWARF"] = True

        if is_msvc(self):
            build_type = str(self.settings.build_type).upper()
            cmake_definitions["LLVM_USE_CRT_{}".format(build_type)] = self.settings.compiler.runtime

        if not self.options.shared:
            cmake_definitions.update({
                "DISABLE_LLVM_LINK_LLVM_DYLIB": True,
                "LLVM_ENABLE_PIC": self.options.get_safe("fPIC", default=False)
            })

        if self.options.use_sanitizer == "None":
            cmake_definitions["LLVM_USE_SANITIZER"] = ""
        else:
            cmake_definitions["LLVM_USE_SANITIZER"] = self.options.use_sanitizer

        tc.variables.update(cmake_definitions)
        tc.cache_variables.update({
            # Enables LLVM to find conan libraries during try_compile
            "CMAKE_TRY_COMPILE_CONFIGURATION": str(self.settings.build_type),
            # LLVM has two separate concepts of a "shared library build".
            # "BUILD_SHARED_LIBS" builds shared versions of all of the static components
            # "LLVM_BUILD_LLVM_DYLIB" builds a single shared library containing all components.
            # It is likely the latter that the user expects by a "shared library" build.
            "BUILD_SHARED_LIBS": False,
        })
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

        if can_run(self):
            # For running llvm-tblgen during the build
            VirtualRunEnv(self).generate(scope="build")

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _is_windows(self):
        return self.settings.os == "Windows"

    def _llvm_components(self):
        cmake_config = load(self, Path(self.package_folder) / "lib" / "cmake" / "llvm" / "LLVMConfig.cmake")

        match_cmake_var = re.compile(r"""^set\(LLVM_AVAILABLE_LIBS (?P<components>.*)\)$""", re.MULTILINE)
        match = match_cmake_var.search(cmake_config)
        if match is None:
            self.output.warning("Could not find components in LLVMConfig.cmake")
            return None

        components = match.groupdict()["components"]

        match_component = re.compile(r"""^LLVM(.+)$""")
        for component in components.split(";"):
            match = match_component.match(component)
            if match:
                yield match.group(1).lower(), component
            else:
                yield component.lower(), component

    @property
    def _components_data_file(self):
        return Path(self.package_folder) / "lib" / "components.json"

    @property
    def _build_module_file_rel_path(self):
        return Path("lib") / "cmake" / "llvm" / f"conan-official-{self.name}-variables.cmake"

    def _create_cmake_build_module(self, components, module_file):
        # FIXME: define other LLVM CMake Variables as per
        #  https://llvm.org/docs/CMake.html#embedding-llvm-in-your-project
        json_text = json.dumps(components).replace('"', '\\"')
        content = textwrap.dedent(f"""\
            set(LLVM_PACKAGE_VERSION "{self.version}")

            function(llvm_map_components_to_libnames OUTPUT)
                set(_libnames )
                set(_components_json "{json_text}")
                foreach(_component ${{ARGN}})
                    string(JSON _lib_name ERROR_VARIABLE ERR GET ${{_components_json}} ${{_component}})
                    if (ERR)
                        message(WARNING "Component ${{_component}} not found: ${{ERR}}")
                    endif()
                    list(APPEND _libnames ${{_lib_name}})
                endforeach()
                set(${{OUTPUT}} ${{_libnames}} PARENT_SCOPE)
            endfunction()
           """)
        save(self, module_file, content)

    def _write_components(self):
        component_dict = {
            component: lib_name for component, lib_name in self._llvm_components()
        }
        with open(self._components_data_file, "w", encoding="utf-8") as fp:
            json.dump(component_dict, fp)

        return component_dict

    def _read_components(self) -> dict:
        with open(self._components_data_file, encoding="utf-8") as fp:
            return json.load(fp)

    def package(self):
        copy(self, "LICENSE.TXT", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        components = {}
        if not self.options.shared:
            components = self._write_components()

        package_folder = Path(self.package_folder)
        rmdir(self, package_folder / "lib" / "cmake")
        rmdir(self, package_folder / "share")

        self._create_cmake_build_module(
            components,
            package_folder / self._build_module_file_rel_path
        )

    def package_id(self):
        del self.info.options.use_llvm_cmake_files
        del self.info.options.ram_per_compile_job
        del self.info.options.ram_per_link_job

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LLVM")
        self.cpp_info.set_property("cmake_build_modules", [self._build_module_file_rel_path])
        self.cpp_info.builddirs.append(os.path.dirname(self._build_module_file_rel_path))

        dependencies = []
        if self.options.with_zlib:
            dependencies.append("zlib::zlib")
        if self.options.with_xml2:
            dependencies.append("libxml2::libxml2")
        if self.options.with_ffi:
            dependencies.append("libffi::libffi")
        if self.options.with_z3:
            dependencies.append("z3::z3")

        if not self.options.shared:
            components = self._read_components()

            for component_name, lib_name in components.items():
                self.cpp_info.components[component_name].set_property("cmake_target_name", lib_name)
                self.cpp_info.components[component_name].libs = [lib_name]
                self.cpp_info.components[component_name].requires = dependencies

                if component_name in ["lto", "remarks"] and self.settings.os in ["Linux", "FreeBSD"]:
                    self.cpp_info.components[component_name].system_libs.append("rt")
        else:
            self.cpp_info.set_property("cmake_target_name", "LLVM")
            self.cpp_info.libs = collect_libs(self)

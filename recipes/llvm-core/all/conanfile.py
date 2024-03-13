import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, can_run, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualRunEnv
from conan.tools.files import (
    apply_conandata_patches,
    collect_libs,
    get,
    rmdir,
    save,
    copy,
    export_conandata_patches,
    load,
    rm, rename
)
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
        "ram_per_compile_job": "auto",
        "ram_per_link_job": "auto"
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

        if cross_building(self):
            # FIXME support cross compilation, at least for common cases like Apple Silicon -> X86
            raise ConanInvalidConfiguration("Cross compilation is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _apply_resource_limits(self, cmake_definitions):
        if os.getenv("CONAN_CENTER_BUILD_SERVICE"):
            self.output.info("Applying CCI Resource Limits")
            if self.options.shared and self.settings.build_type == "Debug":
                ram_per_link_job = "32768"
            else:
                ram_per_link_job = "16384"
            cmake_definitions.update({
                "LLVM_RAM_PER_LINK_JOB": ram_per_link_job,
                "LLVM_RAM_PER_COMPILE_JOB": "2048"
            })
        else:
            if self.options.ram_per_compile_job != "auto":
                cmake_definitions["LLVM_RAM_PER_COMPILE_JOB"] = self.options.ram_per_compile_job
            if self.options.ram_per_link_job != "auto":
                cmake_definitions["LLVM_RAM_PER_LINK_JOB"] = self.options.ram_per_link_job

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
            "LLVM_ENABLE_ZSTD": "FORCE_ON" if self.options.get_safe("with_zstd") else False
        }

        self._apply_resource_limits(cmake_definitions)

        # this capability is back-ported from LLVM 14.x
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
            "BUILD_SHARED_LIBS": False
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

    def _lib_name_to_component(self, lib_name):
        match_component_name = re.compile(r"""^LLVM(.+)$""")
        match = match_component_name.match(lib_name)
        if match:
            return match.group(1).lower()
        else:
            return lib_name.lower()

    def _llvm_components(self):
        cmake_config = load(self, Path(self.package_folder) / "lib" / "cmake" / "llvm" / "LLVMConfig.cmake")

        match_cmake_var = re.compile(r"""^set\(LLVM_AVAILABLE_LIBS (?P<components>.*)\)$""", re.MULTILINE)
        match = match_cmake_var.search(cmake_config)
        if match is None:
            self.output.warning("Could not find components in LLVMConfig.cmake")
            return None

        components = match.groupdict()["components"]
        for lib_name in components.split(";"):
            yield self._lib_name_to_component(lib_name), lib_name

    def _component_dependencies(self):
        """
        Returns a dictionary indexed by the LLVM component name containing
        the cmake target name (library name),
        the component dependencies and system libs. Parsed from the CMake files
        generated by the LLVM project
        """
        def _sanitized_components(deps_list):
            match_genex = re.compile(r"""\\\$<LINK_ONLY:LLVM(.+)>""")
            for dep in deps_list.split(";"):
                match = match_genex.search(dep)
                if match:
                    yield match.group(1).lower()
                elif dep.startswith("-l"):
                    yield dep[2:]
                else:
                    yield self._lib_name_to_component(dep)

        def _parse_deps(deps_list):
            ignore = ["libedit::libedit", "edit"]
            data = {
                "requires": [],
                "system_libs": []
            }
            for component in _sanitized_components(deps_list):
                if component in ignore:
                    continue
                if component in ["rt", "m", "dl", "pthread"]:
                    data["system_libs"].append(component)
                else:
                    data["requires"].append(component)
            return data

        cmake_exports = load(self, Path(self.package_folder) / "lib" / "cmake" / "llvm" / "LLVMExports.cmake")
        match_dependencies = re.compile(
            r'''^set_target_properties\(LLVM(\w+).*\n{0,1}\s*INTERFACE_LINK_LIBRARIES\s+"(\S+)"''', re.MULTILINE)

        components = { component: { "lib_name": lib_name } for component, lib_name in self._llvm_components() }
        for llvm_lib, deps_list in match_dependencies.findall(cmake_exports):
            component = llvm_lib.lower()
            if component in components:
                components[component].update(_parse_deps(deps_list))

        return components

    @property
    def _components_data_file(self):
        return Path(self.package_folder) / "lib" / "components.json"

    @property
    def _cmake_module_path(self):
        return Path("lib") / "cmake" / "llvm"

    @property
    def _build_module_file_rel_path(self):
        return self._cmake_module_path / f"conan-official-{self.name}-variables.cmake"

    def _create_cmake_build_module(self, components, module_file):
        package_folder = Path(self.package_folder)
        content = textwrap.dedent(f"""\
            set(LLVM_PACKAGE_VERSION "{self.version}")
            set(LLVM_AVAILABLE_LIBS "{';'.join(component['lib_name'] for component in components.values())}")
            set(LLVM_BUILD_TYPE "{self.settings.build_type}")
            set(LLVM_CMAKE_DIR "{str(package_folder / "lib" / "cmake" / "llvm")}")
            set(LLVM_TOOLS_BINARY_DIR "{str(package_folder / "bin")}")
            set_property(GLOBAL PROPERTY LLVM_TARGETS_CONFIGURED On)
           """)
        save(self, module_file, content)

    def _write_components(self):
        components = self._component_dependencies()
        with open(self._components_data_file, "w", encoding="utf-8") as fp:
            json.dump(components, fp, indent=2)

        return components

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
        cmake_folder = package_folder / "lib" / "cmake" / "llvm"
        rm(self, "LLVMConfig*", cmake_folder)
        rm(self, "LLVMExports*", cmake_folder)
        rm(self, "Find*", cmake_folder)
        # need to rename this as Conan will flag it, but it's not actually a Config file and is needed by
        # downstream packages
        rename(self, cmake_folder / "LLVM-Config.cmake", cmake_folder / "LLVM-ConfigInternal.cmake")
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
        self.cpp_info.set_property("cmake_build_modules",
            [self._build_module_file_rel_path,
             self._cmake_module_path / "LLVM-ConfigInternal.cmake"]
        )
        self.cpp_info.builddirs.append(self._cmake_module_path)

        if not self.options.shared:
            components = self._read_components()

            for component_name, data in components.items():
                self.cpp_info.components[component_name].set_property("cmake_target_name", data["lib_name"])
                self.cpp_info.components[component_name].libs = [data["lib_name"]]
                requires = data.get("requires")
                if requires is not None:
                    self.cpp_info.components[component_name].requires += requires
                system_libs = data.get("system_libs")
                if system_libs is not None:
                    self.cpp_info.components[component_name].system_libs += system_libs

        else:
            self.cpp_info.set_property("cmake_target_name", "LLVM")
            self.cpp_info.libs = collect_libs(self)

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
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
    rm,
    rename,
    replace_in_file
)
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

import json
import os
from pathlib import Path
import re
import textwrap


required_conan_version = ">=1.62.0"

# LLVM's default config is enable all targets, but end users can significantly reduce
# build times for the package by disabling the ones they don't need with the corresponding option
# `-o llvm-core/*:with_target_<target name in lower case>=False`
LLVM_TARGETS = [
    "AArch64",
    "AMDGPU",
    "ARM",
    "AVR",
    "BPF",
    "Hexagon",
    "Lanai",
    "LoongArch",
    "Mips",
    "MSP430",
    "NVPTX",
    "PowerPC",
    "RISCV",
    "Sparc",
    "SystemZ",
    "VE",
    "WebAssembly",
    "X86",
    "XCore"
]


class LLVMCoreConan(ConanFile):
    name = "llvm-core"
    description = (
        "A toolkit for the construction of highly optimized compilers,"
        "optimizers, and runtime environments."
    )
    license = "LLVM-exception"
    topics = ("llvm", "compiler")
    homepage = "https://llvm.org"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "components": ["ANY"],
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
        "with_libedit": [True, False],
        "with_terminfo": [True, False],
        "with_zlib": [True, False],
        "with_xml2": [True, False],
        "with_z3": [True, False],
        "ram_per_compile_job": ["ANY"],
        "ram_per_link_job": ["ANY"],
    }
    options.update({f"with_target_{target.lower()}": [True, False] for target in LLVM_TARGETS})
    default_options = {
        "shared": False,
        "fPIC": True,
        "components": "all",
        "exceptions": True,
        "rtti": True,
        "threads": True,
        "lto": "Off",
        "static_stdlib": False,
        "unwind_tables": True,
        "expensive_checks": False,
        "use_perf": False,
        "use_sanitizer": "None",
        "with_libedit": True,
        "with_ffi": False,
        "with_terminfo": False,  # differs from LLVM default
        "with_xml2": True,
        "with_z3": True,
        "with_zlib": True,
        "ram_per_compile_job": "auto",
        "ram_per_link_job": "auto"
    }
    default_options.update({f"with_target_{target.lower()}": True for target in LLVM_TARGETS})

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

    @property
    def _major_version(self):
        return Version(self.version).major

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_libedit # not supported on windows
        if self._major_version < 14:
            del self.options.with_target_loongarch  # experimental
            del self.options.with_target_ve  # experimental

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_ffi:
            self.requires("libffi/3.4.4")
        if self.options.get_safe("with_libedit"):
            self.requires("editline/3.1")
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

        if self.options.shared:
            if self._is_windows:
                raise ConanInvalidConfiguration("Shared builds not currently supported on Windows")
            if os.getenv("CONAN_CENTER_BUILD_SERVICE") and self.settings.build_type == "Debug":
                raise ConanInvalidConfiguration("Shared Debug build is not supported on CCI due to resource limitations")
            if is_apple_os(self):
                # FIXME iconv contains duplicate symbols in the libiconv and libcharset libraries (both of which are
                #  provided by libiconv). This may be an issue with how conan packages libiconv
                iconv_dep = self.dependencies.get("libiconv")
                if iconv_dep and not iconv_dep.options.shared:
                    raise ConanInvalidConfiguration("Static iconv cannot be linked into a shared library on macos "
                                                    "due to duplicate symbols. Use libxml2/*:iconv=False.")

        if self.options.exceptions and not self.options.rtti:
            raise ConanInvalidConfiguration("Cannot enable exceptions without rtti support")

        if cross_building(self):
            # FIXME support cross compilation, at least for common cases like Apple Silicon -> X86
            #  requires a host-compiled version of llvm-tablegen
            raise ConanInvalidConfiguration("Cross compilation is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _apply_resource_limits(self, cmake_definitions):
        if os.getenv("CONAN_CENTER_BUILD_SERVICE"):
            self.output.info("Applying CCI Resource Limits")
            cmake_definitions.update({
                "LLVM_RAM_PER_LINK_JOB": "16384",
                "LLVM_RAM_PER_COMPILE_JOB": "2048"
            })
        else:
            if self.options.ram_per_compile_job != "auto":
                cmake_definitions["LLVM_RAM_PER_COMPILE_JOB"] = self.options.ram_per_compile_job
            if self.options.ram_per_link_job != "auto":
                cmake_definitions["LLVM_RAM_PER_LINK_JOB"] = self.options.ram_per_link_job

    @property
    def _targets_to_build(self):
        return ";".join(target for target in LLVM_TARGETS if self.options.get_safe(f"with_target_{target.lower()}"))

    @property
    def _all_targets(self):
        # This is not just LLVM_TARGETS as it is version specific
        return ";".join(
            target for target in LLVM_TARGETS if self.options.get_safe(f"with_target_{target.lower()}") is not None)

    @property
    def _msvcrt(self):
        msvcrt = str(self.settings.compiler.runtime)
        # handle conan legacy setting
        if msvcrt in ["MDd", "MTd", "MD", "MT"]:
            return msvcrt

        if self.settings.build_type in ["Debug", "RelWithDebInfo"]:
            crt = {"static": "MTd", "dynamic": "MDd"}
        else:
            crt = {"static": "MT", "dynamic": "MD"}

        return crt[msvcrt]

    def generate(self):
        tc = CMakeToolchain(self, generator="Ninja")
        # https://releases.llvm.org/12.0.0/docs/CMake.html
        # https://releases.llvm.org/13.0.0/docs/CMake.html
        cmake_definitions = {
            "LLVM_TARGETS_TO_BUILD": self._targets_to_build,
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
            "LLVM_ENABLE_LIBEDIT": self.options.get_safe("with_libedit", False),
            "LLVM_ENABLE_Z3_SOLVER": self.options.with_z3,
            "LLVM_ENABLE_FFI": self.options.with_ffi,
            "LLVM_ENABLE_ZLIB": "FORCE_ON" if self.options.with_zlib else False,
            "LLVM_ENABLE_LIBXML2": "FORCE_ON" if self.options.with_xml2 else False,
            "LLVM_ENABLE_TERMINFO": self.options.with_terminfo
        }

        self._apply_resource_limits(cmake_definitions)

        # this capability is back-ported from LLVM 14.x
        is_platform_ELF_based = self.settings.os in [
            "Linux", "Android", "FreeBSD", "SunOS", "AIX", "Neutrino", "VxWorks"
        ]
        if is_platform_ELF_based:
            self.output.info("ELF Platform Detected, optimizing memory usage during debug build linking.")
            cmake_definitions["LLVM_USE_SPLIT_DWARF"] = True

        if is_msvc(self):
            build_type = str(self.settings.build_type).upper()
            cmake_definitions[f"LLVM_USE_CRT_{build_type}"] = self._msvcrt

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
            # "BUILD_SHARED_LIBS" builds shared versions of all the static components
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

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _is_windows(self):
        return self.settings.os == "Windows"

    @staticmethod
    def load(filename):
        # regex fails on Windows when using conan's built in 'load' method
        with open(filename, "r", encoding="utf-8")as fp:
            return fp.read()

    def _update_component_dependencies(self, components):
        def _sanitized_components(deps_list):
            match_genex = re.compile(r"""\\\$<LINK_ONLY:(.+)>""")
            replacements = {
                "LibXml2::LibXml2": "libxml2::libxml2",
                "ZLIB::ZLIB": "zlib::zlib"
            }
            for dep in deps_list.split(";"):
                match = match_genex.search(dep)
                if match:
                    yield match.group(1)
                else:
                    replacement = replacements.get(dep)
                    if replacement:
                        yield replacement
                    elif dep.startswith("-l"):
                        yield dep[2:]
                    else:
                        yield dep

        def _parse_deps(deps_list):
            data = {
                "requires": [],
                "system_libs": []
            }
            windows_system_libs=[
                "ole32",
                "delayimp",
                "shell32",
                "advapi32",
                "-delayload:shell32.dll",
                "uuid",
                "psapi",
                "-delayload:ole32.dll"
            ]
            for component in _sanitized_components(deps_list):
                if component in windows_system_libs:
                    continue
                if component in ["rt", "m", "dl", "pthread"]:
                    data["system_libs"].append(component)
                else:
                    data["requires"].append(component)
            return data

        cmake_exports = self.load(Path(self.package_folder) / "lib" / "cmake" / "llvm" / "LLVMExports.cmake")
        match_dependencies = re.compile(
            r'''^set_target_properties\((\w+).*\n?\s*INTERFACE_LINK_LIBRARIES\s+"(\S+)"''', re.MULTILINE)

        for llvm_lib, dependencies in match_dependencies.findall(cmake_exports):
            if llvm_lib in components:
                components[llvm_lib].update(_parse_deps(dependencies))

    def _llvm_build_info(self):
        cmake_config = self.load(Path(self.package_folder) / "lib" / "cmake" / "llvm" / "LLVMConfig.cmake")

        match_cmake_var = re.compile(r"""^set\(LLVM_AVAILABLE_LIBS (?P<components>.*)\)$""", re.MULTILINE)
        match = match_cmake_var.search(cmake_config)
        if match is None:
            self.output.warning("Could not find components in LLVMConfig.cmake")
            return None

        components = { component: {} for component in match.groupdict()["components"].split(";") }
        self._update_component_dependencies(components)

        return {
            "components": components,
            "native_arch": re.search(r"""^set\(LLVM_NATIVE_ARCH (\S*)\)$""", cmake_config, re.MULTILINE).group(1)
        }

    @property
    def _cmake_module_path(self):
        return Path("lib") / "cmake" / "llvm"

    @property
    def _build_info_file(self):
        return Path(self.package_folder) / self._cmake_module_path / "conan_llvm_build_info.json"

    @property
    def _build_module_file_rel_path(self):
        return self._cmake_module_path / f"conan-official-{self.name}-variables.cmake"

    def _create_cmake_build_module(self, build_info, module_file):
        targets_with_jit = ["X86", "PowerPC", "AArch64", "ARM", "Mips", "SystemZ"]
        content = textwrap.dedent(f"""\
            set(LLVM_TOOLS_BINARY_DIR "${{CMAKE_CURRENT_LIST_DIR}}/../../../bin")
            cmake_path(NORMAL_PATH LLVM_TOOLS_BINARY_DIR)
            set(LLVM_PACKAGE_VERSION "{self.version}")
            set(LLVM_AVAILABLE_LIBS "{';'.join(build_info['components'].keys())}")
            set(LLVM_BUILD_TYPE "{self.settings.build_type}")
            set(LLVM_CMAKE_DIR "${{CMAKE_CURRENT_LIST_DIR}}")
            set(LLVM_ALL_TARGETS "{self._all_targets}")
            set(LLVM_TARGETS_TO_BUILD "{self._targets_to_build}")
            set(LLVM_TARGETS_WITH_JIT "{';'.join(targets_with_jit)}")
            set(LLVM_NATIVE_ARCH "{build_info['native_arch']}")
            set_property(GLOBAL PROPERTY LLVM_TARGETS_CONFIGURED On)
            set_property(GLOBAL PROPERTY LLVM_COMPONENT_LIBS ${{LLVM_AVAILABLE_LIBS}})
            if (NOT TARGET intrinsics_gen)
              add_custom_target(intrinsics_gen)
            endif()
            if (NOT TARGET omp_gen)
              add_custom_target(omp_gen)
            endif()
            if (NOT TARGET acc_gen)
              add_custom_target(acc_gen)
            endif()
           """)
        save(self, module_file, content)

    def _write_build_info(self):
        build_info = self._llvm_build_info()
        with open(self._build_info_file, "w", encoding="utf-8") as fp:
            json.dump(build_info, fp, indent=2)

        return build_info

    def _read_build_info(self) -> dict:
        with open(self._build_info_file, encoding="utf-8") as fp:
            return json.load(fp)

    def package(self):
        copy(self, "LICENSE.TXT", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        build_info = self._write_build_info()

        package_folder = Path(self.package_folder)
        cmake_folder = package_folder / "lib" / "cmake" / "llvm"
        rm(self, "LLVMConfig.cmake", cmake_folder)
        rm(self, "LLVMExports*", cmake_folder)
        rm(self, "Find*", cmake_folder)
        rm(self, "*.pdb", package_folder / "lib")
        rm(self, "*.pdb", package_folder / "bin")
        # need to rename this as Conan will flag it, but it's not actually a Config file and is needed by
        # downstream packages
        rename(self, cmake_folder / "LLVM-Config.cmake", cmake_folder / "LLVM-ConfigInternal.cmake")
        replace_in_file(self, cmake_folder / "AddLLVM.cmake", "LLVM-Config", "LLVM-ConfigInternal")
        rmdir(self, package_folder / "share")
        if self.options.shared:
            rm(self, "*.a", package_folder / "lib")

        self._create_cmake_build_module(
            build_info,
            package_folder / self._build_module_file_rel_path
        )

    def package_id(self):
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
            build_info = self._read_build_info()
            components = build_info["components"]

            for component_name, data in components.items():
                self.cpp_info.components[component_name].set_property("cmake_target_name", component_name)
                self.cpp_info.components[component_name].libs = [component_name]
                requires = data.get("requires")
                if requires is not None:
                    self.cpp_info.components[component_name].requires += requires
                system_libs = data.get("system_libs")
                if system_libs is not None:
                    self.cpp_info.components[component_name].system_libs += system_libs
        else:
            self.cpp_info.set_property("cmake_target_name", "LLVM")
            self.cpp_info.libs = collect_libs(self)

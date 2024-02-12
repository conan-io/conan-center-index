from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import sys
import textwrap

required_conan_version = ">=1.60.0 <2.0 || >=2.0.5"


class OnnxConan(ConanFile):
    name = "onnx"
    description = "Open standard for machine learning interoperability."
    license = "Apache-2.0"
    topics = ("machine-learning", "deep-learning", "neural-network")
    homepage = "https://github.com/onnx/onnx"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_static_registration": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_static_registration": False,
    }

    @property
    def _is_legacy_one_profile(self):
        return not hasattr(self, "settings_build")

    @property
    def _min_cppstd(self):
        if Version(self.version) >= "1.15.0":
            return 17
        if Version(self.version) >= "1.13.0" and is_msvc(self):
            return 17
        return 11

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
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
        if is_msvc(self):
            del self.options.shared
            self.package_type = "static-library"
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("protobuf/3.21.12", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if self._min_cppstd > 11:
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def build_requirements(self):
        if not self._is_legacy_one_profile:
            self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if self._is_legacy_one_profile:
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = CMakeToolchain(self)
        # https://cmake.org/cmake/help/v3.28/module/FindPythonInterp.html
        # https://github.com/onnx/onnx/blob/1014f41f17ecc778d63e760a994579d96ba471ff/CMakeLists.txt#L119C1-L119C50
        tc.variables["PYTHON_EXECUTABLE"] = sys.executable.replace("\\", "/")
        tc.variables["ONNX_BUILD_BENCHMARKS"] = False
        tc.variables["ONNX_USE_PROTOBUF_SHARED_LIBS"] = self.dependencies.host["protobuf"].options.shared
        tc.variables["BUILD_ONNX_PYTHON"] = False
        tc.variables["ONNX_GEN_PB_TYPE_STUBS"] = False
        tc.variables["ONNX_WERROR"] = False
        tc.variables["ONNX_COVERAGE"] = False
        tc.variables["ONNX_BUILD_TESTS"] = False
        tc.variables["ONNX_USE_LITE_PROTO"] = self.dependencies.host["protobuf"].options.lite
        tc.variables["ONNX_ML"] = True
        if Version(self.version) < "1.13.0":
            tc.variables["ONNXIFI_ENABLE_EXT"] = False
            tc.variables["ONNXIFI_DUMMY_BACKEND"] = False
        tc.variables["ONNX_VERIFY_PROTO3"] = Version(self.dependencies.host["protobuf"].ref.version).major == "3"
        if is_msvc(self):
            tc.variables["ONNX_USE_MSVC_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.variables["ONNX_DISABLE_STATIC_REGISTRATION"] = self.options.get_safe('disable_static_registration')
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        fix_apple_shared_install_name(self)

        # TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {component["target"]:f"ONNX::{component['target']}" for component in self._onnx_components.values()}
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

    @property
    def _onnx_components(self):
        components = {
            "libonnx": {
                "target": "onnx",
                "libs": ["onnx"],
                "defines": ["ONNX_NAMESPACE=onnx", "ONNX_ML=1"],
                "requires": ["onnx_proto"]
            },
            "onnx_proto": {
                "target": "onnx_proto",
                "libs": ["onnx_proto"],
                "defines": ["ONNX_NAMESPACE=onnx", "ONNX_ML=1"],
                "requires": ["protobuf::libprotobuf"]
            }
        }
        if Version(self.version) < "1.13.0":
            components.update(
                {
                    "onnxifi": {
                        "target": "onnxifi",
                        "system_libs": [(self.settings.os in ["Linux", "FreeBSD"], ["dl"])],
                    },
                    "onnxifi_dummy": {
                        "target": "onnxifi_dummy",
                        "libs": ["onnxifi_dummy"],
                        "requires": ["onnxifi"]
                    },
                    "onnxifi_loader": {
                        "target": "onnxifi_loader",
                        "libs": ["onnxifi_loader"],
                        "requires": ["onnxifi"]
                    },
                    "onnxifi_wrapper": {
                        "target": "onnxifi_wrapper"
                    }
                }
            )
        components["libonnx"]["defines"].append("__STDC_FORMAT_MACROS")
        return components

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ONNX")

        def _register_components(components):
            for comp_name, comp_values in components.items():
                target = comp_values["target"]
                libs = comp_values.get("libs", [])
                defines = comp_values.get("defines", [])
                requires = comp_values.get("requires", [])
                system_libs = [l for cond, sys_libs in comp_values.get("system_libs", []) if cond for l in sys_libs]
                self.cpp_info.components[comp_name].set_property("cmake_target_name", target)
                self.cpp_info.components[comp_name].libs = libs
                self.cpp_info.components[comp_name].defines = defines
                self.cpp_info.components[comp_name].requires = requires
                self.cpp_info.components[comp_name].system_libs = system_libs

                # TODO: to remove in conan v2 once cmake_find_package_* generators removed
                self.cpp_info.components[comp_name].names["cmake_find_package"] = target
                self.cpp_info.components[comp_name].names["cmake_find_package_multi"] = target
                self.cpp_info.components[comp_name].build_modules["cmake_find_package"] = [self._module_file_rel_path]
                self.cpp_info.components[comp_name].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        _register_components(self._onnx_components)

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "ONNX"
        self.cpp_info.names["cmake_find_package_multi"] = "ONNX"

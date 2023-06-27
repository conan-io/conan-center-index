from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"


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
    def _min_cppstd(self):
        if Version(self.version) >= "1.13.0" and is_msvc(self):
            return 17
        return 11

    @property
    def _protobuf_version(self):
        # onnx < 1.9.0 doesn't support protobuf >= 3.18
        return "3.21.9" if Version(self.version) >= "1.9.0" else "3.17.1"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.version < "1.9.0":
            del self.options.disable_static_registration

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"protobuf/{self._protobuf_version}", run=not cross_building(self), transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration("onnx shared is broken with Visual Studio")

    def build_requirements(self):
        if hasattr(self, "settings_build") and cross_building(self):
            self.tool_requires(f"protobuf/{self._protobuf_version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = CMakeToolchain(self)
        tc.variables["ONNX_BUILD_BENCHMARKS"] = False
        tc.variables["ONNX_USE_PROTOBUF_SHARED_LIBS"] = self.dependencies.host["protobuf"].options.shared
        tc.variables["BUILD_ONNX_PYTHON"] = False
        tc.variables["ONNX_GEN_PB_TYPE_STUBS"] = False
        tc.variables["ONNX_WERROR"] = False
        tc.variables["ONNX_COVERAGE"] = False
        tc.variables["ONNX_BUILD_TESTS"] = False
        tc.variables["ONNX_USE_LITE_PROTO"] = False
        tc.variables["ONNX_ML"] = True
        if Version(self.version) < "1.13.0":
            tc.variables["ONNXIFI_ENABLE_EXT"] = False
            tc.variables["ONNXIFI_DUMMY_BACKEND"] = False
        tc.variables["ONNX_VERIFY_PROTO3"] = Version(self.dependencies.host["protobuf"].ref.version).major == "3"
        if is_msvc(self):
            tc.variables["ONNX_USE_MSVC_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        if self.version >= "1.9.0":
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
        if Version(self.version) >= "1.11.0":
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

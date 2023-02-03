from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, get, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.50.2 <1.51.0 || >=1.51.2"


class OnnxConan(ConanFile):
    name = "onnx"
    description = "Open standard for machine learning interoperability."
    license = "Apache-2.0"
    topics = ("machine-learning", "deep-learning", "neural-network")
    homepage = "https://github.com/onnx/onnx"
    url = "https://github.com/conan-io/conan-center-index"

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
    def _protobuf_version(self):
        # onnx < 1.9.0 doesn't support protobuf >= 3.18
        return "3.21.4" if Version(self.version) >= "1.9.0" else "3.17.1"

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires(f"protobuf/{self._protobuf_version}")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration("onnx shared is broken with Visual Studio")

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.tool_requires(f"protobuf/{self._protobuf_version}")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ONNX_BUILD_BENCHMARKS"] = False
        tc.variables["ONNX_USE_PROTOBUF_SHARED_LIBS"] = self.options["protobuf"].shared
        tc.variables["BUILD_ONNX_PYTHON"] = False
        tc.variables["ONNX_GEN_PB_TYPE_STUBS"] = False
        tc.variables["ONNX_WERROR"] = False
        tc.variables["ONNX_COVERAGE"] = False
        tc.variables["ONNX_BUILD_TESTS"] = False
        tc.variables["ONNX_USE_LITE_PROTO"] = False
        tc.variables["ONNXIFI_ENABLE_EXT"] = False
        tc.variables["ONNX_ML"] = True
        tc.variables["ONNXIFI_DUMMY_BACKEND"] = False
        tc.variables["ONNX_VERIFY_PROTO3"] = Version(self.dependencies.host["protobuf"].ref.version).major == "3"
        if is_msvc(self):
            tc.variables["ONNX_USE_MSVC_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        env = VirtualBuildEnv(self)
        env.generate()

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
            },
            "onnxifi": {
                "target": "onnxifi"
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
                self.cpp_info.components[comp_name].set_property("cmake_target_name", target)
                self.cpp_info.components[comp_name].libs = libs
                self.cpp_info.components[comp_name].defines = defines
                self.cpp_info.components[comp_name].requires = requires

                # TODO: to remove in conan v2 once cmake_find_package_* generators removed
                self.cpp_info.components[comp_name].names["cmake_find_package"] = target
                self.cpp_info.components[comp_name].names["cmake_find_package_multi"] = target
                self.cpp_info.components[comp_name].build_modules["cmake_find_package"] = [self._module_file_rel_path]
                self.cpp_info.components[comp_name].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        _register_components(self._onnx_components)

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "ONNX"
        self.cpp_info.names["cmake_find_package_multi"] = "ONNX"

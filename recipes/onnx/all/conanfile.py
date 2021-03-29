from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class OnnxConan(ConanFile):
    name = "onnx"
    description = "Open standard for machine learning interoperability."
    license = "Apache-2.0"
    topics = ("conan", "onnx", "machine-learning", "deep-learning", "neural-network")
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

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("onnx shared is broken with Visual Studio")

    def requirements(self):
        self.requires("protobuf/3.15.5")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # No warnings as errors for Visual Studio also
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "/WX", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ONNX_BUILD_BENCHMARKS"] = False
        self._cmake.definitions["ONNX_USE_PROTOBUF_SHARED_LIBS"] = self.options["protobuf"].shared
        self._cmake.definitions["BUILD_ONNX_PYTHON"] = False
        self._cmake.definitions["ONNX_GEN_PB_TYPE_STUBS"] = False
        self._cmake.definitions["ONNX_WERROR"] = False
        self._cmake.definitions["ONNX_COVERAGE"] = False
        self._cmake.definitions["ONNX_BUILD_TESTS"] = False
        self._cmake.definitions["ONNX_USE_LITE_PROTO"] = False
        self._cmake.definitions["ONNXIFI_ENABLE_EXT"] = False
        self._cmake.definitions["ONNX_ML"] = True
        self._cmake.definitions["ONNXIFI_DUMMY_BACKEND"] = False
        self._cmake.definitions["ONNX_VERIFY_PROTO3"] = tools.Version(self.deps_cpp_info["protobuf"].version).major == "3"
        if self.settings.compiler.get_safe("runtime"):
            self._cmake.definitions["ONNX_USE_MSVC_STATIC_RUNTIME"] = str(self.settings.compiler.runtime) in ["MT", "MTd", "static"]
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {component["target"]:"ONNX::{}".format(component["target"]) for component in self._onnx_components.values()}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    @property
    def _onnx_components(self):
        return {
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

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "ONNX"
        self.cpp_info.names["cmake_find_package_multi"] = "ONNX"

        def _register_components(components):
            for comp_name, comp_values in components.items():
                target = comp_values["target"]
                libs = comp_values.get("libs", [])
                defines = comp_values.get("defines", [])
                requires = comp_values.get("requires", [])
                self.cpp_info.components[comp_name].names["cmake_find_package"] = target
                self.cpp_info.components[comp_name].names["cmake_find_package_multi"] = target
                self.cpp_info.components[comp_name].builddirs.append(self._module_subfolder)
                self.cpp_info.components[comp_name].build_modules["cmake_find_package"] = [self._module_file_rel_path]
                self.cpp_info.components[comp_name].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
                self.cpp_info.components[comp_name].libs = libs
                self.cpp_info.components[comp_name].defines = defines
                self.cpp_info.components[comp_name].requires = requires

        _register_components(self._onnx_components)

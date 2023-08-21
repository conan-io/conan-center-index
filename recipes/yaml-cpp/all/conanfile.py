from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os
import textwrap

required_conan_version = ">=1.53.0"


class YamlCppConan(ConanFile):
    name = "yaml-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jbeder/yaml-cpp"
    topics = ("yaml", "yaml-parser", "serialization", "data-serialization")
    description = "A YAML parser and emitter in C++"
    license = "MIT"
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(
                f"Visual Studio build for {self.name} shared library with MT runtime is not supported"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["YAML_CPP_BUILD_TESTS"] = False
        tc.variables["YAML_CPP_BUILD_CONTRIB"] = True
        tc.variables["YAML_CPP_BUILD_TOOLS"] = False
        tc.variables["YAML_CPP_INSTALL"] = True
        tc.variables["YAML_BUILD_SHARED_LIBS"] = self.options.shared
        if is_msvc(self):
            tc.variables["YAML_MSVC_SHARED_RT"] = not is_msvc_static_runtime(self)
            tc.preprocessor_definitions["_NOEXCEPT"] = "noexcept"
        tc.generate()

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
        rmdir(self, os.path.join(self.package_folder, "CMake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"yaml-cpp": "yaml-cpp::yaml-cpp"}
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
        self.cpp_info.set_property("cmake_file_name", "yaml-cpp")
        self.cpp_info.set_property("cmake_target_name", "yaml-cpp")
        self.cpp_info.set_property("pkg_config_name", "yaml-cpp")
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.append("m")
        if is_msvc(self):
            self.cpp_info.defines.append("_NOEXCEPT=noexcept")
            if self.options.shared:
                self.cpp_info.defines.append("YAML_CPP_DLL")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

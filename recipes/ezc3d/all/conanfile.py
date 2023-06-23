from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"


class Ezc3dConan(ConanFile):
    name = "ezc3d"
    description = "EZC3D is an easy to use reader, modifier and writer for C3D format files."
    license = "MIT"
    topics = ("ezc3d", "c3d")
    homepage = "https://github.com/pyomeca/ezc3d"
    url = "https://github.com/conan-io/conan-center-index"

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
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_MATRIX_FAST_ACCESSOR"] = True
        tc.variables["BINDER_PYTHON3"] = False
        tc.variables["BINDER_MATLAB"] = False
        if Version(self.version) >= "1.4.3":
            tc.variables["BINDER_OCTAVE"] = False
        tc.variables["BUILD_EXAMPLE"] = False
        tc.variables["BUILD_DOC"] = False
        tc.variables["GET_OFFICIAL_DOCUMENTATION"] = False
        tc.variables["BUILD_TESTS"] = False
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
        rmdir(self, os.path.join(self.package_folder, "CMake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # TODO: to remove once cmake_find_package* removed in conan v2
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"ezc3d": "ezc3d::ezc3d"}
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
        self.cpp_info.set_property("cmake_file_name", "ezc3d")
        self.cpp_info.set_property("cmake_target_name", "ezc3d")

        self.cpp_info.includedirs.append(os.path.join("include", "ezc3d"))
        lib_suffix = {"Debug": "_debug"}.get(str(self.settings.build_type), "")
        self.cpp_info.libs = [f"ezc3d{lib_suffix}"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]

        # TODO: to remove once cmake_find_package* removed in conan v2
        self.cpp_info.names["cmake_find_package"] = "ezc3d"
        self.cpp_info.names["cmake_find_package_multi"] = "ezc3d"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

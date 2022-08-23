from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, save
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.50.0"


class XsimdConan(ConanFile):
    name = "xsimd"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xtensor-stack/xsimd"
    description = "C++ wrappers for SIMD intrinsics and parallelized, optimized mathematical functions (SSE, AVX, NEON, AVX512)"
    topics = ("simd-intrinsics", "vectorization", "simd")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "xtl_complex": [True, False],
    }
    default_options = {
        "xtl_complex": False,
    }

    no_copy_source = True

    def requirements(self):
        if self.options.xtl_complex:
            self.requires("xtl/0.7.4")

    def package_id(self):
        self.info.clear()

    def validate(self):
        # TODO: check supported version (probably >= 8.0.0)
        if Version(self.version) < "8.0.0" and self.settings.os == "Macos" and self.settings.arch in ["armv8", "armv8_32", "armv8.3"]:
            raise ConanInvalidConfiguration(f"{self.name} doesn't support macOS M1")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        includedir = os.path.join(self.source_folder, "include")
        copy(self, "*.hpp", src=includedir, dst=os.path.join(self.package_folder, "include"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"xsimd": "xsimd::xsimd"}
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
        self.cpp_info.set_property("cmake_file_name", "xsimd")
        self.cpp_info.set_property("cmake_target_name", "xsimd")
        self.cpp_info.set_property("pkg_config_name", "xsimd")
        if self.options.xtl_complex:
            self.cpp_info.defines = ["XSIMD_ENABLE_XTL_COMPLEX=1"]
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

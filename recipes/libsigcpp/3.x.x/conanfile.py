from conan import ConanFile
from conan.tools import build, files
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration

import glob
import os
import shutil
import textwrap

required_conan_version = ">=1.53.0"


class LibSigCppConan(ConanFile):
    name = "libsigcpp"
    homepage = "https://github.com/libsigcplusplus/libsigcplusplus"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-3.0"
    description = "libsigc++ implements a typesafe callback system for standard C++."
    topics = ("libsigcpp", "callback")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    short_paths = True

    def export_sources(self):
        files.export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15.7",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
           build.check_min_cppstd(self, 17)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("libsigcpp requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("libsigcpp requires C++17, which your compiler does not support.")

    def layout(self):
        return basic_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        files.apply_conandata_patches(self)
        if not self.options.shared:
            files.replace_in_file(self, os.path.join(self.source_folder, "sigc++config.h.cmake"),
                                  "define SIGC_DLL 1", "undef SIGC_DLL")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self.source_folder)
        cmake = self._configure_cmake()
        cmake.install()
        for header_file in glob.glob(os.path.join(self.package_folder, "lib", "sigc++-3.0", "include", "*.h")):
            shutil.move(
                header_file,
                os.path.join(self.package_folder, "include", "sigc++-3.0", os.path.basename(header_file))
            )
        for dir_to_remove in ["cmake", "pkgconfig", "sigc++-3.0"]:
            files.rmdir(self, os.path.join(self.package_folder, "lib", dir_to_remove))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"sigc-3.0": "sigc++-3::sigc-3.0"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        files.save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sigc++-3")
        self.cpp_info.set_property("cmake_target_name", "sigc-3.0")
        self.cpp_info.set_property("pkg_config_name", "sigc++-3.0")

        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["sigc++"].includedirs = [os.path.join("include", "sigc++-3.0")]
        self.cpp_info.components["sigc++"].libs = files.collect_libs(self)
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["sigc++"].system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "sigc++-3"
        self.cpp_info.names["cmake_find_package_multi"] = "sigc++-3"
        self.cpp_info.components["sigc++"].names["cmake_find_package"] = "sigc-3.0"
        self.cpp_info.components["sigc++"].names["cmake_find_package_multi"] = "sigc-3.0"
        self.cpp_info.components["sigc++"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["sigc++"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["sigc++"].set_property("pkg_config_name", "sigc++-3.0")

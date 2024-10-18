from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, rename, replace_in_file, rmdir, save
import glob
import os
import textwrap

required_conan_version = ">=1.53.0"


class LibSigCppConan(ConanFile):
    name = "libsigcpp"
    homepage = "https://github.com/libsigcplusplus/libsigcplusplus"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-3.0-only"
    description = "libsigc++ implements a typesafe callback system for standard C++."
    topics = ("callback")

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
    def _min_cppstd(self):
        return "17"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15.7",
            "msvc": "191",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

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
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            return all(int(p1) < int(p2) for p1, p2 in zip(str(v1).split("."), str(v2).split(".")))

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Avoid 'short_paths=True required' warning due to an unused folder
        rmdir(self, os.path.join(self.source_folder, "untracked"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def _patch_sources(self):
        if not self.options.shared:
            replace_in_file(self, os.path.join(self.source_folder, "sigc++config.h.cmake"),
                                  "define SIGC_DLL 1", "undef SIGC_DLL")
        # Disable subdirs
        save(self, os.path.join(self.source_folder, "examples", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "tests", "CMakeLists.txt"), "")
        # Enable static builds
        cmakelists = os.path.join(self.source_folder, "sigc++", "CMakeLists.txt")
        replace_in_file(self, cmakelists, " SHARED ", " ")
        # Fix install paths
        replace_in_file(self, cmakelists,
                        'LIBRARY DESTINATION "lib"',
                        "LIBRARY DESTINATION lib ARCHIVE DESTINATION lib RUNTIME DESTINATION bin")


    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        for header_file in glob.glob(os.path.join(self.package_folder, "lib", "sigc++-3.0", "include", "*.h")):
            dst = os.path.join(self.package_folder, "include", "sigc++-3.0", os.path.basename(header_file))
            rename(self, header_file, dst)
        for dir_to_remove in ["cmake", "pkgconfig", "sigc++-3.0"]:
            rmdir(self, os.path.join(self.package_folder, "lib", dir_to_remove))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"sigc-3.0": "sigc++-3::sigc-3.0"}
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
        self.cpp_info.set_property("cmake_file_name", "sigc++-3")
        self.cpp_info.set_property("cmake_target_name", "sigc-3.0")
        self.cpp_info.set_property("pkg_config_name", "sigc++-3.0")

        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["sigc++"].includedirs = [os.path.join("include", "sigc++-3.0")]
        self.cpp_info.components["sigc++"].libs = collect_libs(self)
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

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import (
    export_conandata_patches,
    get,
    copy,
    apply_conandata_patches,
)
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os
import textwrap


required_conan_version = ">=1.53.0"


class MBitsLngsConan(ConanFile):
    name = "mbits-lngs"
    description = "Language strings support"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mbits-os/lngs"
    topics = "gettext"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "clang": "12",
            "Visual Studio": "16",
            "msvc": "192",
            "apple-clang": "11.0.3",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fmt/9.1.0")
        self.requires("mbits-utfconv/1.0.3")
        self.requires("mbits-diags/0.9.5")
        self.requires("mbits-mstch/1.0.4")
        self.requires("mbits-args/0.12.3")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(
                str(self.settings.compiler), False
            )
            if (
                minimum_version
                and Version(self.settings.compiler.version) < minimum_version
            ):
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LNGS_TESTING"] = False
        tc.variables["LNGS_LITE"] = False
        tc.variables["LNGS_LINKED_RESOURCES"] = True
        tc.variables["LNGS_NO_PKG_CONFIG"] = True
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _cmake_install_base_path(self):
        return os.path.join("lib", "cmake")

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()

        os.unlink(
            os.path.join(
                self.package_folder, self._cmake_install_base_path, "mbits-lngs.cmake"
            )
        )
        os.unlink(
            os.path.join(
                self.package_folder,
                self._cmake_install_base_path,
                "mbits-lngs-{}.cmake".format(str(self.settings.build_type).lower()),
            )
        )
        with open(
            os.path.join(
                self.package_folder,
                self._cmake_install_base_path,
                "module-mbits-lngs.cmake",
            ),
            "w",
            encoding="UTF-8",
        ) as cfg:
            exe_ext = ".exe" if self.settings.os == "Windows" else ""
            lngs_filename = "lngs" + exe_ext
            module_folder_depth = len(
                os.path.normpath(self._cmake_install_base_path).split(os.path.sep)
            )
            lngs_rel_path = "{}bin/{}".format(
                "".join(["../"] * module_folder_depth), lngs_filename
            )
            cfg.write(
                textwrap.dedent(
                    """\
                if(NOT TARGET mbits::lngs)
                    if(CMAKE_CROSSCOMPILING)
                        find_program(LNGS_PROGRAM lngs PATHS ENV PATH NO_DEFAULT_PATH)
                    endif()
                    if(NOT LNGS_PROGRAM)
                        set(LNGS_REL_PATH "{lngs_rel_path}")
                        set(LNGS_PROGRAM "${{CMAKE_CURRENT_LIST_DIR}}/${{LNGS_REL_PATH}}")
                    endif()
                    get_filename_component(LNGS_PROGRAM "${{LNGS_PROGRAM}}" ABSOLUTE)
                    set(Mbitslngs_LNGS_EXECUTABLE ${{LNGS_PROGRAM}} CACHE FILEPATH "The lngs tool")
                    add_executable(mbits::lngs IMPORTED)
                    set_property(TARGET mbits::lngs PROPERTY IMPORTED_LOCATION ${{Mbitslngs_LNGS_EXECUTABLE}})
                endif()
            """.format(
                        lngs_rel_path=lngs_rel_path
                    )
                )
            )

    def package_info(self):
        self.cpp_info.set_property(
            "cmake_build_modules",
            [
                os.path.join(self._cmake_install_base_path, "module-mbits-lngs.cmake"),
            ],
        )

        self.cpp_info.libs = ["lngs"]

        self.cpp_info.set_property("cmake_file_name", "mbits-lngs")
        self.cpp_info.set_property("cmake_target_name", "mbits::liblngs")

        self.cpp_info.filenames["cmake_find_package"] = "mbits-lngs"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mbits-lngs"
        self.cpp_info.names["cmake_find_package"] = "mbits"
        self.cpp_info.names["cmake_find_package_multi"] = "mbits"
        self.cpp_info.components["liblngs"].set_property(
            "cmake_target_name", "mbits::liblngs"
        )
        self.cpp_info.components["liblngs"].libs = ["lngs"]

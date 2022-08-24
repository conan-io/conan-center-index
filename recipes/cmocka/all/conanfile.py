from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir, save
import os
import textwrap

required_conan_version = ">=1.47.0"


class CmockaConan(ConanFile):
    name = "cmocka"
    license = "Apache-2.0"
    homepage = "https://cmocka.org"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A unit testing framework for C"
    topics = ("unit_test", "unittest", "test", "testing", "mock", "mocking")

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
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_STATIC_LIB"] = not self.options.shared
        tc.variables["WITH_EXAMPLES"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent("""\
            if(NOT DEFINED CMOCKA_INCLUDE_DIR)
                set(CMOCKA_INCLUDE_DIR ${cmocka_INCLUDE_DIRS}
                                       ${cmocka_INCLUDE_DIRS_RELEASE}
                                       ${cmocka_INCLUDE_DIRS_RELWITHDEBINFO}
                                       ${cmocka_INCLUDE_DIRS_MINSIZEREL}
                                       ${cmocka_INCLUDE_DIRS_DEBUG})
            endif()
            if(TARGET cmocka::cmocka)
                if(NOT DEFINED CMOCKA_LIBRARY)
                    set(CMOCKA_LIBRARY cmocka::cmocka)
                endif()
                if(NOT DEFINED CMOCKA_LIBRARIES)
                    set(CMOCKA_LIBRARIES cmocka::cmocka)
                endif()
            endif()
        """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cmocka")
        self.cpp_info.set_property("pkg_config_name", "cmocka")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.libs = ["cmocka{}".format("" if self.options.shared else "-static")]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.microsoft import is_msvc
import os
import textwrap

required_conan_version = ">=1.53.0"


class LitehtmlConan(ConanFile):
    name = "litehtml"
    description = "litehtml is the lightweight HTML rendering engine with CSS2/CSS3 support."
    license = "BSD-3-Clause"
    topics = ("render engine", "html", "parser")
    homepage = "https://github.com/litehtml/litehtml"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "utf8": [True, False],
        "with_icu": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "utf8": False,
        "with_icu": False,
    }

    @property
    def _with_xxd(self):
        # FIXME: create conan recipe for xxd, and use it unconditionally (returning False means cross build doesn't work)
        return self.settings.os != "Windows"

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

    def requirements(self):
        # FIXME: add gumbo requirement (it is vendored right now)
        if self.options.with_icu:
            self.requires("icu/72.1")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.info.options.shared and is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} shared not supported with Visual Studio")

    def build_requirements(self):
        # FIXME: add unconditional xxd build requirement
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["LITEHTML_UTF8"] = self.options.utf8
        tc.variables["USE_ICU"] = self.options.with_icu
        tc.variables["EXTERNAL_GUMBO"] = False # FIXME: add cci recipe, and use it unconditionally (option value should be True)
        tc.variables["EXTERNAL_XXD"] = self._with_xxd  # FIXME: should be True unconditionally
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

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "litehtml": "litehtml::litehtml",
                "gumbo": "litehtml::gumbo",
            }
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
        self.cpp_info.set_property("cmake_file_name", "litehtml")
        self.cpp_info.set_property("cmake_target_name", "litehtml")

        self.cpp_info.components["litehtml_litehtml"].set_property("cmake_target_name", "litehtml")
        self.cpp_info.components["litehtml_litehtml"].libs = ["litehtml"]
        self.cpp_info.components["litehtml_litehtml"].requires = ["gumbo"]
        if self.options.with_icu:
            self.cpp_info.components["litehtml_litehtml"].requires.append("icu::icu")

        if True: # FIXME: remove once we use a vendored gumbo library
            self.cpp_info.components["gumbo"].set_property("cmake_target_name", "gumbo")
            self.cpp_info.components["gumbo"].libs = ["gumbo"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["litehtml_litehtml"].names["cmake_find_package"] = "litehtml"
        self.cpp_info.components["litehtml_litehtml"].names["cmake_find_package_multi"] = "litehtml"
        self.cpp_info.components["litehtml_litehtml"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["litehtml_litehtml"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if True:
            self.cpp_info.components["gumbo"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["gumbo"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools import files
from conan import ConanFile
import os
import textwrap

required_conan_version = ">=1.45.0"


class Tixi3Conan(ConanFile):
    name = "tixi3"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A simple xml interface based on libxml2 and libxslt"
    topics = ("tixi3", "xml")
    homepage = "https://github.com/DLR-SC/tixi"
    license = "Apache-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def requirements(self):
        self.requires("libxml2/2.9.14")
        self.requires("libxslt/1.1.34")
        self.requires("libcurl/7.84.0")

    def layout(self):
        cmake_layout(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

        # tixi is a c library
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"], src=self.recipe_folder, dst=self.export_sources_folder)

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self.source_folder)

    def build(self):
        files.apply_conandata_patches(self)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        files.save(self, module_file, content)

    def package(self):
        cmake = CMake(self)
        cmake.install()

        files.rmdir(self, os.path.join(self.package_folder, "lib", "tixi3"))
        files.copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        files.rmdir(self, os.path.join(self.package_folder, "share"))

        # provide alias target tixi3 for v1 packages
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"tixi3": "tixi3::tixi3"}
        )

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "tixi3"))

        if self.settings.build_type != "Debug":
            self.cpp_info.libs = ['tixi3']
        else:
            self.cpp_info.libs = ['tixi3-d']

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ['Shlwapi']

        self.cpp_info.set_property("cmake_file_name", "tixi3")
        self.cpp_info.set_property("cmake_target_name", "tixi3")

        # provide alias target tixi3 for v1 packages
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

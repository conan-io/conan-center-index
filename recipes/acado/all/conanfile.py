import os

from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class AcadoConan(ConanFile):
    name = "acado"
    description = ("ACADO Toolkit is a software environment and algorithm "
                   "collection for automatic control and dynamic optimization.")
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/acado/acado"
    topics = ("control", "optimization", "mpc")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "codegen_only": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "codegen_only": True,
    }
    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "cmake/qpoases.cmake", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Note: ACADO also separately vendors and exports qpOASES v1.3 for code generation.
        self.requires("qpoases/3.2.1")

    def validate(self):
        if is_msvc(self) and self.options.shared:
            # https://github.com/acado/acado/blob/b4e28f3131f79cadfd1a001e9fff061f361d3a0f/CMakeLists.txt#L77-L80
            raise ConanInvalidConfiguration("Acado does not support shared builds on Windows.")
        if self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration("apple-clang not supported")
        if self.settings.compiler == "clang" and self.settings.compiler.version == "9":
            raise ConanInvalidConfiguration("acado can not be built by Clang 9.")
        if conan_version.major < 2 and self.settings.compiler in ["clang", "gcc"] and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration("libstdc++11 required")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ACADO_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["ACADO_BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["ACADO_BUILD_CGT_ONLY"] = self.options.codegen_only
        tc.cache_variables["ACADO_WITH_EXAMPLES"] = False
        tc.cache_variables["ACADO_WITH_TESTING"] = False
        tc.cache_variables["ACADO_DEVELOPER"] = False
        tc.cache_variables["ACADO_INTERNAL"] = False
        # The build logs 170,000 lines of warnings otherwise
        tc.variables["CMAKE_C_FLAGS"] = "-w"
        tc.variables["CMAKE_CXX_FLAGS"] = "-w"
        tc.variables["CMAKE_CXX_STANDARD"] = 11
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # TODO: Use Eigen from Conan. Failed with static assert errors even if using matching eigen/3.2.0 version for some reason.
        # rmdir(self, os.path.join(self.source_folder, "external_packages", "eigen3"))
        # replace_in_file(self, os.path.join(self.source_folder, "acado/matrix_vector/matrix_vector_tools.hpp"),
        #                 "external_packages/eigen3/", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _qpoases_sources(self):
        return os.path.join(self.package_folder, "lib", "cmake", "qpoases")

    def package(self):
        copy(self, "LICENSE.txt",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()

        if not self.options.shared:
            # Copy internal static acado_casadi lib
            copy(self, "*acado_casadi*",
                 src=os.path.join(self.build_folder, "lib"),
                 dst=os.path.join(self.package_folder, "lib"),
                 keep_path=False)

        # Copy embedded qpOASES v1.3 sources for code generation
        copy(self, "qpoases.cmake",
             src=os.path.join(self.export_sources_folder, "cmake"),
             dst=os.path.join(self.package_folder, "lib", "cmake"))
        copy(self, "*",
             src=os.path.join(self.package_folder, "share", "acado", "external_packages", "qpoases"),
             dst=self._qpoases_sources)

        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        rm(self, "*.exp", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ACADO")
        self.cpp_info.set_property("cmake_target_name", "ACADO::ACADO")

        if self.options.shared:
            self.cpp_info.libs = ["acado_toolkit_s"]
        else:
            self.cpp_info.libs = ["acado_toolkit", "acado_casadi"]

        self.cpp_info.includedirs.append(os.path.join("include", "acado"))

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "qpoases.cmake")])
        self.cpp_info.includedirs += [
            self._qpoases_sources,
            os.path.join(self._qpoases_sources, "INCLUDE"),
            os.path.join(self._qpoases_sources, "SRC"),
        ]

        acado_template_paths = os.path.join(self.package_folder, "include", "acado", "code_generation", "templates")
        self.conf_info.define("user.acado:template_paths", acado_template_paths)
        self.buildenv_info.define_path("ACADO_TEMPLATE_PATHS", acado_template_paths)

        # TODO: to remove in conan v2
        self.env_info.ACADO_TEMPLATE_PATHS = acado_template_paths
        self.cpp_info.names["cmake_find_package"] = "ACADO"
        self.cpp_info.names["cmake_find_package_multi"] = "ACADO"
        self.cpp_info.build_modules["cmake_find_package"].append(os.path.join("lib", "cmake", "qpoases.cmake"))
        self.cpp_info.build_modules["cmake_find_package_multi"].append(os.path.join("lib", "cmake", "qpoases.cmake"))

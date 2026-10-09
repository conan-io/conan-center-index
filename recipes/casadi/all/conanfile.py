import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir

required_conan_version = ">=2.1"


class CasadiConan(ConanFile):
    name = "casadi"
    description = (
        "CasADi is a symbolic framework for numeric optimization implementing "
        "automatic differentiation in forward and reverse modes on sparse "
        "matrix-valued computational graphs."
    )
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://web.casadi.org"
    topics = ("optimization", "automatic-differentiation", "optimal-control", "nlp", "symbolic")
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
    implements = ["auto_shared_fpic"]

    _first_party_plugins = (
        "conic_nlpsol", "conic_qrqp", "conic_ipqp",
        "nlpsol_qrsqp", "nlpsol_sqpmethod", "nlpsol_feasiblesqpmethod", "nlpsol_scpgen",
        "importer_shell",
        "integrator_rk", "integrator_collocation",
        "interpolant_linear", "interpolant_bspline",
        "linsol_symbolicqr", "linsol_qr", "linsol_ldl", "linsol_tridiag", "linsol_lsqr",
        "rootfinder_newton", "rootfinder_fast_newton", "rootfinder_nlpsol", "rootfinder_bisection",
    )

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fmi2/2.0.4")
        self.requires("fmi3/3.0.2")

    def validate(self):
        check_min_cppstd(self, 11)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16.3 <5]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ENABLE_SHARED"] = self.options.shared
        tc.cache_variables["ENABLE_STATIC"] = not self.options.shared
        tc.cache_variables["WITH_SELFCONTAINED"] = True
        if self.settings.os == "Android":
            # Bionic has no RTLD_DEEPBIND
            tc.cache_variables["WITH_DEEPBIND"] = False
        tc.cache_variables["WITH_EXAMPLES"] = False
        for pkg in ("SUNDIALS", "CSPARSE", "TINYXML"):
            tc.cache_variables[f"WITH_{pkg}"] = False
        tc.cache_variables["FMI2_INCLUDE_DIR"] = self.dependencies["fmi2"].cpp_info.includedir
        tc.cache_variables["FMI3_INCLUDE_DIR"] = self.dependencies["fmi3"].cpp_info.includedir
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        licenses = os.path.join(self.package_folder, "licenses")
        copy(self, "LICENSE.txt", self.source_folder, licenses)
        cmake = CMake(self)
        cmake.install()
        # WITH_SELFCONTAINED installs the CMake config files to casadi/cmake
        rmdir(self, os.path.join(self.package_folder, "casadi"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # WITH_SELFCONTAINED dumps every vendored license here, including unbuilt packages
        rmdir(self, os.path.join(self.package_folder, "include", "licenses"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "casadi")
        self.cpp_info.set_property("cmake_target_name", "casadi::casadi")
        self.cpp_info.set_property("pkg_config_name", "casadi")

        core = self.cpp_info.components["core"]
        core.libs = ["casadi"]
        core.defines = ["CASADI_SNPRINTF=snprintf"]
        core.requires = ["fmi2::fmi2", "fmi3::fmi3"]
        if self.settings.os in ("Linux", "FreeBSD"):
            core.system_libs = ["dl"]

        if not self.options.shared:
            # Static plugins can't be dlopen'ed, consumers register them explicitly
            # via casadi_load_<type>_<name>()
            for plugin in self._first_party_plugins:
                component = self.cpp_info.components[plugin]
                component.libs = [f"casadi_{plugin}"]
                component.requires = ["core"]

import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir

required_conan_version = ">=2.1"


class CasadiConan(ConanFile):
    name = "casadi"
    description = (
        "CasADi is a symbolic framework for numeric optimization implementing "
        "automatic differentiation in forward and reverse modes on sparse "
        "matrix-valued computational graphs."
    )
    license = "LGPL-3.0-only AND BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://web.casadi.org"
    topics = ("optimization", "automatic-differentiation", "optimal-control", "nlp", "symbolic")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # Import of FMI 2.0/3.0 binaries (uses the FMI standard headers vendored in the sources)
        "with_fmi": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_fmi": True,
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        v = tc.cache_variables
        v["ENABLE_SHARED"] = self.options.shared
        v["ENABLE_STATIC"] = not self.options.shared
        # $ORIGIN rpath so the plugin .so files next to libcasadi are found in a relocated cache
        v["WITH_SELFCONTAINED"] = True
        # Typed cache entries: an untyped -D relative path would be made absolute against the
        # build dir once CasADi declares it CACHE PATH, instead of against CMAKE_INSTALL_PREFIX
        tc.variables["LIB_PREFIX"] = "lib"
        tc.variables["BIN_PREFIX"] = "bin"
        tc.variables["INCLUDE_PREFIX"] = "include"
        tc.variables["CMAKE_PREFIX"] = "lib/cmake/casadi"
        v["WITH_DEEPBIND"] = self.settings.os != "Android"
        v["WITH_FMI2"] = self.options.with_fmi
        v["WITH_FMI3"] = self.options.with_fmi
        v["WITH_EXAMPLES"] = False
        v["WITH_PYTHON"] = False
        v["WITH_MATLAB"] = False
        v["WITH_OCTAVE"] = False
        # No network access at build time and no third-party solver interfaces (yet)
        v["WITH_BUILD_REQUIRED"] = False
        v["WITH_MOCKUP_REQUIRED"] = False
        for pkg in ("SUNDIALS", "CSPARSE", "TINYXML", "QPOASES", "BLOCKSQP", "SUPERSCS", "IPOPT", "LAPACK"):
            v[f"WITH_{pkg}"] = False
        for pkg in ("SUNDIALS", "CSPARSE", "TINYXML"):
            v[f"WITH_BUILD_{pkg}"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        licenses = os.path.join(self.package_folder, "licenses")
        copy(self, "LICENSE.txt", self.source_folder, licenses)
        if self.options.with_fmi:
            for fmi in ("FMI-Standard-2.0.2", "FMI-Standard-3.0"):
                copy(self, "LICENSE.txt", os.path.join(self.source_folder, "external_packages", fmi),
                     os.path.join(licenses, fmi))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # WITH_SELFCONTAINED dumps every vendored license here, including unbuilt packages
        rmdir(self, os.path.join(self.package_folder, "include", "licenses"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "casadi")
        self.cpp_info.set_property("cmake_target_name", "casadi::casadi")
        self.cpp_info.set_property("pkg_config_name", "casadi")
        # Exported upstream as an INTERFACE definition of casadi::casadi
        self.cpp_info.defines = ["CASADI_SNPRINTF=snprintf"]
        if self.options.shared:
            self.cpp_info.libs = ["casadi"]
        else:
            # Static plugins must precede the core they depend on; consumers register them
            # explicitly via casadi_load_<type>_<name>() since nothing can be dlopen'ed
            self.cpp_info.libs = [f"casadi_{p}" for p in self._first_party_plugins] + ["casadi"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["dl", "m", "pthread"]
        # Plugins (casadi_<type>_<name> shared libs) are dlopen'ed by name; tell CasADi where they live
        if self.options.shared:
            plugin_dir = os.path.join(self.package_folder, "bin" if self.settings.os == "Windows" else "lib")
            self.runenv_info.define_path("CASADIPATH", plugin_dir)
            self.buildenv_info.define_path("CASADIPATH", plugin_dir)

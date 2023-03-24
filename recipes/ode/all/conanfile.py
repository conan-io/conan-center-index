from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
import os

required_conan_version = ">=1.54.0"


class OdeConan(ConanFile):
    name = "ode"
    description = "ODE is an open source, high performance library for simulating rigid body dynamics."
    license = ("LGPL-2.1-or-later", "BSD-3-Clause")
    topics = ("open-dynamics-engine", "physics", "physics-engine", "physics-simulation", "dynamics", "rigid-body")
    homepage = "https://www.ode.org"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "precision": ["single", "double"],
        "with_libccd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "precision": "double",
        "with_libccd": False,
    }

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
        if self.options.with_libccd:
            self.requires("libccd/2.1")

    def validate(self):
        if self.options.with_libccd:
            ccd_double_precision = self.dependencies["libccd"].options.enable_double_precision
            if self.options.precision == "single" and ccd_double_precision:
                raise ConanInvalidConfiguration("ode:precision=single requires libccd:enable_double_precision=False")
            elif self.options.precision == "double" and not ccd_double_precision:
                raise ConanInvalidConfiguration("ode:precision=double requires libccd:enable_double_precision=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ODE_16BIT_INDICES"] = False
        tc.variables["ODE_NO_BUILTIN_THREADING_IMPL"] = False
        tc.variables["ODE_NO_THREADING_INTF"] = False
        tc.variables["ODE_OLD_TRIMESH"] = False
        tc.variables["ODE_WITH_DEMOS"] = False
        tc.variables["ODE_WITH_GIMPACT"] = False
        tc.variables["ODE_WITH_LIBCCD"] = self.options.with_libccd
        tc.variables["ODE_WITH_OPCODE"] = True
        tc.variables["ODE_WITH_OU"] = False
        tc.variables["ODE_WITH_TESTS"] = False
        if self.options.with_libccd:
            tc.variables["ODE_WITH_LIBCCD_SYSTEM"] = True
        tc.variables["ODE_DOUBLE_PRECISION"] = self.options.precision == "double"
        # Relocatable shared libs on macOS
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # Avoid a warning
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0075"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        for license_file in ("COPYING", "LICENSE*"):
            copy(self, license_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ode")
        self.cpp_info.set_property("cmake_target_name", "ODE::ODE")
        self.cpp_info.set_property("pkg_config_name", "ode")
        lib_name = "ode"
        if self.settings.os == "Windows":
            lib_name += "_double" if self.options.precision == "double" else "_single"
            lib_name += "" if self.options.shared else "s"
            lib_name += "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [lib_name]
        self.cpp_info.defines.append("dIDEDOUBLE" if self.options.precision == "double" else "dIDESINGLE")
        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.extend(["m", "pthread"])
            elif self.settings.os == "Macos":
                self.cpp_info.frameworks.append("CoreServices")
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.filenames["cmake_find_package"] = "ode"
        self.cpp_info.filenames["cmake_find_package_multi"] = "ode"
        self.cpp_info.names["cmake_find_package"] = "ODE"
        self.cpp_info.names["cmake_find_package_multi"] = "ODE"

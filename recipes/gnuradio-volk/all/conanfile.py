import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, Environment
from conan.tools.files import copy, get, rm, save, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class GnuradioVolkConan(ConanFile):
    name = "gnuradio-volk"
    description = "VOLK is the Vector-Optimized Library of Kernels."
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libvolk.org/"
    topics = ("simd", "kernel", "sdr", "dsp", "gnuradio")

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

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # To avoid ConanInvalidConfiguration on Windows
        self.options["cpython"].shared = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpu_features/0.9.0")
        # TODO: add recipe for gstreamer-orc https://github.com/GStreamer/orc

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cpython/3.10.0")
        # To avoid a conflict with CMake installed via pip on the system Python
        self.tool_requires("cmake/[>=3.15 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _site_packages_dir(self):
        return os.path.join(self.build_folder, "site-packages")

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        tc = CMakeToolchain(self)
        tc.variables["ENABLE_STATIC_LIBS"] = not self.options.shared
        tc.variables["ENABLE_TESTING"] = False
        tc.variables["ENABLE_MODTOOL"] = False  # Requires Python
        tc.variables["ENABLE_ORC"] = False  # Not available on CCI
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0148"] = "OLD" # FindPythonInterp support
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW" # tc.requires support
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        env = Environment()
        env.append_path("PYTHONPATH", self._site_packages_dir)
        env.append_path("PATH", os.path.join(self._site_packages_dir, "bin"))
        env.vars(self).save_script("pythonpath")

    def _patch_sources(self):
        # Disable apps
        save(self, os.path.join(self.source_folder, "apps", "CMakeLists.txt"), "")

    def _pip_install(self, packages):
        self.run(f"python -m pip install {' '.join(packages)} --no-cache-dir --target={self._site_packages_dir}")

    def build(self):
        self._patch_sources()
        self._pip_install(["mako"])
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if not self.options.shared:
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dylib*", os.path.join(self.package_folder, "lib"))
            rm(self, "volk.dll.lib", os.path.join(self.package_folder, "lib"))
            rm(self, "volk.dll", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Volk")
        self.cpp_info.set_property("cmake_target_name", "Volk::volk")
        self.cpp_info.set_property("pkg_config_name", "volk")
        self.cpp_info.libs = ["volk"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])

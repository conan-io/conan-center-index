from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=1.53.0"


class OmplConan(ConanFile):
    name = "ompl"
    description = "The Open Motion Planning Library (OMPL)"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ompl.kavrakilab.org/"
    topics = ("motion-planning", "robotics", "path-planning")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    # Add options for optional dependencies
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_flann": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_flann": True,  # Enabled by default, can be disabled by user
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)

        # Configure Boost: Disable Python and other unused components to prevent build errors
        self.requires(
            "boost/1.83.0",
            transitive_headers=True,
            options={
                # Explicitly disabled components (Not needed by OMPL)
                "without_python": True,
                "without_mpi": True,
                "without_test": True,
                "without_contract": True,
                "without_stacktrace": True,
                "without_fiber": True,
                "without_log": True,
                "without_wave": True,
                "without_nowide": True,
                "without_json": True,
                "without_url": True,
                "without_locale": True,
                "without_context": True,
                "without_coroutine": True,
                "without_timer": True,
                "without_type_erasure": True,
                # NOTE: We KEEP these implicitly enabled by NOT listing them above:
                # - filesystem
                # - graph
                # - math
                # - program_options
                # - serialization
                # - system
                # - iostreams (often a transitive dependency for serialization/fs)
                # - chrono (required by thread)
                # - container (required by thread)
                # - thread (needed by system/graph)
            },
        )

        if self.options.with_flann:
            self.requires("flann/1.9.2")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        # Enforce CMake Policy CMP0077 to NEW.
        # This prevents internal 'option()' command overwrite back to default."
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"

        # Respect the shared option defined in this recipe.
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared

        tc.cache_variables["OMPL_BUILD_PYBINDINGS"] = False
        tc.cache_variables["OMPL_BUILD_DEMOS"] = False
        tc.cache_variables["OMPL_BUILD_TESTS"] = False
        tc.cache_variables["OMPL_BUILD_PYTESTS"] = False
        tc.cache_variables["OMPL_REGISTRATION"] = False
        tc.cache_variables["OMPL_VERSIONED_INSTALL"] = False

        # Handle Optional Dependencies in CMake
        # If with_flann is False, explicitly disable finding the package
        if not self.options.with_flann:
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_flann"] = True

        # Disable others not currently supported in this recipe
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_castxml"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Doxygen"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_spot"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Triangle"] = True

        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        # PATCH: The OMPL CMakeLists.txt hardcodes "SHARED" for non-MSVC builds
        # Remove this keyword so CMake respects Conan's "shared=False" setting
        ompl_cmake_path = os.path.join(
            self.source_folder, "src", "ompl", "CMakeLists.txt"
        )
        replace_in_file(
            self,
            ompl_cmake_path,
            "add_library(ompl SHARED ${OMPL_SOURCE_CODE})",
            "add_library(ompl ${OMPL_SOURCE_CODE})",
        )

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ompl")
        self.cpp_info.set_property("cmake_target_name", "ompl::ompl")
        self.cpp_info.set_property("pkg_config_name", "ompl")

        self.cpp_info.libs = ["ompl"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"


class FclConan(ConanFile):
    name = "fcl"
    description = "C++11 library for performing three types of proximity " \
                  "queries on a pair of geometric models composed of triangles."
    license = "BSD-3-Clause"
    topics = ("geometry", "collision")
    homepage = "https://github.com/flexible-collision-library/fcl"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_octomap": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_octomap": True,
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
        self.requires("eigen/3.4.0")
        self.requires("libccd/2.1")
        if self.options.with_octomap:
            self.requires("octomap/1.9.7")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't properly support shared lib on Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FCL_ENABLE_PROFILING"] = False
        tc.variables["FCL_TREAT_WARNINGS_AS_ERRORS"] = False
        tc.variables["FCL_HIDE_ALL_SYMBOLS"] = False
        tc.variables["FCL_STATIC_LIBRARY"] = not self.options.shared
        tc.variables["FCL_USE_X64_SSE"] = False # Let consumer decide to add relevant compile options, fcl doesn't have simd intrinsics
        tc.variables["FCL_USE_HOST_NATIVE_ARCH"] = False
        tc.variables["FCL_USE_SSE"] = False
        tc.variables["FCL_COVERALLS"] = False
        tc.variables["FCL_COVERALLS_UPLOAD"] = False
        tc.variables["FCL_WITH_OCTOMAP"] = self.options.with_octomap
        if self.options.with_octomap:
            octomap_version_str = self.dependencies["octomap"].ref.version
            tc.variables["OCTOMAP_VERSION"] = octomap_version_str
            octomap_version = Version(octomap_version_str)
            tc.variables["OCTOMAP_MAJOR_VERSION"] = octomap_version.major
            tc.variables["OCTOMAP_MINOR_VERSION"] = octomap_version.minor
            tc.variables["OCTOMAP_PATCH_VERSION"] = octomap_version.patch
        tc.variables["BUILD_TESTING"] = False
        tc.variables["FCL_NO_DEFAULT_RPATH"] = False
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "CMake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"fcl": "fcl::fcl"}
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
        self.cpp_info.set_property("cmake_file_name", "fcl")
        self.cpp_info.set_property("cmake_target_name", "fcl")
        self.cpp_info.set_property("pkg_config_name", "fcl")
        self.cpp_info.libs = ["fcl"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

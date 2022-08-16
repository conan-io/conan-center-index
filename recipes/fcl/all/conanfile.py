from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir, save
import os
import textwrap

required_conan_version = ">=1.50.0"


class FclConan(ConanFile):
    name = "fcl"
    description = "C++11 library for performing three types of proximity " \
                  "queries on a pair of geometric models composed of triangles."
    license = "BSD-3-Clause"
    topics = ("fcl", "geometry", "collision")
    homepage = "https://github.com/flexible-collision-library/fcl"
    url = "https://github.com/conan-io/conan-center-index"

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
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("eigen/3.4.0")
        self.requires("libccd/2.1")
        if self.options.with_octomap:
            self.requires("octomap/1.9.7")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if self.info.settings.os == "Windows" and self.info.options.shared:
            raise ConanInvalidConfiguration(
                "fcl {} doesn't properly support shared lib on Windows".format(self.version)
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

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
            tc.variables["OCTOMAP_VERSION"] = self.deps_cpp_info["octomap"].version
            octomap_major, octomap_minor, octomap_patch = self.deps_cpp_info["octomap"].version.split(".")
            tc.variables["OCTOMAP_MAJOR_VERSION"] = octomap_major
            tc.variables["OCTOMAP_MINOR_VERSION"] = octomap_minor
            tc.variables["OCTOMAP_PATCH_VERSION"] = octomap_patch
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
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fcl")
        self.cpp_info.set_property("cmake_target_name", "fcl")
        self.cpp_info.set_property("pkg_config_name", "fcl")
        self.cpp_info.libs = ["fcl"]

        # TODO: to remove if required_conan_version updated to 1.51.1 (see https://github.com/conan-io/conan/pull/11790)
        self.cpp_info.requires = ["eigen::eigen", "libccd::libccd"]
        if self.options.with_octomap:
            self.cpp_info.requires.append("octomap::octomap")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

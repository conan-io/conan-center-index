from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"

#
# INFO: Please, remove all comments before pushing your PR!
#


class PackageConan(ConanFile):
    name = "package"
    description = "short description"
    # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    # In case not listed there, use "DocumentRef-<license-file-name>:LicenseRef-<package-name>"
    license = ""
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/project/package"
    # no "conan" and project name in topics. Use topics from the upstream listed on GH
    topics = ("topic1", "topic2", "topic3")
    # package_type should usually be "library", "shared-library" or "static-library"
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
        return 14

    # in case the project requires C++14/17/20/... the minimum compiler version should be listed
    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }

    # no exports_sources attribute, but export_sources(self) method instead
    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # for plain C projects only
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Prefer self.requires method instead of requires attribute.
        # Set transitive_headers=True (which usually also requires transitive_libs=True)
        # if the dependency is used in any of the packaged header files.
        self.requires("dependency/0.8.1")
        if self.options.with_foobar:
            # used in foo/baz.hpp:34
            self.requires("foobar/0.1.0", transitive_headers=True, transitive_libs=True)
        # A small number of dependencies on CCI are allowed to use version ranges.
        # See https://github.com/conan-io/conan-center-index/blob/master/docs/adding_packages/dependencies.md#version-ranges
        self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        # validate the minimum cpp standard supported. For C++ projects only
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        # in case it does not work in another configuration, it should be validated here too
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    # if a tool other than the compiler or CMake newer than 3.15 is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # BUILD_SHARED_LIBS and POSITION_INDEPENDENT_CODE are set automatically as tc.variables when self.options.shared or self.options.fPIC exist
        # Note that tc.variables require either cmake_minimum_required() >= 3.13 or the CMP0077 policy set to NEW to work correctly.
        tc = CMakeToolchain(self)
        # Boolean values are preferred instead of "ON"/"OFF"
        tc.variables["PACKAGE_BUILD_TESTS"] = False
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        if self.dependencies["dependency"].options.foobar:
            tc.variables["DEPENDENCY_LIBPATH"] = self.dependencies["dependency"].cpp_info.libdir.replace("\\", "/")
        # cache_variables should be used sparingly, for example to set CMake policies
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        # In case there are dependencies listed under requirements, CMakeDeps should be used
        deps = CMakeDeps(self)
        # You can override the CMake package and target names if they don't match the names used in the project
        deps.set_property("fontconfig", "cmake_file_name", "Fontconfig")
        deps.set_property("fontconfig", "cmake_target_name", "Fontconfig::Fontconfig")
        deps.generate()

        # In case there are dependencies listed under build_requirements, VirtualBuildEnv should be used
        VirtualBuildEnv(self).generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # remove bundled xxhash
        rm(self, "whatever.*", os.path.join(self.source_folder, "lib"))
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "...", "")
        # disable subdirectories by truncating their CMakeLists.txt
        save(self, os.path.join(self.source_folder, "tests", "CMakeLists.txt"), "")

    def build(self):
        self._patch_sources()  # It can be just apply_conandata_patches(self) if no more patches are needed
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["package_lib"]

        # if package has an official FindPACKAGE.cmake listed in https://cmake.org/cmake/help/latest/manual/cmake-modules.7.html#find-modules
        # examples: bzip2, freetype, gdal, icu, libcurl, libjpeg, libpng, libtiff, openssl, sqlite3, zlib...
        self.cpp_info.set_property("cmake_module_file_name", "PACKAGE")
        self.cpp_info.set_property("cmake_module_target_name", "PACKAGE::PACKAGE")
        # if package provides a CMake config file (package-config.cmake or packageConfig.cmake, with package::package target, usually installed in <prefix>/lib/cmake/<package>/)
        self.cpp_info.set_property("cmake_file_name", "package")
        self.cpp_info.set_property("cmake_target_name", "package::package")
        # if package provides a pkgconfig file (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        self.cpp_info.set_property("pkg_config_name", "package")

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")

        # To export additional CMake variables, such as upper-case variables otherwise set by the project's *-config.cmake,
        # you can copy or save a .cmake file under <prefix>/lib/cmake/ with content like
        #     set(XYZ_VERSION ${${CMAKE_FIND_PACKAGE_NAME}_VERSION})
        #     set(XYZ_INCLUDE_DIRS ${${CMAKE_FIND_PACKAGE_NAME}_INCLUDE_DIRS})
        #     ...
        # and set the following fields:
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
        cmake_module = os.path.join("lib", "cmake", "conan-official-variables.cmake")
        self.cpp_info.set_property("cmake_build_modules", [cmake_module])
        self.cpp_info.build_modules["cmake_find_package"] = [cmake_module]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [cmake_module]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "PACKAGE"
        self.cpp_info.filenames["cmake_find_package_multi"] = "package"
        self.cpp_info.names["cmake_find_package"] = "PACKAGE"
        self.cpp_info.names["cmake_find_package_multi"] = "package"

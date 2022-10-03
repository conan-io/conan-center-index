from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os


required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "libical"
    version = "3.0.14"
    description = "Reference implementation of the iCalendar data type and serialization format"
    license = "MPL-2.0 OR LGPL-2.1-only"
    url = "https://github.com/libical/libical"
    homepage = "https://libical.github.io/libical"
    topics = ("libical", "calendar")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cxx_bindings": [True, False],
        "with_glib": [True, False],
        "with_gobject_introspection": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_cxx_bindings": True,
        "with_glib": True,
        "with_gobject_introspection": False,
    }

    _cmake = None

    @property
    def _minimum_cpp_standard(self):
        return 11

    # in case the project requires C++14/17/20/... the minimum compiler version should be listed
    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "0",
            "Visual Studio": "0",
            "clang": "0",
            "apple-clang": "0",
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC  # once removed by config_options, need try..except for a second del
            except Exception:  # pylint: disable=broad-except
                pass
        try:
            del self.settings.compiler.libcxx  # for plain C projects only
        except Exception:  # pylint: disable=broad-except
            pass
        try:
            del self.settings.compiler.cppstd  # for plain C projects only
        except Exception:  # pylint: disable=broad-except
            pass

    def layout(self):
        # src_folder must use the same source folder name the project
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # prefer self.requires method instead of requires attribute
        self.requires("dependency/0.8.1")
        if self.options.with_glib:
            self.requires("glib/2.44")
            self.requires("libxml/2.7.3")
        if self.options.with_gobject_introspection:
            self.requires("gobject-introspection/0.6.7")

    def validate(self):
        # validate the minimum cpp standard supported. For C++ projects only
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        minimum_version = self._compilers_minimum_version.get(
            str(self.info.settings.compiler), False)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support.")
        # in case it does not work in another configuration, it should validated here too
        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    # if another tool than the compiler or CMake is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        self.tool_requires("strawberryperl/5.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        # BUILD_SHARED_LIBS and POSITION_INDEPENDENT_CODE are automatically parsed when self.options.shared or self.options.fPIC exist
        tc = CMakeToolchain(self)
        # turn off deps to avoid picking up them accidentally
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_BDB"] = True
        tc.variables["ICAL_ERRORS_ARE_FATAL"] = False
        tc.variables["ICAL_ALLOW_EMPTY_PROPERTIES="] = False
        tc.variables["ICAL_GLIB_VAPI"] = False
        tc.variables["ICAL_GTK_DOC"] = False
        tc.variables["USE_32BIT_TIME_T"] = False
        tc.variables["ABI_DUMPER"] = False
        tc.variables["ADDRESS_SANITIZER"] = False
        tc.variables["THREAD_SANITIZER"] = False
        tc.variables["ICAL_BUILD_DOCS"] = False
        tc.variables["LIBICAL_BUILD_TESTING"] = False

        # defaults can be overridden by commandline option
        tc.variables["WITH_CXX_BINDINGS"] = self.options.with_cxx_bindings
        tc.variables["ICAL_GLIB"] = self.options.with_glib
        tc.variables["GOBJECT_INTROSPECTION"] = self.options.with_gobject_introspection

        # hard-coded, platform dependent
        if self.settings.os == "Windows":
            tc.variables["USE_BUILTIN_TZDATA"] = True
        else:
            tc.variables["USE_BUILTIN_TZDATA"] = False

        # handle shared vs. static builds. we only want 1 type
        if self.options.shared:
            tc.variables["SHARED_ONLY"] = True
        else:
            tc.variables["STATIC_ONLY"] = True

        # Boolean values are preferred instead of "ON"/"OFF"
        tc.cache_variables["PACKAGE_CUSTOM_DEFINITION"] = True
        if is_msvc(self):
            # don't use self.settings.compiler.runtime
            tc.cache_variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(
                self)
        # deps_cpp_info, deps_env_info and deps_user_info are no longer used
        if self.dependencies["dependency"].options.foobar:
            tc.cache_variables["DEPENDENCY_LIBPATH"] = self.dependencies["dependency"].cpp_info.libdirs
        tc.generate()
        # In case there are dependencies listed on requirements, CMakeDeps should be used
        tc = CMakeDeps(self)
        tc.generate()
        # In case there are dependencies listed on build_requirements, VirtualBuildEnv should be used
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def _patch_sources(self):
        apply_conandata_patches(self)
        # remove bundled xxhash
        rm(self, "whateer.*", os.path.join(self.source_folder, "lib"))
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "...",
            "",
        )

    def build(self):
        # It can be apply_conandata_patches(self) only in case no more patches are needed
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        copy(self, pattern="LICENSE", dst=os.path.join(
            self.package_folder, "license"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la",  os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["package_lib"]

        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "LibIcal")
        self.cpp_info.set_property("cmake_target_name", "LibIcal::LibIcal")
        self.cpp_info.set_property("pkg_config_name", "libical")

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")

        self.cpp_info.names["cmake_find_package"] = "LibIcal"
        self.cpp_info.names["cmake_find_package_multi"] = "LibIcal"

import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration, ConanException


class CppMicroServicesConan(ConanFile):
    name = "cppmicroservices"
    description = "An OSGi-inspired dynamic module framework for C++"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CppMicroServices/CppMicroServices"
    topics = ("modularity", "runtime linking", "dependency inversion",
              "service oriented", "osgi", "microservices", "cross-platform")
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"

    package_type = "library"

    options = {
        "shared":         [True, False],
        "fPIC":           [True, False],
        "with_threading": [True, False],
    }
    default_options = {
        "shared":         True,
        "fPIC":           True,
        "with_threading": True,
    }

    @property
    def _build_compendium(self):
        # Upstream only adds the full compendium when threading + shared libs are both on.
        return bool(self.options.shared and self.options.with_threading)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.17]")

    def requirements(self):
        # boost and cli11 link only into build-time tools (resource compiler, code-gen);
        # visible=False keeps them out of consumers' Conan graphs.
        #
        # miniz/spdlog/rapidjson are baked into the installed shared libraries. rapidjson is
        # header-only. miniz/spdlog are not but their symbols are not exported/visible.
        self.requires("boost/[>=1.86.0 <2]",     visible=False)
        self.requires("miniz/3.1.1")
        self.requires("spdlog/1.14.1")
        self.requires("rapidjson/cci.20220822")
        self.requires("cli11/2.4.1",             visible=False)

    def validate(self):
        check_min_cppstd(self, 17)

        if self.settings.os == "Windows":
            if self.dependencies["boost"].options.get_safe("without_nowide"):
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires boost with nowide on Windows"
                )

        # Mirror the minimum compiler versions enforced by upstream CMake.
        min_versions = {
            "gcc":         "7.5",
            "clang":       "9",
            "apple-clang": "10",
            "msvc":        "191",
        }
        compiler = str(self.settings.compiler)
        min_ver = min_versions.get(compiler)
        if min_ver and Version(str(self.settings.compiler.version)) < min_ver:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires {compiler} >= {min_ver}, "
                f"got {self.settings.compiler.version}"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    # generate is where we set CMake variables and generate both the CMakeToolchain and CMakeDeps files.
    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.17"
        if self.settings.os == "Linux":
            tc.extra_cxxflags.append("-Wno-maybe-uninitialized")
        tc.variables["CMAKE_BUILD_TYPE"] = str(self.settings.build_type)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["US_ENABLE_THREADING_SUPPORT"] = self.options.with_threading
        # Always use Conan-provided packages instead of the bundled third_party/ copies.
        tc.variables["US_USE_SYSTEM_BOOST"] = True
        tc.variables["Boost_NO_BOOST_CMAKE"] = False
        tc.variables["US_USE_SYSTEM_MINIZ"] = True
        tc.variables["US_USE_SYSTEM_SPDLOG"] = True
        tc.variables["US_USE_SYSTEM_RAPIDJSON"] = True
        tc.variables["US_USE_SYSTEM_CLI11"] = True
        # Never pull in test or example build-time deps in a package recipe.
        tc.variables["US_USE_SYSTEM_GTEST"] = False
        tc.variables["US_BUILD_TESTING"] = False
        tc.variables["US_BUILD_EXAMPLES"] = False
        # Set CMAKE_DEBUG_POSTFIX to "" to avoid upstream's default "d" suffix on debug builds,
        # which would break Conan's package ID consistency between build types.
        tc.variables["CMAKE_DEBUG_POSTFIX"] = ""
        # prefer config over find module
        tc.variables["CMAKE_FIND_PACKAGE_PREFER_CONFIG"] = True
        tc.generate()

        deps = CMakeDeps(self)
        # Override where Conan package defaults don't match upstream CMake expectations.
        # rapidjson: default generates find_package(RapidJSON) + target "rapidjson",
        #   but upstream expects find_package(rapidjson) + target "rapidjson::rapidjson".
        deps.set_property("rapidjson", "cmake_file_name",   "rapidjson")
        deps.set_property("rapidjson", "cmake_target_name", "rapidjson::rapidjson")
        deps.generate()

    # build / package are where we call CMake to build and install the library.  The upstream
    # CMakeLists.txt is already set up to install everything correctly, so we don't need to do any
    # manual copying here.
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

    # package_info is where we define the components and their properties for consumers.
    #
    # The upstream CMakeLists.txt defines three components: the core framework (CppMicroServices),
    # the LogService API (usLogService), and the full compendium of built-in bundles
    # (AsyncWorkService, DeclarativeServices ConfigurationAdmin, etc.).  The framework is always
    # present, the LogService API is always built alongside it, and the full compendium is only
    # built when both threading and shared options are enabled.
    def package_info(self):
        major = self.version.split(".")[0]  # "3"
        cmake_dir = os.path.join("share", f"cppmicroservices{major}", "cmake")
        helpers = os.path.join(cmake_dir, "CppMicroServicesHelpers.cmake")

        # cmake_build_modules is included after targets are defined; it exposes
        # the bundle-authoring API (usFunction* helpers, usResourceCompiler target,
        # template paths) without consumers needing to know any install paths.
        self.cpp_info.set_property("cmake_file_name",     "CppMicroServices")
        self.cpp_info.set_property("cmake_build_modules", [helpers])
        self.cpp_info.bindirs = ["bin"]

        lib_dir = os.path.join(self.package_folder, "lib")

        def find_lib(prefix):
            # Find the installed lib matching a prefix and return the bare
            # logical name for cpp_info.libs.  On Unix, filenames look like
            # lib<Name>.X.Y.Z.<ext>, strip the "lib" prefix and version
            # suffixes so we match against the logical name.
            for f in os.listdir(lib_dir):
                if not os.path.isfile(os.path.join(lib_dir, f)):
                    continue
                bare = f.split(".")[0]
                if bare.startswith("lib"):
                    bare = bare[3:]
                if bare.startswith(prefix):
                    return bare
            raise ConanException(
                f"Could not find lib with prefix '{prefix}' in {lib_dir}")

        # framework
        fw = self.cpp_info.components["framework"]
        fw.set_property("cmake_target_name", "CppMicroServices")
        fw.libs = [find_lib("CppMicroServices")]
        fw.includedirs = [f"include/cppmicroservices{major}"]

        if self.settings.os == "Windows":
            fw.system_libs = ["shlwapi"]
        elif self.settings.os == "Linux":
            fw.system_libs = ["dl"]

        if self.options.with_threading and self.settings.os != "Windows":
            fw.system_libs.append("pthread")


        fw.requires = ["miniz::miniz", "spdlog::spdlog",
                       "rapidjson::rapidjson"]

        # LogService (INTERFACE / header-only upstream, no compiled library)
        ls = self.cpp_info.components["logservice"]
        ls.set_property("cmake_target_name", "usLogService")
        ls.requires = ["framework"]

        # Full compendium (threading=ON and shared=ON only)
        if self._build_compendium:
            # CM (INTERFACE / header-only, Configuration Management API)
            cm_comp = self.cpp_info.components["cm"]
            cm_comp.set_property("cmake_target_name", "usCM")
            cm_comp.requires = ["framework"]

            bundles = {
                # component key         : (cmake target,        output name on Unix)
                "logserviceimpl":        ("LogService",          find_lib("LogService")),
                "asyncworkservice":      ("usAsyncWorkService",  find_lib("usAsyncWorkService")),
                "servicecomponent":      ("usServiceComponent",  find_lib("usServiceComponent")),
                "declarativeservices":   ("DeclarativeServices", find_lib("DeclarativeServices")),
                "configurationadmin":    ("ConfigurationAdmin",  find_lib("ConfigurationAdmin")),
                "eventadmin":            ("usEM",                find_lib("usEM")),
            }
            for comp_name, (cmake_tgt, lib_name) in bundles.items():
                comp = self.cpp_info.components[comp_name]
                comp.set_property("cmake_target_name", cmake_tgt)
                comp.libs = [lib_name]
                comp.requires = ["framework"]

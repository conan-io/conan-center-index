from conan import ConanFile
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, replace_in_file
from conan.tools.env import VirtualBuildEnv
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=2.1.0"


class CppMicroServicesConan(ConanFile):
    name = "cppmicroservices"
    description = "An OSGi-like C++ dynamic module system and service registry"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://cppmicroservices.org/"
    topics = ("microservice", "osgi", "microservices-framework")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.91.0", options={"without_nowide": False})
        self.requires("miniz/3.1.1")
        self.requires("rapidjson/cci.20250205")
        self.requires("cli11/2.6.2")
        if self.options.shared:
            # LogService, DeclarativeServices and ConfigurationAdmin bundles are only built as shared libraries
            self.requires("spdlog/[>=1.15 <2]")

    def validate(self):
        check_min_cppstd(self, 17)
        if self.dependencies["boost"].options.without_nowide:
            raise ConanInvalidConfiguration(f"Boost nowide is required for {self.name}. Build with -o 'boost/*:without_nowide=False'")
        if cross_building(self):
            # FIXME: usResourceCompiler is a build tool in CppMicroServices required by cppmicroservices
            # We need to run it as for native arch and solve its dynamic linking issues
            raise ConanInvalidConfiguration(f"Cross-building is not supported yet. Contributions are welcome!")
        # FIXME: usResourceCompiler3 tools have issues locating shared DLLs on Windows
        # We can patch its cmake to inject library paths
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(f"usResourceCompiler3 tools can not find shared DLLs. Contributions are welcome!")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.17]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # error: virtual method '~ConfigurationManager' is inside a 'final' class and can never be overridden
        # Fixed by https://github.com/CppMicroServices/CppMicroServices/pull/1275
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "-Werror", "")
        # Link Boost::nowide from Conan instead of virtual imported target nowide::nowide
        replace_in_file(self, os.path.join(self.source_folder, "tools", "rc", "CMakeLists.txt"), "nowide::nowide", "Boost::nowide")
        # Let Conan manage cppstd
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD 17)", "")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["US_USE_SYSTEM_BOOST"] = True
        tc.cache_variables["US_USE_SYSTEM_MINIZ"] = True
        tc.cache_variables["US_USE_SYSTEM_SPDLOG"] = self.options.shared
        tc.cache_variables["US_USE_SYSTEM_RAPIDJSON"] = True
        tc.cache_variables["US_USE_SYSTEM_CLI11"] = True
        tc.cache_variables["US_BUILD_TESTING"] = False
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Doxygen"] = True
        tc.preprocessor_definitions["US_HAVE_BOOST_NOWIDE"] = "1"
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("boost", "cmake_target_name", "boost::boost")
        deps.set_property("rapidjson", "cmake_file_name", "rapidjson")
        deps.set_property("rapidjson", "cmake_target_name", "rapidjson::rapidjson")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYRIGHT", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # INFO: keep the helper scripts (usFunction*.cmake, CppMicroServicesHelpers.cmake)
        cmake_dir = os.path.join(self.package_folder, "share", "cppmicroservices3", "cmake")
        rm(self, "*Config.cmake", cmake_dir)
        rm(self, "*ConfigVersion.cmake", cmake_dir)
        rm(self, "*Targets*.cmake", cmake_dir)

    def package_info(self):
        libsuffix = "d" if self.settings.build_type == "Debug" else ""
        libversion = "3" if self.settings.os == "Windows" else ""
        complibversion = "1" if self.settings.os == "Windows" else ""
        self.cpp_info.set_property("cmake_file_name", "CppMicroServices")
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("share", "cppmicroservices3", "cmake", "CppMicroServicesHelpers.cmake")])

        # The executable is named usResourceCompiler3 on every platform
        self.cpp_info.components["usresourcecompiler3"].exe = "usResourceCompiler3"
        self.cpp_info.components["usresourcecompiler3"].location = os.path.join(self.package_folder, "bin", "usResourceCompiler3")
        # Only the Boost.Nowide headers are used
        self.cpp_info.components["usresourcecompiler3"].requires = ["boost::headers", "miniz::miniz"]
        self.cpp_info.components["usresourcecompiler3"].libdirs = []
        self.cpp_info.components["usresourcecompiler3"].includedirs = []

        self.cpp_info.components["jsonschemavalidator"].exe = "jsonschemavalidator"
        self.cpp_info.components["jsonschemavalidator"].location = os.path.join(self.package_folder, "bin", "jsonschemavalidator")
        self.cpp_info.components["jsonschemavalidator"].requires = ["cli11::cli11"]
        self.cpp_info.components["jsonschemavalidator"].libdirs = []
        self.cpp_info.components["jsonschemavalidator"].includedirs = []

        self.cpp_info.components["change_namespace"].exe = "change_namespace"
        self.cpp_info.components["change_namespace"].location = os.path.join(self.package_folder, "bin", "change_namespace")
        self.cpp_info.components["change_namespace"].requires = ["cli11::cli11"]
        self.cpp_info.components["change_namespace"].libdirs = []
        self.cpp_info.components["change_namespace"].includedirs = []

        self.cpp_info.components["scrcodegen3"].exe = "SCRCodeGen3"
        self.cpp_info.components["scrcodegen3"].location = os.path.join(self.package_folder, "bin", "SCRCodeGen3")
        self.cpp_info.components["scrcodegen3"].libdirs = []
        self.cpp_info.components["scrcodegen3"].includedirs = []

        self.cpp_info.components["usframework"].set_property("cmake_file_name", "usFramework")
        self.cpp_info.components["usframework"].set_property("cmake_target_name", "CppMicroServices")
        self.cpp_info.components["usframework"].libs = [f"CppMicroServices{libversion}{libsuffix}"]
        self.cpp_info.components["usframework"].includedirs.append(os.path.join("include", "cppmicroservices3"))
        self.cpp_info.components["usframework"].requires = ["miniz::miniz", "rapidjson::rapidjson"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["usframework"].system_libs.append("pthread")
        if self.settings.os == "Linux":
            self.cpp_info.components["usframework"].system_libs.append("dl")
        elif self.settings.os == "Windows":
            self.cpp_info.components["usframework"].system_libs.append("shlwapi")

        self.cpp_info.components["cppmicroservices"].set_property("cmake_file_name", "CppMicroServices")
        self.cpp_info.components["cppmicroservices"].requires = ["usframework"]
        self.cpp_info.components["cppmicroservices"].libdirs = []
        self.cpp_info.components["cppmicroservices"].includedirs = []

        if self.options.shared:
            self.cpp_info.components["uslogservice"].set_property("cmake_file_name", "usLogServiceImpl")
            self.cpp_info.components["uslogservice"].set_property("cmake_target_name", "LogService")
            self.cpp_info.components["uslogservice"].libs = [f"LogService{complibversion}{libsuffix}"]
            self.cpp_info.components["uslogservice"].includedirs.append(os.path.join("include", "cppmicroservices3"))
            self.cpp_info.components["uslogservice"].requires = ["usframework", "spdlog::spdlog"]

            self.cpp_info.components["usasyncworkservice"].set_property("cmake_file_name", "usAsyncWorkService")
            self.cpp_info.components["usasyncworkservice"].set_property("cmake_target_name", "usAsyncWorkService")
            self.cpp_info.components["usasyncworkservice"].libs = [f"usAsyncWorkService{libsuffix}"]
            self.cpp_info.components["usasyncworkservice"].includedirs.append(os.path.join("include", "cppmicroservices3"))

            self.cpp_info.components["usservicecomponent"].set_property("cmake_file_name", "usServiceComponent")
            self.cpp_info.components["usservicecomponent"].set_property("cmake_target_name", "usServiceComponent")
            self.cpp_info.components["usservicecomponent"].libs = [f"usServiceComponent{libsuffix}"]
            self.cpp_info.components["usservicecomponent"].includedirs.append(os.path.join("include", "cppmicroservices3"))
            self.cpp_info.components["usservicecomponent"].requires = ["usframework"]

            self.cpp_info.components["usem"].set_property("cmake_file_name", "usem")
            self.cpp_info.components["usem"].set_property("cmake_target_name", "usEM")
            self.cpp_info.components["usem"].libs = [f"usEM{libsuffix}"]
            self.cpp_info.components["usem"].includedirs.append(os.path.join("include", "cppmicroservices3"))
            self.cpp_info.components["usem"].requires = ["usframework"]

            self.cpp_info.components["usdeclarativeservices"].set_property("cmake_file_name", "usDeclarativeServices")
            self.cpp_info.components["usdeclarativeservices"].set_property("cmake_target_name", "DeclarativeServices")
            self.cpp_info.components["usdeclarativeservices"].libs = [f"DeclarativeServices{complibversion}{libsuffix}"]
            self.cpp_info.components["usdeclarativeservices"].includedirs.append(os.path.join("include", "cppmicroservices3"))
            self.cpp_info.components["usdeclarativeservices"].requires = ["usframework", "usservicecomponent", "usasyncworkservice", "boost::headers"]

            self.cpp_info.components["usconfigurationadmin"].set_property("cmake_file_name", "usConfigurationAdmin")
            self.cpp_info.components["usconfigurationadmin"].set_property("cmake_target_name", "ConfigurationAdmin")
            self.cpp_info.components["usconfigurationadmin"].libs = [f"ConfigurationAdmin{complibversion}{libsuffix}"]
            self.cpp_info.components["usconfigurationadmin"].includedirs.append(os.path.join("include", "cppmicroservices3"))
            self.cpp_info.components["usconfigurationadmin"].requires = ["usframework", "usasyncworkservice", "boost::headers"]

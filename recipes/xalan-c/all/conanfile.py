from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.0.5"


class XalanCConan(ConanFile):
    name = "xalan-c"
    description = "Xalan-C++ is a library to transform XML documents using XSLT"
    topics = ("xalan", "XML", "XSLT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://apache.github.io/xalan-c"
    license = "Apache-2.0"

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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        if self.settings.os == "Windows":
            del self.options.shared
            self.package_type = "shared-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        if self.settings.os == "Windows":
            # cmake >=3.25 required to use `cmake -E env --modify` patch
            self.tool_requires("cmake/[>=3.25]")

    def requirements(self):
        self.requires("xerces-c/[>=3.2.2 <4]", transitive_headers=True)

    def validate(self):
        if (self.settings.os == "Windows" and not self.dependencies.direct_host["xerces-c"].options.shared):
            # shared xalan-c with static xerces-c fails at runtime in the consumer during Static initialisation
            # when calling  xercesc::XMLPlatformUtils::Initialize() + xalanc::XalanTransformer::initialize(); as documented
            # presumably because symbols from xerces-c end up in both the consumer and the xalan-c DLL
            raise ConanInvalidConfiguration("shared Xalan-C does not work with static Xerces-C on Windows (builds but fails at runtime)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD 14)",
                        "## set(CMAKE_CXX_STANDARD 14)")

    def generate(self):
        tc = CMakeToolchain(self)
        # Because upstream overrides BUILD_SHARED_LIBS as a CACHE variable
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.get_safe("shared", True)
        tc.cache_variables["transcoder"] = "default" # icu is currently not supported
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        if self.settings.os == "Windows":
            # `MsgCreator` is built and run during the build - modify the environment on Windows to find the DLL dependency
            replace_in_file(self, os.path.join(self.source_folder, "src/xalanc/Utils/CMakeLists.txt"),
                            'COMMAND "$<TARGET_FILE:MsgCreator>"',
                            'COMMAND ${CMAKE_COMMAND} -E env --modify "PATH=path_list_prepend:$<JOIN:${CONAN_RUNTIME_LIB_DIRS},;>" "$<TARGET_FILE:MsgCreator>"')

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        for license_file in ("LICENSE", "NOTICE"):
            copy(self, license_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "XalanC")
        self.cpp_info.set_property("pkg_config_name", "xalan-c")

        _debug_postfix = "D" if self.settings.build_type == "Debug" else ""
        self.cpp_info.components["xalan-c"].libs = [f"Xalan-C_1{_debug_postfix}"] if is_msvc(self) else ["xalan-c"]
        self.cpp_info.components["xalan-c"].set_property("cmake_target_name", "XalanC::XalanC")
        self.cpp_info.components["xalan-c"].requires = ["xalanMsg"]

        self.cpp_info.components["xalanMsg"].libs = [f"XalanMsgLib_1{_debug_postfix}"] if is_msvc(self) else ["xalanMsg"]
        self.cpp_info.components["xalanMsg"].set_property("cmake_target_name", "XalanC::XalanMsg")
        self.cpp_info.components["xalanMsg"].requires = ["xerces-c::xerces-c"]


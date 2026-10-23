from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os


required_conan_version = ">=2.0.9"

class OpencolladaConan(ConanFile):
    name = "opencollada"
    description = "Library to works with DAE (Digital Assets Exchange) file"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KhronosGroup/OpenCOLLADA"
    topics = ("3d", "dae")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    # no exports_sources attribute, but export_sources(self) method instead
    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 14)
        # if self.settings.os == "Windows" and self.options.shared:
        #     raise ConanInvalidConfiguration("Disable temporary windows platform with shared build")

    def requirements(self):
        # self.requires("zlib/[>=1.2.11 <2]")
        # self.requires("llvm-core/[>=19.1.7 <20]")
        self.requires("pcre/[>=8.45 <9]")
        self.requires("libxml2/[>=2.12.5 <3]")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Using patches is always the last resort to fix issues. If possible, try to fix the issue in the upstream project.
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["USE_STATIC"] = not self.options.shared
        tc.cache_variables["USE_SHARED"] = self.options.shared
        tc.generate()

        deps = CMakeDeps(self)
        # deps.set_property("llvm-core", "cmake_target_name", "UTF")
        deps.generate()

    def build(self):
        # if self.settings.compiler == "gcc":
        #     replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), 'set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CXX_WARNINGS}")', 'set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CXX_WARNINGS} -Wno-error=dangling-reference")')
        # elif self.settings.compiler == "apple-clang":
        #     replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), 'set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CXX_WARNINGS}")', 'set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CXX_WARNINGS} -Wno-unqualified-std-cast-call")')  
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenCOLLADA")
        # self.cpp_info.libdirs = ['lib/opencollada']

        ftoaComponent = self.cpp_info.components["ftoa"]
        ftoaComponent.libdirs = [os.path.join("lib", "opencollada")]
        ftoaComponent.libs = ["ftoa"]
        
        utfComponent = self.cpp_info.components["utf"]
        utfComponent.libdirs = [os.path.join("lib", "opencollada")]
        utfComponent.libs = ["UTF"]
        
        bufferComponent = self.cpp_info.components["buffer"]
        bufferComponent.libdirs = [os.path.join("lib", "opencollada")]
        bufferComponent.libs = ["buffer "]
        bufferComponent.requires = ["ftoa", "utf"]

        mathMLSolverComponent = self.cpp_info.components["MathMLSolver"]
        mathMLSolverComponent.libdirs = [os.path.join("lib", "opencollada")]
        mathMLSolverComponent.libs = ["MathMLSolver"]
        
        openCOLLADABaseUtilsComponent = self.cpp_info.components["openCOLLADABaseUtils"]
        openCOLLADABaseUtilsComponent.includedirs = [os.path.join("include", "opencollada", "COLLADABaseUtils")]
        openCOLLADABaseUtilsComponent.libdirs = [os.path.join("lib", "opencollada")]
        openCOLLADABaseUtilsComponent.libs = ["OpenCOLLADABaseUtils"]
        openCOLLADABaseUtilsComponent.requires = ["utf", "pcre::pcre"]
        
        colladaStreamWriterComponent = self.cpp_info.components["COLLADAStreamWriter"]
        colladaStreamWriterComponent.includedirs = [os.path.join("include", "opencollada", "COLLADAStreamWriter")]
        colladaStreamWriterComponent.libdirs = [os.path.join("lib", "opencollada")]
        colladaStreamWriterComponent.libs = ["OpenCOLLADAStreamWriter"]
        colladaStreamWriterComponent.requires = ["openCOLLADABaseUtils", "buffer", "ftoa"]

        generatedSaxParserComponent = self.cpp_info.components["GeneratedSaxParser"]
        generatedSaxParserComponent.includedirs = [os.path.join("include", "opencollada", "GeneratedSaxParser")]
        generatedSaxParserComponent.libdirs = [os.path.join("lib", "opencollada")]
        generatedSaxParserComponent.libs = ["GeneratedSaxParser"]
        generatedSaxParserComponent.requires = ["openCOLLADABaseUtils", "libxml2::libxml2"]
        
        openColladaFrameworkComponent = self.cpp_info.components["OpenCOLLADAFramework"]
        openColladaFrameworkComponent.includedirs = [os.path.join("include", "opencollada", "COLLADAFramework")]
        openColladaFrameworkComponent.libdirs = [os.path.join("lib", "opencollada")]
        openColladaFrameworkComponent.libs = ["OpenCOLLADAFramework"]
        openColladaFrameworkComponent.requires = ["openCOLLADABaseUtils"]
        
        openColladaFrameworkComponent = self.cpp_info.components["OpenCOLLADASaxFrameworkLoader"]
        openColladaFrameworkComponent.includedirs = [os.path.join("include", "opencollada", "COLLADAFramework")]
        openColladaFrameworkComponent.libdirs = [os.path.join("lib", "opencollada")]
        openColladaFrameworkComponent.libs = ["OpenCOLLADASaxFrameworkLoader"]
        openColladaFrameworkComponent.requires = ["openCOLLADABaseUtils", "GeneratedSaxParser", "OpenCOLLADAFramework", "MathMLSolver", "pcre::pcre"]
        
      
        # def _add_component(name, requires=None):
        #     component = self.cpp_info.components[name]
        #     component.includedirs = [os.path.join("include", "opencollada", name)]
        #     # component.set_property("cmake_target_name", name)
        #     component.libs = [name]
        #     component.requires = requires or []
        #     return component

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

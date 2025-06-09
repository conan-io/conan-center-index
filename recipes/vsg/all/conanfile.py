from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import get, copy, rm, rmdir, collect_libs
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
import os

required_conan_version = ">=2.0"

class VsgConan(ConanFile):
    name = "vsg"
    description = "VulkanSceneGraph"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.vulkanscenegraph.org"
    topics = ("vulkan", "scenegraph", "graphics", "3d")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "max_devices": [1,2,3,4],
        "windowing": [True, False],
        "with_glslang": [True, False],
        "max_instrumentation_level": [0,1,2,3],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "max_devices" : 1,
        "windowing" : True,
        "with_glslang" : False,
        "max_instrumentation_level": 1,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
   
        if Version(self.version) < "1.1.10":
           del self.options.max_instrumentation_level
                            


    def requirements(self):
        self.requires("vulkan-loader/1.3.268.0", transitive_headers=True)
        if self.options.with_glslang:
            self.requires("glslang/1.3.268.0")
            # Required to avoid missing include:
            # It seems VSG relies on spirv headers that are propagated via
            # glslang components, but conan glslang does not provide
            # proper directory linkage to consumers. thus, its explicitly added.
            self.requires("spirv-tools/1.3.268.0")  
    
    def build_requirements(self):
        if self.options.with_glslang:
            self.build_requires("glslang/1.3.268.0")
            self.build_requires("spirv-tools/1.3.268.0")
    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)

        if is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(f"{self.name} does not support MSVC static runtime (MT/MTd) configurations, only dynamic runtime (MD/MDd) is supported")

        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
            if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
 
    def generate(self):
        tc = CMakeToolchain(self)

        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["VSG_SUPPORTS_ShaderCompiler"] = 1 if self.options.with_glslang else 0
        tc.cache_variables["VSG_MAX_DEVICES"] = self.options.max_devices
        tc.cache_variables["VSG_SUPPORTS_Windowing"] = 1 if self.options.windowing else 0

        # Override GLSLANG_MIN_VERSION to ensure compatibility with the Conan-provided glslang.
        #
        # VSG sets GLSLANG_MIN_VERSION to "14" by default, based on glslang's internal versioning.
        # However, the glslang package in Conan Center follows Vulkan SDK versioning instead.
        #
        # Only glslang >= 1.3.243.0 (Vulkan SDK version) in Conan exports the 
        # `glslang-default-resource-limits` CMake target required by VSG.
        #
        # Without this override, VSG's call to:
        #     find_package(glslang ${GLSLANG_MIN_VERSION} CONFIG)
        # will fail, because no Conan-provided glslang package matches the default version "14".
        #
        # Note: GLSLANG_MIN_VERSION **must** be explicitly set. Leaving it at its default will 
        # cause `find_package` to fail. While patching the VSG CMakeLists is an option, overriding
        # the variable here is the cleanest and most maintainable solution.
        tc.cache_variables["GLSLANG_MIN_VERSION"] = "1.3.243.0"


        if Version(self.version) >= "1.1.10":
            tc.cache_variables["VSG_MAX_INSTRUMENTATION_LEVEL"] = self.options.max_instrumentation_level

        if is_msvc(self):
            tc.cache_variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = False

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rm(self, "Find*.cmake", os.path.join(self.package_folder, "lib/cmake/vsg"))
        rm(self, "*Config.cmake", os.path.join(self.package_folder, "lib/cmake/vsg"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        self.cpp_info.set_property("cmake_file_name", "vsg")
        self.cpp_info.set_property("cmake_target_name", "vsg::vsg")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")

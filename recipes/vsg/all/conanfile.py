from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import get, copy, rm, rmdir, collect_libs
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version, Git
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
import os

required_conan_version = ">=1.53.0"

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
        "shader_compiler": [True, False],
        "max_devices": [1,2,3,4],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "shader_compiler": True,
        "max_devices" : 1,
        "fPIC": True,
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

    def requirements(self):
        self.requires("vulkan-loader/1.3.239.0", transitive_headers=True)

    def validate(self):
        if self.info.settings.compiler.cppstd:
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

        if "glslang" in self.conan_data and self.version in self.conan_data["glslang"]:
            git = Git(self)
            clone_args = ['--depth', '1', '--branch', self.conan_data["glslang"][self.version]["branch"]]
            git.clone(url= self.conan_data["glslang"][self.version]["url"], args=clone_args, target ="src/glslang")

    def generate(self):
        tc = CMakeToolchain(self)
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = False
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["VSG_SUPPORTS_ShaderCompiler"] = 1 if self.options.shader_compiler else 0
        tc.variables["VSG_MAX_DEVICES"] = self.options.max_devices
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

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "vsg"
        self.cpp_info.filenames["cmake_find_package_multi"] = "vsg"
        self.cpp_info.names["cmake_find_package"] = "VSG"
        self.cpp_info.names["cmake_find_package_multi"] = "vsg"

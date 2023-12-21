from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from os.path import join

required_conan_version = ">=1.53.0"


class HiGHSConan(ConanFile):
    name = "highs"
    description = "high performance serial and parallel solver for large scale sparse linear optimization problems"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.highs.dev/"
    topics = ("simplex", "interior point", "solver", "linear", "programming")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SHARED"] = self.options.shared
        tc.variables["BUILD_TESTING"] = False
        tc.variables["PYTHON"] = False
        tc.variables["FORTRAN"] = False
        tc.variables["CSHARP"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="highs")

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=join(self.package_folder, "licenses"))
        copy(self, pattern="*.h", src=join(self.source_folder, "src"), dst=join(self.package_folder, "include"))
        copy(self, pattern="HConfig.h", src=self.build_folder, dst=join(self.package_folder, "include"))
        if self.options.shared:
            copy(self, pattern="*.so*", src=join(self.build_folder, "lib"), dst=join(self.package_folder, "lib"))
            copy(self, pattern="*.dylib*", src=join(self.build_folder, "lib"), dst=join(self.package_folder, "lib"))
            copy(self, pattern="*.lib", src=self.build_folder, dst=join(self.package_folder, "lib"), keep_path=False)
            copy(self, pattern="*.dll", src=self.build_folder, dst=join(self.package_folder, "bin"), keep_path=False)
        else:
            copy(self, pattern="*.a", src=join(self.build_folder, "lib"), dst=join(self.package_folder, "lib"))
            if Version(self.version) >= Version("1.5.3"):
                # https://github.com/ERGO-Code/HiGHS/commit/2c24b4cb6ecece98ed807dbeff9b27a2fbba8d37
                copy(self, pattern="*.lib", src=self.build_folder, dst=join(self.package_folder, "lib"), keep_path=False)
            else:
                copy(self, pattern="*.lib", src=join(self.build_folder, "lib"), dst=join(self.package_folder, "lib"), keep_path=False)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
        if is_msvc(self) and Version(self.version) < Version("1.5.3"):
            # https://github.com/ERGO-Code/HiGHS/commit/7d784db29ab22003670b8b2eb494ab1a97f1815b
            self.cpp_info.defines.append("_ITERATOR_DEBUG_LEVEL=0")

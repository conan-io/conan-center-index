from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version
from os.path import join

required_conan_version = ">=1.53.0"


class SCIPConan(ConanFile):
    name = "scip"
    description = "SCIP mixed integer (nonlinear) programming solver"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://scipopt.org/"
    topics = ("mip", "solver", "linear", "programming")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_boost": [True, False],
        "with_gmp": [True, False],
        "with_tpi": ["none", "omp", "tny"],
        "with_sym": ["bliss", "none"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_boost": True,
        "with_gmp": True,
        "with_tpi": "none",
        "with_sym": "bliss",
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "4",
            "apple-clang": "7",
        }

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")
        if self.options.shared and self.options.with_sym == "bliss":
            raise ConanInvalidConfiguration("Bliss is not supported in shared mode.")
        comp = self.settings.compiler
        if self.options.with_sym == "bliss" and comp == 'clang' and comp.libcxx and comp.libcxx == 'libc++':
            raise ConanInvalidConfiguration("Bliss does not support libc++.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("soplex/6.0.3")

    def configure(self):
        self.options["soplex"].with_boost = self.options.with_boost
        self.options["soplex"].with_gmp = self.options.with_gmp
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    @staticmethod
    def _to_cmake(*arrays):
        return ";".join(item.replace("\\", "/") for sublist in arrays for item in sublist)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SHARED"] = self.options.shared
        tc.variables["READLINE"] = False  # required for interactive stuff
        tc.variables["GMP"] = self.options.with_gmp
        tc.variables["BOOST"] = self.options.with_boost
        tc.variables["TPI"] = self.options.with_tpi
        tc.variables["LPS"] = "spx"
        tc.variables["SYM"] = self.options.with_sym
        tc.variables["SOPLEX_INCLUDE_DIRS"] = self._to_cmake(self.dependencies["soplex"].cpp_info.includedirs)
        if self.options.shared:
            # CMakeLists accesses different variables for SoPlex depending on the SHARED option
            tc.variables["SOPLEX_PIC_LIBRARIES"] = "soplex"
        if self.options.with_gmp:
            tc.cache_variables["GMP_INCLUDE_DIRS"] = self._to_cmake(self.dependencies["gmp"].cpp_info.includedirs)
        if self.options.with_boost:
            tc.cache_variables["SOPLEX_INCLUDE_DIRS"] = self._to_cmake(  # docu states BOOST_ROOT, yet that does not exist in CMakeLists
                self.dependencies["soplex"].cpp_info.includedirs,
                self.dependencies["soplex"].dependencies["boost"].cpp_info.includedirs
            )
        tc.variables["PAPILO"] = False  # LGPL
        tc.variables["ZIMPL"] = False  # LPGL
        tc.variables["IPOPT"] = False  # no such coin package on conan center yet
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="libscip")

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=join(self.package_folder, "licenses"))
        # cmake install is not used as this requires the command line tools to be built, which we do not do
        copy(self, pattern="*.h", src=join(self.source_folder, "src"), dst=join(self.package_folder, "include"))
        copy(self, pattern="*.h", src=join(self.build_folder, "scip"), dst=join(self.package_folder, "include", "scip"))
        if self.options.shared:
            copy(self, pattern="*.so*", src=join(self.build_folder, "lib"), dst=join(self.package_folder, "lib"))
            copy(self, pattern="*.dylib*", src=join(self.build_folder, "lib"), dst=join(self.package_folder, "lib"))
        else:
            copy(self, pattern="*.a", src=join(self.build_folder, "lib"), dst=join(self.package_folder, "lib"))
            copy(self, pattern="*.lib", src=join(self.build_folder, "lib"), dst=join(self.package_folder, "lib"), keep_path=False)
            copy(self, pattern="*.lib", src=self.build_folder, dst=join(self.package_folder, "lib"), keep_path=False)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.libs = ["libscip" if is_msvc(self) else "scip"]
        if self.options.with_sym == "bliss":
            self.cpp_info.libs.append("bliss")
        if self.options.with_tpi == "omp":
            self.cpp_info.system_libs.append("-fopenmp")

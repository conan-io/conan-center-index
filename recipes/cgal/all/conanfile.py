import os
import textwrap
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, replace_in_file, rmdir, rm, copy, save, export_conandata_patches, apply_conandata_patches
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.50.0"

class CgalConan(ConanFile):
    name = "cgal"
    license = "GPL-3.0-or-later", "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CGAL/cgal"
    description = "C++ library that provides easy access to efficient and reliable algorithms"\
                  " in computational geometry."
    topics = ("cgal", "geometry", "algorithms")
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"
    short_paths = True

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.83.0")
        self.requires("eigen/3.4.0")
        self.requires("mpfr/4.2.1")
        self.requires("gmp/6.3.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def _patch_sources(self):
        replace_in_file(self,  os.path.join(self.source_folder, "CMakeLists.txt"),
                        "if(NOT PROJECT_NAME)", "if(1)", strict=False)
        apply_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "bin"))
        rm(self, "*Config*.cmake", os.path.join(self.package_folder, "lib", "cmake", "CGAL"))
        rm(self, "Find*.cmake", os.path.join(self.package_folder, "lib", "cmake", "CGAL"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._cmake_module_file_rel_path)
        )

    def _create_cmake_module_variables(self, module_file):
        '''
        CGAL requires C++14, and specific compilers flags to enable the possibility to set FPU rounding modes.
        This CMake module, from the upstream CGAL pull-request https://github.com/CGAL/cgal/pull/7512, takes
        care of all the known compilers CGAL has ever supported.
        '''
        content = textwrap.dedent('''\
function(CGAL_setup_CGAL_flags target)
  # CGAL now requires C++14. `decltype(auto)` is used as a marker of
  # C++14.
  target_compile_features(${target} INTERFACE cxx_decltype_auto)

  if(MSVC)
    target_compile_options(${target} INTERFACE
      "-D_SCL_SECURE_NO_DEPRECATE;-D_SCL_SECURE_NO_WARNINGS")
    if(CMAKE_VERSION VERSION_LESS 3.11)
      target_compile_options(${target} INTERFACE
        /fp:strict
        /fp:except-
        /wd4503  # Suppress warnings C4503 about "decorated name length exceeded"
        /bigobj  # Use /bigobj by default
        )
    else()
      # The MSVC generator supports `$<COMPILE_LANGUAGE: >` since CMake 3.11.
      target_compile_options(${target} INTERFACE
        $<$<COMPILE_LANGUAGE:CXX>:/fp:strict>
        $<$<COMPILE_LANGUAGE:CXX>:/fp:except->
        $<$<COMPILE_LANGUAGE:CXX>:/wd4503>  # Suppress warnings C4503 about "decorated name length exceeded"
        $<$<COMPILE_LANGUAGE:CXX>:/bigobj>  # Use /bigobj by default
        )
    endif()
  elseif ("${CMAKE_CXX_COMPILER_ID}" MATCHES "AppleClang")
    if (CMAKE_CXX_COMPILER_VERSION VERSION_LESS 11.0.3)
      message(STATUS "Apple Clang version ${CMAKE_CXX_COMPILER_VERSION} compiler detected")
      message(STATUS "Boost MP is turned off for all Apple Clang versions below 11.0.3!")
      target_compile_options(${target} INTERFACE "-DCGAL_DO_NOT_USE_BOOST_MP")
    endif()
  elseif(CMAKE_CXX_COMPILER_ID MATCHES "Intel")
    message( STATUS "Using Intel Compiler. Adding -fp-model strict" )
    if(WIN32)
      target_compile_options(${target} INTERFACE "/fp:strict")
    else()
      target_compile_options(${target} INTERFACE "-fp-model" "strict")
    endif()
  elseif(CMAKE_CXX_COMPILER_ID MATCHES "SunPro")
    message( STATUS "Using SunPro compiler, using STLPort 4." )
    target_compile_options(${target} INTERFACE
      "-features=extensions;-library=stlport4;-D_GNU_SOURCE")
    target_link_libraries(${target} INTERFACE "-library=stlport4")
  elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    if ( RUNNING_CGAL_AUTO_TEST OR CGAL_TEST_SUITE )
      target_compile_options(${target} INTERFACE "-Wall")
    endif()
    if(CMAKE_CXX_COMPILER_VERSION VERSION_GREATER 3)
      message( STATUS "Using gcc version 4 or later. Adding -frounding-math" )
      if(CMAKE_VERSION VERSION_LESS 3.3)
        target_compile_options(${target} INTERFACE "-frounding-math")
      else()
        target_compile_options(${target} INTERFACE "$<$<COMPILE_LANGUAGE:CXX>:-frounding-math>")
      endif()
    endif()
    if ( "${GCC_VERSION}" MATCHES "^4.2" )
      message( STATUS "Using gcc version 4.2. Adding -fno-strict-aliasing" )
      target_compile_options(${target} INTERFACE "-fno-strict-aliasing" )
    endif()
    if ( "${CMAKE_SYSTEM_PROCESSOR}" MATCHES "alpha" )
      message( STATUS "Using gcc on alpha. Adding -mieee -mfp-rounding-mode=d" )
      target_compile_options(${target} INTERFACE "-mieee" "-mfp-rounding-mode=d" )
    endif()
  endif()
endfunction()

CGAL_setup_CGAL_flags(CGAL::CGAL)

# CGAL use may rely on the presence of those two variables
set(CGAL_USE_GMP  TRUE CACHE INTERNAL "CGAL library is configured to use GMP")
set(CGAL_USE_MPFR TRUE CACHE INTERNAL "CGAL library is configured to use MPFR")
''')
        save(self, module_file, content)

    @property
    def _cmake_module_file_rel_path(self):
        return os.path.join("lib", "cmake", "CGAL", f"conan-official-{self.name}-variables.cmake")

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake", "CGAL")

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.set_property("cmake_find_package", "CGAL")
        self.cpp_info.set_property("cmake_target_name", "CGAL::CGAL")
        self.cpp_info.set_property("cmake_build_modules", [self._cmake_module_file_rel_path])

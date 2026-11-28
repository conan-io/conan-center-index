from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import textwrap


required_conan_version = ">=2.0.9"

class MatplotPlusPlusConan(ConanFile):
    name = "matplotplusplus"
    description = "Matplot++: A C++ Graphics Library for Data Visualization"
    license = "MIT"
    url = "https://github.com/alandefreitas/matplotplusplus"
    homepage = "https://alandefreitas.github.io/matplotplusplus/"
    topics = ("graphics", "plotting", "visualization", "charts", "gnuplot")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_opengl": [True, False],
        "with_jpeg": [True, False],
        "with_tiff": [True, False],
        "with_zlib": [True, False],
        "with_png": [True, False],
        "with_fftw": [True, False],
        "with_opencv": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_opengl": False,
        "with_jpeg": False,
        "with_tiff": False,
        "with_zlib": False,
        "with_png": False,
        "with_fftw": False,
        "with_opencv": False,
        "cimg/*:enable_x11": False,
    }
    implements = ["auto_shared_fpic"]

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "11",
            "msvc": "192",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("nodesoup/cci.20200905")
        self.requires("cimg/3.3.2")
        if self.options.with_opengl:
            self.requires("opengl/system")
            self.requires("glfw/3.4")
            self.requires("glad/0.1.36")
        if self.options.with_jpeg:
            self.requires("libjpeg/9f")
        if self.options.with_tiff:
            self.requires("libtiff/4.7.0")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_fftw:
            self.requires("fftw/3.3.10")
        if self.options.with_opencv:
            self.requires("opencv/[>=4.5.0 <5]")

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Remove vendored libraries to ensure Conan packages are used
        rmdir(self, os.path.join(self.source_folder, "source", "3rd_party", "nodesoup"))
        rmdir(self, os.path.join(self.source_folder, "source", "3rd_party", "cimg"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MATPLOTPP_BUILD_EXAMPLES"] = False
        tc.variables["MATPLOTPP_BUILD_TESTS"] = False
        tc.variables["MATPLOTPP_BUILD_INSTALLER"] = True
        tc.variables["MATPLOTPP_BUILD_FOR_DOCUMENTATION_IMAGES"] = False
        tc.variables["MATPLOTPP_BUILD_EXPERIMENTAL_OPENGL_BACKEND"] = self.options.with_opengl
        tc.variables["MATPLOTPP_WITH_SYSTEM_NODESOUP"] = True
        tc.variables["MATPLOTPP_WITH_SYSTEM_CIMG"] = True
        tc.variables["MATPLOTPP_WITH_JPEG"] = self.options.with_jpeg
        tc.variables["MATPLOTPP_WITH_TIFF"] = self.options.with_tiff
        tc.variables["MATPLOTPP_WITH_ZLIB"] = self.options.with_zlib
        tc.variables["MATPLOTPP_WITH_PNG"] = self.options.with_png
        tc.variables["MATPLOTPP_WITH_FFTW"] = self.options.with_fftw
        tc.variables["MATPLOTPP_WITH_OPENCV"] = self.options.with_opencv
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        third_party_cmake = textwrap.dedent("""\
            find_package(nodesoup REQUIRED CONFIG)
            add_library(nodesoup INTERFACE)
            target_link_libraries(nodesoup INTERFACE nodesoup::nodesoup)
            get_target_property(NODESOUP_INC nodesoup::nodesoup INTERFACE_INCLUDE_DIRECTORIES)
            if(NODESOUP_INC)
                target_include_directories(nodesoup INTERFACE ${NODESOUP_INC})
            endif()

            find_package(CImg REQUIRED CONFIG)
            add_library(cimg INTERFACE)
            target_link_libraries(cimg INTERFACE cimg::cimg)
            target_compile_definitions(cimg INTERFACE cimg_display=0)
            get_target_property(CIMG_INC cimg::cimg INTERFACE_INCLUDE_DIRECTORIES)
            if(CIMG_INC)
                target_include_directories(cimg INTERFACE ${CIMG_INC})
            endif()

            if(MATPLOTPP_WITH_JPEG)
                find_package(JPEG REQUIRED)
                target_compile_definitions(cimg INTERFACE cimg_use_jpeg)
                target_link_libraries(cimg INTERFACE JPEG::JPEG)
            endif()

            if(MATPLOTPP_WITH_TIFF)
                find_package(TIFF REQUIRED)
                target_compile_definitions(cimg INTERFACE cimg_use_tiff)
                target_link_libraries(cimg INTERFACE TIFF::TIFF)
            endif()

            if(MATPLOTPP_WITH_ZLIB)
                find_package(ZLIB REQUIRED)
                target_compile_definitions(cimg INTERFACE cimg_use_zlib)
                target_link_libraries(cimg INTERFACE ZLIB::ZLIB)
            endif()

            if(MATPLOTPP_WITH_PNG)
                find_package(PNG REQUIRED)
                target_compile_definitions(cimg INTERFACE cimg_use_png)
                target_link_libraries(cimg INTERFACE PNG::PNG)
            endif()

            if(MATPLOTPP_WITH_FFTW)
                find_package(FFTW3 REQUIRED)
                target_compile_definitions(cimg INTERFACE cimg_use_fftw3)
                target_link_libraries(cimg INTERFACE FFTW3::fftw3)
            endif()

            if(MATPLOTPP_WITH_OPENCV)
                find_package(OpenCV REQUIRED)
                target_compile_definitions(cimg INTERFACE cimg_use_opencv)
                target_link_libraries(cimg INTERFACE ${OpenCV_LIBS})
            endif()

            install(TARGETS nodesoup cimg EXPORT Matplot++Targets)
        """)
        save(self, os.path.join(self.source_folder, "source", "3rd_party", "CMakeLists.txt"), third_party_cmake)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Matplot++")

        # Main matplot component
        self.cpp_info.components["matplot"].set_property("cmake_target_name", "Matplot++::matplot")
        self.cpp_info.components["matplot"].libs = ["matplot"]
        self.cpp_info.components["matplot"].requires = ["nodesoup::nodesoup", "cimg::cimg"]

        if self.options.with_opengl:
            self.cpp_info.components["matplot_opengl"].set_property("cmake_target_name", "Matplot++::matplot_opengl")
            self.cpp_info.components["matplot_opengl"].libs = ["matplot_opengl"]
            self.cpp_info.components["matplot_opengl"].requires = ["matplot", "opengl::opengl", "glfw::glfw", "glad::glad"]

        if self.options.with_jpeg:
            self.cpp_info.components["matplot"].requires.append("libjpeg::libjpeg")
        if self.options.with_tiff:
            self.cpp_info.components["matplot"].requires.append("libtiff::libtiff")
        if self.options.with_zlib:
            self.cpp_info.components["matplot"].requires.append("zlib::zlib")
        if self.options.with_png:
            self.cpp_info.components["matplot"].requires.append("libpng::libpng")
        if self.options.with_fftw:
            self.cpp_info.components["matplot"].requires.append("fftw::fftw")
        if self.options.with_opencv:
            self.cpp_info.components["matplot"].requires.append("opencv::opencv")

        self.output.info("matplotplusplus requires gnuplot (>= 5.2.6) installed on PATH at runtime for rendering.")

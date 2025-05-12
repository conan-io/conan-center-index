import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, save, rmdir, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LibCVDConan(ConanFile):
    name = "libcvd"
    description = "libCVD - efficient and easy-to-use C++ computer vision library"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/edrosten/libcvd"
    topics = ("computer-vision",)

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libjpeg": [False, "libjpeg", "libjpeg-turbo", "mozjpeg"],
        "with_libpng": [True, False],
        "with_libtiff": [True, False],
        "with_ffmpeg": [True, False],
        "with_libdc1394": [True, False],
        "with_opengl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libjpeg": "libjpeg",
        "with_libpng": True,
        "with_libtiff": True,
        # Build without video support by default
        "with_ffmpeg": False,
        "with_libdc1394": False,
        "with_opengl": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # OpenGL is always used on Windows
            del self.options.with_opengl

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # https://github.com/edrosten/libcvd/blob/main/cmake/CVDFindAllDeps.cmake
        # Used in a public header https://github.com/edrosten/libcvd/blob/RELEASE_2_5_0/cvd/canny.h#L4
        self.requires("toon/3.2", transitive_headers=True, transitive_libs=True)
        if self.options.with_ffmpeg:
            # FFMPEG v5.x+ are not supported
            self.requires("ffmpeg/4.4.4", transitive_libs=True)
        if self.options.with_libdc1394:
            # FIXME: libidc1394 seems to be missing raw1394 dependency
            # test_package fails with "undefined reference to `raw1394_new_handle'" etc
            self.requires("libdc1394/2.2.7")
        if self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.2")
        elif self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_libjpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")
        if self.options.with_libpng:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_libtiff:
            self.requires("libtiff/4.6.0")
        if self.options.get_safe("with_opengl", True):
            # https://github.com/edrosten/libcvd/blob/RELEASE_2_5_0/cvd/videodisplay.h#L18-L20
            self.requires("opengl/system", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CVD_ENABLE_TESTS"] = False
        tc.variables["CVD_ENABLE_PROGS"] = False
        tc.variables["CVD_ENABLE_EXAMPLES"] = False
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_ffmpeg"] = not self.options.with_ffmpeg
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_libdc1394"] = not self.options.with_libdc1394
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_JPEG"] = not self.options.with_libjpeg
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_PNG"] = not self.options.with_libpng
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_TIFF"] = not self.options.with_libtiff
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_OpenGL"] = not self.options.get_safe("with_opengl", True)
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_X11"] = not self.options.get_safe("with_opengl", True)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("ffmpeg", "cmake_file_name", "CVD_FFMPEG")
        deps.set_property("libdc1394", "cmake_file_name", "CVD_dc1394v2")
        deps.set_property("toon", "cmake_file_name", "CVD_TooN")
        deps.generate()

    def _patch_sources(self):
        # Use deps from Conan
        save(self, os.path.join(self.source_folder, "cmake", "CVDFindFFMPEG.cmake"),
             "find_package(CVD_FFMPEG REQUIRED)\n" if self.options.with_ffmpeg else "")
        save(self, os.path.join(self.source_folder, "cmake", "CVDFinddc1394v2.cmake"),
             "find_package(CVD_dc1394v2 REQUIRED)\n" if self.options.with_libdc1394 else "")
        save(self, os.path.join(self.source_folder, "cmake", "CVDFindTooN.cmake"),
            "set(CVD_TooN_FOUND FALSE)\n")

        # For debugging
        save(self, os.path.join(self.source_folder, "cmake", "CVDFindAllDeps.cmake"),
             '\nmessage(INFO "CVD_DEP_LIBS: ${CVD_DEP_LIBS}")\n', append=True)

        # Install DLL
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "install(TARGETS ${PROJECT_NAME} ARCHIVE DESTINATION lib LIBRARY DESTINATION lib)",
                        "install(TARGETS ${PROJECT_NAME} ARCHIVE DESTINATION lib LIBRARY DESTINATION lib RUNTIME DESTINATION bin)")


    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CVD")
        self.cpp_info.set_property("cmake_target_name", "cvd")
        self.cpp_info.set_property("cmake_find_mode", "both")

        postfix = "_debug" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["cvd" + postfix]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")

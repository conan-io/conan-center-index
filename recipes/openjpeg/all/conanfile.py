from conans import ConanFile, CMake, tools
import os
import glob


class OpenjpegConan(ConanFile):
    name = "openjpeg"
    url = "https://github.com/conan-io/conan-center-index"
    description = "OpenJPEG is an open-source JPEG 2000 codec written in C language."
    topics = ("conan", "jpeg2000", "jp2", "openjpeg", "image", "multimedia", "format", "graphics")
    options = {"shared": [True, False], "build_codec": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'build_codec': True, 'fPIC': True}
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    homepage = "https://github.com/uclouvain/openjpeg"
    license = "BSD 2-Clause"

    _source_subfolder = "source_subfolder"

    requires = (
        "zlib/1.2.11",
        "lcms/2.9",
        "libpng/1.6.37",
        "libtiff/4.0.9"
    )

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        # ensure that bundled cmake files are not used
        os.unlink(os.path.join(self._source_subfolder, 'cmake', 'FindLCMS.cmake'))
        os.unlink(os.path.join(self._source_subfolder, 'cmake', 'FindLCMS2.cmake'))

        # fix installing libs when only shared or static library built
        tools.replace_in_file(os.path.join(self._source_subfolder, 'src', 'lib', 'openjp2', 'CMakeLists.txt'),
                              'add_library(${OPENJPEG_LIBRARY_NAME} ${OPENJPEG_SRCS})',
                              'add_library(${OPENJPEG_LIBRARY_NAME} ${OPENJPEG_SRCS})\n'
                              'set(INSTALL_LIBS ${OPENJPEG_LIBRARY_NAME})')

        # cmake tries to find LCMS2 library with LCMS2 API that is packaged as lcms library
        # it should not be changed in conan-lcms because both lcms and lcms2 names are widespread
        tools.replace_in_file(os.path.join(self._source_subfolder, 'thirdparty', 'CMakeLists.txt'),
                              'find_package(LCMS2)',
                              'find_package(lcms)')
        tools.replace_in_file(os.path.join(self._source_subfolder, 'thirdparty', 'CMakeLists.txt'),
                              'if(LCMS2_FOUND)',
                              'if(lcms_FOUND)')
        tools.replace_in_file(os.path.join(self._source_subfolder, 'thirdparty', 'CMakeLists.txt'),
                              'set(LCMS_LIBNAME ${LCMS2_LIBRARIES} PARENT_SCOPE)',
                              'set(LCMS_LIBNAME ${lcms_LIBRARIES} PARENT_SCOPE)')
        tools.replace_in_file(os.path.join(self._source_subfolder, 'thirdparty', 'CMakeLists.txt'),
                              'set(LCMS_INCLUDE_DIRNAME ${LCMS2_INCLUDE_DIRS} PARENT_SCOPE)',
                              'set(LCMS_INCLUDE_DIRNAME ${lcms_INCLUDE_DIRS} PARENT_SCOPE)')

        # avoid always linking PNG
        tools.save(os.path.join(self._source_subfolder, 'thirdparty', 'CMakeLists.txt'),
                   'set(OPJ_HAVE_PNG_H 0 PARENT_SCOPE)\n' \
                   'set(OPJ_HAVE_LIBPNG 0 PARENT_SCOPE)\n' \
                   'set(PNG_LIBNAME "" PARENT_SCOPE)\n',
                   append=True)


        cmake = CMake(self)
        cmake.definitions['BUILD_SHARED_LIBS'] = self.options.shared
        cmake.definitions['BUILD_STATIC_LIBS'] = not self.options.shared
        cmake.definitions['BUILD_PKGCONFIG_FILES'] = False
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        # remove pkgconfig
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        # remove cmake
        for f in glob.glob(os.path.join(self.package_folder, 'lib',
                                        'openjpeg-%s.%s' % tuple(self.version.split('.')[0:2]),
                                        "*.cmake")):
            os.remove(f)

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join('include', 'openjpeg-%s.%s' % tuple(self.version.split('.')[0:2])))
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append('OPJ_STATIC')
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        self.cpp_info.name = 'OpenJPEG'

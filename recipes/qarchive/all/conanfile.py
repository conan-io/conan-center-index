import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
from textwrap import dedent

class qarchiveConan(ConanFile):
    name = "qarchive"
    license = "BSD-3-Clause"
    homepage = "https://antonyjr.in/QArchive/"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("QArchive is a cross-platform C++ library that modernizes libarchive ,\
                    This library helps you to extract and compress archives supported by libarchive")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, "fPIC": True}
    generators = "cmake", "cmake_find_package"
    topics = ("conan", "qt", "Qt", "compress", "libarchive")
    exports_sources = ["CMakeLists.txt"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        # TODO Remove this once Conan CCI build images have cmake 3.17 installed
        # This is safe since the minimum version was bumped only to have the LibArchive::LibArchive
        # target exposed by FindLibArchive, which was introduced in cmake 3.17.
        # Since we use conan's FindLibArchive we can revert the minimum version bump.
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "CMAKE_MINIMUM_REQUIRED( VERSION 3.17)",
            "CMAKE_MINIMUM_REQUIRED( VERSION 3.2)")

        # Remove CMAKE_CXX_FLAGS_DEBUG and CMAKE_CXX_FLAGS_RELEASE flags
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
            """set(CMAKE_CXX_FLAGS_DEBUG "-g")""",
            "")

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
            """set(CMAKE_CXX_FLAGS_RELEASE "-O3")""",
            "")

        # Use conan's qt
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "find_package(Qt5Core)",
            "find_package(qt REQUIRED COMPONENTS Core)")

        # TODO Once components support is available on qt, link only to qt::Core
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "target_link_libraries(QArchive PUBLIC Qt5::Core LibArchive::LibArchive)",
            "target_link_libraries(QArchive PUBLIC qt::qt LibArchive::LibArchive)")

        # Manually invoke MOC on QArchive sources since it doesn't get invoked automatically
        # when using conan's qt.
        old = '''\
            add_library(QArchive
            	    src/qarchivediskcompressor.cc
            	    src/qarchivediskextractor.cc
            	    src/qarchive_enums.cc
            	    src/qarchivediskcompressor_p.cc
            	    src/qarchivediskextractor_p.cc
            	    src/qarchiveutils_p.cc
            	    src/qarchiveioreader_p.cc
            	    include/qarchivediskcompressor.hpp
            	    include/qarchivediskextractor.hpp
            	    include/qarchive_enums.hpp
            	    include/qarchivediskcompressor_p.hpp
            	    include/qarchivediskextractor_p.hpp
            	    include/qarchiveutils_p.hpp
            	    include/qarchiveioreader_p.hpp
            	    include/qarchive_global.hpp
            	    )
            '''

        new = '''\
            set(SOURCES
            	src/qarchivediskcompressor.cc
            	src/qarchivediskextractor.cc
            	src/qarchive_enums.cc
            	src/qarchivediskcompressor_p.cc
            	src/qarchivediskextractor_p.cc
            	src/qarchiveutils_p.cc
            	src/qarchiveioreader_p.cc
            	include/qarchivediskcompressor.hpp
            	include/qarchivediskextractor.hpp
            	include/qarchive_enums.hpp
            	include/qarchivediskcompressor_p.hpp
            	include/qarchivediskextractor_p.hpp
            	include/qarchiveutils_p.hpp
            	include/qarchiveioreader_p.hpp
            	include/qarchive_global.hpp
                )

            qt5_wrap_cpp(SOURCES ${SOURCES})

            add_library(QArchive ${SOURCES})
            '''
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), dedent(old), dedent(new))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libarchive/3.4.0")
        self.requires("qt/5.15.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "QArchive-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "QArchive"
        self.cpp_info.names["cmake_find_package_multi"] = "QArchive"

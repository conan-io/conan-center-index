# TODO LIST
# - Make cmake a build requirement for conan-CI to work
# - Why are cmake_wrapper cmake files being deployed?
# - How can I utilise VTK's built-in cmake module dependency system, rather than recreate it here?
# - 3rd party deps are required for different enabled module configurations, how to take that info out of VTK's module system?
# - patching with src in local folder seems to fail - export_sources_folder = None?
# - use build/modules.json to compute the components and dependencies
#
# - how do i make one component depend on another (in cpp_info), ie i'm attaching the custom-cmake-module to all of the components, but technically it should only be connected to the "common" one.
#   BUT, logically it is a bit weird, because WHICH "common" module (VTK::Common or VTK::CommonCore) depends on VTK_ENABLE_KITS,
#   which is what i'm trying to attach and export.
# So I need some kind of general component that the user could import, to determine which modules they further need to import?
#
# freetype_MAJOR_VERSION or whatever it was... proj?
# SpaceIm: CMakeDeps creates a config version file for each dependency, so if find_package(<package>) is resolved, it will define <package>_VERSION

# RECIPE MAINTAINER NOTES:
# Read vtk's Documentation/release/9.1.md for important notes about versions and forks
# Also read vtk's Documentation/build.md for information about build settings and flags

import os
import textwrap
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake
from conan.tools.files import apply_conandata_patches
from conan.tools.system.package_manager import Apt
from conans.tools import get, remove_files_by_mask, save

_support_old_ci_20220514 = True

if _support_old_ci_20220514:
    # not yet supported by current CI (2022-05-14)
    from conans.tools import rmdir
else:
    # new stuff!
    from conan.tools.files import rmdir


class VtkConan(ConanFile):
    name = "vtk"
    settings = "os", "compiler", "build_type", "arch"
    description = "The Visualization Toolkit (VTK) by Kitware is an open-source, \
        freely available software system for 3D computer graphics, \
        image processing, and visualization."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.vtk.org/"
    license = "BSD-3-Clause"
    topics = ("vtk", "scientific", "image", "processing", "visualization")

    short_paths = True
    no_copy_source = True

    generators = "CMakeDeps"

    exports = ["CMakeLists.txt"]
    exports_sources = "patches/**"

    # Alternative method: can use git directly - helpful when hacking VTK
    # TODO allow user to set the git_url from the command line, during conan install
    # git_url = "https://gitlab.kitware.com/vtk/vtk.git"
    git_url = "/build/git-mirrors/vtk.git"


    ############
    # list of all possible 3rd parties (as of 9.1.0)
    # with each one marked as where they should come from.
    #
    # cgns:             TODO
    # cli11:            TODO
    # diy2:             TODO
    # doubleconversion: conan (double-conversion)
    # eigen:            conan (eigen)
    # exodusII:         TODO
    # expat:            TODO
    # exprtk:           conan (exprtk)
    # fides:            TODO
    # fmt:              conan (fmt)
    # freetype:         conan (freetype)
    # gl2ps:            internal (not available in CCI - TODO)
    # glew:             conan (glew)
    # h5part:           TODO
    # hdf5:             conan (hdf5) - TODO requires MPI and other things
    # ioss:             TODO
    # jpeg:             TODO
    # jsoncpp:          conan (jsoncpp)
    # kissfft:          TODO
    # libharu:          TODO
    # libproj:          conan (proj)
    # libxml2:          TODO
    # loguru:           TODO
    # lz4:              conan (lz4)
    # lzma:             conan (xz_utils)
    # mpi4py:           TODO
    # netcdf:           TODO
    # ogg:              TODO
    # pegtl:            TODO
    # png:              TODO
    # pugixml:          conan (pugixml)
    # sqlite:           conan (sqlite3)
    # theora:           TODO
    # tiff:             TODO
    # utf8:             conan (utfcpp)
    # verdict:          TODO
    # vpic:             TODO
    # vtkm:             TODO
    # xdmf2:            TODO
    # xdmf3:            TODO
    # zfp:              TODO
    # zlib:             conan
    #
    ############

    options = {
              "shared": [True, False]
            , "fPIC": [True, False]

            , "enable_kits": [True, False]     # VTK_ENABLE_KITS - smaller set of libraries - ONLY for shared mode

            , "use_source_from_git": [True, False]

            , "use_64bit_ids": ["Auto", True, False]

            , "qt_version": ["Auto", "5", "6"]
            , "qt":      [True, False]
            , "qtquick": [True, False]
            , "qtsql":   [True, False]

            # TODO , "imaging":    [True, False]
            # TODO , "mpi":        [True, False]
            , "rendering":  [True, False]
            # TODO , "standAlone": [True, False]
            # TODO , "views":      [True, False]
            # TODO , "web":        [True, False]

            # I don't use these so I can't make these ones below
            # , "mpi": [True, False]
            # , "minimal": [True, False]
            # , "ioxml": [True, False]
            # , "mpi_minimal": [True, False]
            }

    default_options = {
              "shared": False
            , "fPIC": True

            , "use_source_from_git": False # use the tarball

            , "use_64bit_ids": "Auto" # TODO normally 32 bit on 32 bit platforms

            , "enable_kits": False

            , "qt_version": "Auto"
            , "qt": False
            , "qtquick": False
            , "qtsql": False

            # TODO , "imaging":    False
            # TODO , "mpi":        False
            , "rendering":  False
            # TODO , "standAlone": False
            # TODO , "views":      False
            # TODO , "web":        False

            # TODO try supporting more modules, I chose hdf5 randomly...
            # HDF5 requires 'parallel' to be enabled, which also brings in the MPI requirements.
            # HDF5 is expected to have "parallel" enabled
            # , "hdf5:parallel":   True
            # , "hdf5:enable_cxx": False  # can't be enabled with parallel

            # I don't use these so I can't make these ones below
            # , "mpi": False
            # , "minimal": False
            # , "ioxml": False
            # , "mpi_minimal": False
            }


    @property
    def _source_subfolder(self):
        return "source_subfolder"



    def _patch_source(self):
        # Note that VTK's cmake will insert its own CMAKE_MODULE_PATH at the
        # front of the list.  This is ok as long as there is nothing in that
        # path that will be found before our conan cmake files...
        # That is why we delete the third party finders.
        # Else, we have to patch VTK's CMakeLists.txt, like so:
        #####
        # diff --git a/CMakeLists.txt b/CMakeLists.txt
        # index c15890cfdc..022f704d75 100644
        # --- a/CMakeLists.txt
        # +++ b/CMakeLists.txt
        # @@ -7,7 +7,7 @@ if (POLICY CMP0127)
        #  endif ()
        #
        #  set(vtk_cmake_dir "${VTK_SOURCE_DIR}/CMake")
        # -list(INSERT CMAKE_MODULE_PATH 0 "${vtk_cmake_dir}")
        # +list(APPEND CMAKE_MODULE_PATH "${vtk_cmake_dir}")
        #####

        # DELETE any of the third party finders, before we build - see note above
        remove_files_by_mask(os.path.join(self._source_subfolder,"CMake"), "Find*.cmake")

        # Delete VTK's cmake patches (these support older cmake programs).
        # We do not have to support old cmake: we require an updated cmake instead.
        if _support_old_ci_20220514:
            rmdir(os.path.join(self._source_subfolder,"CMake","patches"))
        else:
            rmdir(self, os.path.join(self._source_subfolder,"CMake","patches"))

        # And apply our patches.  I do it here rather than in build, so I can repeatedly call build without applying patches.
        apply_conandata_patches(self)



    def source(self):
        if self.options.use_source_from_git:
            self.run("git clone -b release --single-branch " + self.git_url + " " + self._source_subfolder)
            # note: we give the branch a name so we don't have detached heads
            # TODO change to standard git and python chdir
            git_hash = "v" + self.version
            self.run("cd " + self._source_subfolder + " && git checkout -b branch-" + git_hash + " " + git_hash)
        else:
            get(**self.conan_data["sources"][self.version],
                    strip_root=True,
                    destination=self._source_subfolder,
                    )

        if self.no_copy_source:
            self._patch_source()


    def _third_party(self):
        parties = {
                # LEFT field:  target name for linking, will be used as TARGET::TARGET in package_info()
                # RIGHT field: package/version to require
                  "double-conversion": "double-conversion/3.2.0"
                , "eigen":             "eigen/3.4.0"
                , "exprtk":            "exprtk/0.0.1"
                , "fmt":               "fmt/8.1.1"       # 9.1.0 release docs mention a PR - confirmed merged 8.1.0
                , "freetype":          "freetype/2.11.1" # ... what? ... WORKED with 2022-05-06-freetype
                , "glew":              "glew/2.2.0"
                , "jsoncpp":           "jsoncpp/1.9.5"
                # , "libharu": "libharu/2.3.0" -- use VTK's bundled version - heavily patched
                , "lz4":               "lz4/1.9.3"
                , "proj":              "proj/9.0.0" # if MAJOR version changes, update ThirdParty/libproj/CMakeLists.txt
                , "pugixml":           "pugixml/1.12.1"
                , "sqlite3":           "sqlite3/3.38.1"
                , "utfcpp":            "utfcpp/3.2.1"
                , "xz_utils":          "xz_utils/5.2.5" # VTK calls this lzma
                }

        # TODO figure out how we want to support modules...
        # VTK already has an extensive module system, we would want to mirror or use it
        # if self.options.module_hdf5:
        # parties["hdf5"] = "hdf5/1.12.1"

        if self.options.qt:
            parties["qt"] = "qt/6.2.4"

            # NOTE: could also try QT's offical QT
            # self.requires("qtbase/6.2.4@qt/everywhere")

        return parties


    def requirements(self):
        for pack in self._third_party().values():
            self.requires(pack)


    def build_requirements(self):
        # Check the CMake/patches folder, and use the most recent cmake
        # that matches the largest major version in the list.
        # That should be the last cmake that was tested by VTK.
        self.build_requires("cmake/3.22.4")

        if self.options.rendering:
            Apt(self).install([
                "build-essential",
                "mesa-common-dev",
                "mesa-utils",
                "freeglut3-dev"

                # These were listed by the previous recipe author,
                # but they are not listed in vtk Documentation/dev/build.md
                # so I'm not sure if they are really needed ... TODO
                #
                # "mesa-utils-extra",
                # "libgl1-mesa-dev",
                # "libglapi-mesa",
                # "libsm-dev",
                # "libx11-dev",
                # "libxext-dev",
                # "libxt-dev",
                # "libglu1-mesa-dev"
                ])
            # TODO people on other platforms please
            # contribute what packages are required


    def validate(self):
        if not self.options.shared and self.options.enable_kits:
            raise ConanInvalidConfiguration("KITS can only be enabled with shared")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC


    def configure(self):
        if self.options.shared:
            del self.options.fPIC


    def generate(self):
        tc = CMakeToolchain(self)

        # 64 / 32 bit IDs
        if self.options.use_64bit_ids != "Auto":
            tc.variables["VTK_USE_64BIT_IDS"] = self.options.use_64bit_ids

        # Be sure to set this, otherwise vtkCompilerChecks.cmake will downgrade our CXX standard to 11
        tc.variables["VTK_IGNORE_CMAKE_CXX11_CHECKS"] = "ON"


        # no need for versions on installed names?
        tc.variables["VTK_VERSIONED_INSTALL"] = "OFF"

        # Needed or not? Nothing gets installed without this ON at the moment.
        # tc.variables["VTK_INSTALL_SDK"] = "OFF"

        # TODO future-proofing
        # tc.variables["VTK_LEGACY_REMOVE"] = "ON" # disable legacy APIs
        # tc.variables["VTK_USE_FUTURE_CONST"] = "ON" # use the newer const-correct APIs

        # TODO development debugging
        # tc.variables["VTK_DEBUG_LEAKS"] = "ON" # use the newer const-correct APIs


        # ON or OFF
        tc.variables["BUILD_TESTING"] = "OFF"
        tc.variables["BUILD_EXAMPLES"] = "OFF"
        tc.variables["BUILD_DOCUMENTATION"] = "OFF"

        # Enable KITs - Quote: "Compiles VTK into a smaller set of libraries."
        # Quote: "Can be useful on platforms where VTK takes a long time to launch due to expensive disk access."
        tc.variables["VTK_ENABLE_KITS"] = "ON" if self.options.enable_kits else "OFF"


        #### CUDA / MPI / MEMKIND ####
        # ON or OFF
        tc.variables["VTK_USE_CUDA"]    = "OFF"
        tc.variables["VTK_USE_MEMKIND"] = "OFF"
        tc.variables["VTK_USE_MPI"]     = "OFF"


        # There are LOTS of these modules now ...
        # for vtkModule in self.required_modules:
            # tc.variables["VTK_MODULE_ENABLE_VTK_" + vtkModule] = "YES" or NO or WANT or DONT_WANT

        # TODO support more modules - see notes above re hdf5
        # tc.variables["VTK_MODULE_ENABLE_VTK_hdf5"] = "YES" # or NO or WANT or DONT_WANT

        # https://gitlab.kitware.com/vtk/vtk/-/blob/master/Documentation/dev/build.md
        # TODO try VTK_USE_VIDEO_FOR_WINDOWS   for video capture
        # TODO try VTK_USE_VIDEO_FOR_WINDOWS_CAPTURE   for video capture
        # TODO try VTK_USE_MICROSOFT_MEDIA_FOUNDATION   for video capture (MP4)


        # groups can be:  DEFAULT   DONT_WANT   WANT   YES   NO
        # Note that YES is like WANT, but will show errors if can't make everything
        # NO is also more forceful than DONT_WANT
        # Default is DONT_WANT, let it auto-enable when required
        tc.variables["VTK_GROUP_ENABLE_Imaging"]    = "DONT_WANT"   # TODO add option
        tc.variables["VTK_GROUP_ENABLE_MPI"]        = "DONT_WANT"   # TODO add option
        tc.variables["VTK_GROUP_ENABLE_Rendering"]  = "YES" if self.options.rendering else "DONT_WANT"
        tc.variables["VTK_GROUP_ENABLE_StandAlone"] = "DONT_WANT"   # TODO add option
        tc.variables["VTK_GROUP_ENABLE_Views"]      = "DONT_WANT"   # TODO add option
        tc.variables["VTK_GROUP_ENABLE_Web"]        = "DONT_WANT"   # TODO add option

        # for QT, use the more specific MODULE options below
        tc.variables["VTK_GROUP_ENABLE_Qt"] = "DONT_WANT"


        ##### QT ######
        # QT has a few modules, we'll be specific
        tc.variables["VTK_QT_VERSION"] = self.options.qt_version
        tc.variables["VTK_MODULE_ENABLE_VTK_GUISupportQt"]      = "YES" if self.options.qt else "DONT_WANT"
        tc.variables["VTK_MODULE_ENABLE_VTK_GUISupportQtQuick"] = "YES" if self.options.qtquick else "DONT_WANT"
        tc.variables["VTK_MODULE_ENABLE_VTK_GUISupportQtSQL"]   = "YES" if self.options.qtsql else "DONT_WANT"

        ##### SMP parallelism ####  Sequential  STDThread  OpenMP  TBB
        # Note that STDThread seems to be available by default
        tc.variables["VTK_SMP_IMPLEMENTATION_TYPE"] = "Sequential"
        # Change change the mode during runtime, if you enable the backends like so:
        # tc.variables["VTK_SMP_ENABLE_<backend_name>"] = "ON"

        # TODO OLD STUFF that was here before, I don't use or know much about
        # if self.options.minimal:
        #     tc.variables["VTK_Group_StandAlone"] = "OFF"
        #     tc.variables["VTK_Group_Rendering"] = "OFF"
        # if self.options.ioxml:
        #     tc.variables["Module_vtkIOXML"] = "ON"
        # if self.options.mpi:
        #     tc.variables["VTK_Group_MPI"] = "ON"
        #     tc.variables["Module_vtkIOParallelXML"] = "ON"
        # if self.options.mpi_minimal:
        #     tc.variables["Module_vtkIOParallelXML"] = "ON"
        #     tc.variables["Module_vtkParallelMPI"] = "ON"
        #
        # if self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio":
        #     tc.variables["CMAKE_DEBUG_POSTFIX"] = "_d"


        #### Use the Internal VTK bundled libraries for these Third Party dependencies ...
        # Ask VTK to use their bundled versions for these:
        #
        # VTK uses a heavily-forked version they call 2.4.0.  Upstream libharu is currently unmaintained.
        tc.variables["VTK_MODULE_USE_EXTERNAL_VTK_libharu"] = "OFF"
        #
        # CCI does not have gl2ps yet.  Note that cern-root is also waiting for gl2ps.
        tc.variables["VTK_MODULE_USE_EXTERNAL_VTK_gl2ps"] = "OFF"
        #
        ###


        # Everything else should come from conan.
        # TODO check if anything is coming from the system CMake,
        # and change it to conan or add as a build_requirement for the system to install.
        # SOME of VTK's bundled Third Party libs are heavily forked and patched, so system versions may
        # not be appropriate to use externally (like libharu).
        tc.variables["VTK_USE_EXTERNAL"] = "ON"

        tc.generate()


    def build(self):
        if not self.no_copy_source:
            self._patch_source()

        cmake = CMake(self)
        cmake.configure()
        cmake.build()


    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "vtk", "conan-official-{}-variables.cmake".format(self.name))


    def package(self):
        self.copy("Copyright.txt", dst="licenses", src=self._source_subfolder)
        # TODO there are more licences for the bundled third party libs

        cmake = CMake(self)
        cmake.install()

        # create a cmake file with our special variables
        content = textwrap.dedent("""\
                set (VTK_ENABLE_KITS {})
                """
                .format("ON" if self.options.enable_kits else "OFF")
                )
        save(os.path.join(self.package_folder, self._module_file_rel_path),
                content
                )


    def package_info(self):
###         self.cpp_info.libs = tools.collect_libs(self)
#        if self.settings.os == "Linux":
#            self.cpp_info.system_libs += ["dl","pthread"]

        # this is still required as vtk files include themselves as <vtkCommand.h>,
        # and it can't seem to find itself in the same dir when included with <>
###         self.cpp_info.includedirs = [ "include/vtk" ] # no short_version as we disabled versioning

#            "include/vtk-%s" % self.short_version,
#            # dont know why these were in here ... "include/vtk-%s/vtknetcdf/include" % self.short_version,
#            # dont know why these were in here ... "include/vtk-%s/vtknetcdfcpp" % self.short_version
#        ]

        # self.cpp_info.names["cmake_find_package"] = "VTK"
        # self.cpp_info.names["cmake_find_package_multi"] = "VTK"

        # needed?
        # self.cpp_info.set_property("cmake_target_name", "VTK::VTK")
        # self.cpp_info.set_property("cmake_module_target_name", "VTK::VTK")


        # TRY WITHOUT ... self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "VTK")

        # needed? self.cpp_info.set_property("cmake_module_file_name", "vtk")

        self.cpp_info.names["cmake_find_package"] = "VTK"
        self.cpp_info.names["cmake_find_package_multi"] = "VTK"

        components = []

        # these component lists are cheating by me,
        # just copy-paste all the .so files in here, chop off the start and end of filenames
        # TODO use modules.json

        # for shared AND KITs (can't be unshared and kits)
        if self.options.shared and self.options.enable_kits:

            if not self.options.rendering:
                # base components
                components += [
                        "kissfft",
                        "loguru",
                        "sys",
                        "WrappingTools",

                        "Common",
                        ]

            else:   # with Rendering
                if not self.options.qt:
                    components += [
                            "ChartsCore",
                            "Common",
                            "DICOMParser",
                            "DomainsChemistry",
                            "DomainsChemistryOpenGL2",
                            "Filters",
                            "FiltersHybrid",
                            "GeovisCore",
                            "gl2ps",
                            "Imaging",
                            "ImagingHybrid",
                            "InfovisCore",
                            "InfovisLayout",
                            "Interaction",
                            "IO",
                            "IOExportGL2PS",
                            "IOExportPDF",
                            "kissfft",
                            "libharu",
                            "loguru",
                            "metaio",
                            "OpenGL",
                            "Parallel",
                            "Rendering",
                            "RenderingGL2PSOpenGL2",
                            "RenderingUI",
                            "RenderingVtkJS",
                            "sys",
                            "TestingRendering",
                            "Views",
                            "ViewsInfovis",
                            "WrappingTools",
                            ]
                else:   # with QT
                    components += [
                            "ChartsCore",
                            "Common",
                            "DICOMParser",
                            "DomainsChemistryOpenGL2",
                            "DomainsChemistry",
                            "FiltersHybrid",
                            "Filters",
                            "GeovisCore",
                            "gl2ps",
                            "GUISupportQt",
                            "ImagingHybrid",
                            "Imaging",
                            "InfovisCore",
                            "InfovisLayout",
                            "Interaction",
                            "IOExportGL2PS",
                            "IOExportPDF",
                            "IO",
                            "kissfft",
                            "libharu",
                            "loguru",
                            "metaio",
                            "OpenGL",
                            "Parallel",
                            "RenderingGL2PSOpenGL2",
                            "Rendering",
                            "RenderingUI",
                            "RenderingVtkJS",
                            "sys",
                            "TestingRendering",
                            "ViewsInfovis",
                            "Views",
                            "WrappingTools",
                            ]

        else: # not kits, many more libraries

            if not self.options.rendering:
                components += [
                        "kissfft",
                        "loguru",
                        "sys",
                        "WrappingTools",

                        "CommonCore",
                        "CommonDataModel",
                        "CommonMath",
                        "CommonMisc",
                        "CommonSystem",
                        "CommonTransforms",
                        ]
            else:   # with Rendering
                # just copy-paste all the .so files in here, chop off the start and end of filenames
                if not self.options.qt:
                    components += [
                            "ChartsCore",
                            "CommonColor",
                            "CommonComputationalGeometry",
                            "CommonCore",
                            "CommonDataModel",
                            "CommonExecutionModel",
                            "CommonMath",
                            "CommonMisc",
                            "CommonSystem",
                            "CommonTransforms",
                            "DICOMParser",
                            "DomainsChemistryOpenGL2",
                            "DomainsChemistry",
                            "FiltersCore",
                            "FiltersExtraction",
                            "FiltersGeneral",
                            "FiltersGeometry",
                            "FiltersHybrid",
                            "FiltersImaging",
                            "FiltersModeling",
                            "FiltersSources",
                            "FiltersStatistics",
                            "FiltersTexture",
                            "GeovisCore",
                            "gl2ps",
                            "ImagingColor",
                            "ImagingCore",
                            "ImagingGeneral",
                            "ImagingHybrid",
                            "ImagingMath",
                            "ImagingSources",
                            "InfovisCore",
                            "InfovisLayout",
                            "InteractionImage",
                            "InteractionStyle",
                            "InteractionWidgets",
                            "IOCore",
                            "IOExportGL2PS",
                            "IOExportPDF",
                            "IOExport",
                            "IOGeometry",
                            "IOImage",
                            "IOLegacy",
                            "IOXMLParser",
                            "IOXML",
                            "kissfft",
                            "libharu",
                            "loguru",
                            "metaio",
                            "ParallelCore",
                            "ParallelDIY",
                            "RenderingAnnotation",
                            "RenderingContext2D",
                            "RenderingContextOpenGL2",
                            "RenderingCore",
                            "RenderingFreeType",
                            "RenderingGL2PSOpenGL2",
                            "RenderingImage",
                            "RenderingLabel",
                            "RenderingLOD",
                            "RenderingOpenGL2",
                            "RenderingSceneGraph",
                            "RenderingUI",
                            "RenderingVolumeOpenGL2",
                            "RenderingVolume",
                            "RenderingVtkJS",
                            "sys",
                            "TestingRendering",
                            "ViewsCore",
                            "ViewsInfovis",
                            "WrappingTools",
                            ]
                else:   # with QT
                    components += [
                            "ChartsCore",
                            "CommonColor",
                            "CommonComputationalGeometry",
                            "CommonCore",
                            "CommonDataModel",
                            "CommonExecutionModel",
                            "CommonMath",
                            "CommonMisc",
                            "CommonSystem",
                            "CommonTransforms",
                            "DICOMParser",
                            "DomainsChemistryOpenGL2",
                            "DomainsChemistry",
                            "FiltersCore",
                            "FiltersExtraction",
                            "FiltersGeneral",
                            "FiltersGeometry",
                            "FiltersHybrid",
                            "FiltersImaging",
                            "FiltersModeling",
                            "FiltersSources",
                            "FiltersStatistics",
                            "FiltersTexture",
                            "GeovisCore",
                            "gl2ps",
                            "GUISupportQt",
                            "ImagingColor",
                            "ImagingCore",
                            "ImagingGeneral",
                            "ImagingHybrid",
                            "ImagingMath",
                            "ImagingSources",
                            "InfovisCore",
                            "InfovisLayout",
                            "InteractionImage",
                            "InteractionStyle",
                            "InteractionWidgets",
                            "IOCore",
                            "IOExportGL2PS",
                            "IOExportPDF",
                            "IOExport",
                            "IOGeometry",
                            "IOImage",
                            "IOLegacy",
                            "IOXMLParser",
                            "IOXML",
                            "kissfft",
                            "libharu",
                            "loguru",
                            "metaio",
                            "ParallelCore",
                            "ParallelDIY",
                            "RenderingAnnotation",
                            "RenderingContext2D",
                            "RenderingContextOpenGL2",
                            "RenderingCore",
                            "RenderingFreeType",
                            "RenderingGL2PSOpenGL2",
                            "RenderingImage",
                            "RenderingLabel",
                            "RenderingLOD",
                            "RenderingOpenGL2",
                            "RenderingSceneGraph",
                            "RenderingUI",
                            "RenderingVolumeOpenGL2",
                            "RenderingVolume",
                            "RenderingVtkJS",
                            "sys",
                            "TestingRendering",
                            "ViewsCore",
                            "ViewsInfovis",
                            "WrappingTools",
                            ]


# all components, from a list somewhere, for reference
# "CommonColor",
# "CommonComputationalGeometry",
# "CommonCore",
# "CommonDataModel",
# "CommonExecutionModel",
# "CommonMath",
# "CommonMisc",
# "CommonSystem",
# "CommonTransforms",
# "DICOMParser",
# "FiltersCore",
# "FiltersExtraction",
# "FiltersGeneral",
# "FiltersGeometry",
# "FiltersHybrid",
# "FiltersModeling",
# "FiltersSources",
# "FiltersStatistics",
# "FiltersTexture",
# "GUISupportQt",
# "ImagingColor",
# "ImagingCore",
# "ImagingGeneral",
# "ImagingHybrid",
# "ImagingSources",
# "InteractionStyle",
# "InteractionWidgets",
# "IOCore",
# "IOImage",
# "IOLegacy",
# "IOXML",
# "IOXMLParser",
# "metaio",
# "ParallelCore",
# "ParallelDIY",
# "RenderingAnnotation",
# "RenderingContext2D",
# "RenderingCore",
# "RenderingFreeType",
# "RenderingOpenGL2",
# "RenderingUI",
# "RenderingVolume",


        # remove duplicates in components list
        components = list(set(components))

        # Note: I don't currently import the explicit dependency list for each component from VTK,
        # so every module will depend on "everything" external, and there are no internal dependencies.
        # Consumers just have to figure out what they have to link.

        # get keys as a list and make a list of target::target
        all_targets = [k + "::" + k for k in self._third_party().keys()]

        # all modules use the same include dir,
        # and note we aren't using include/vtk-9
        # no short_version in path, as we disabled versioning
        vtk_include_dirs   = [os.path.join("include", "vtk")]

        # all modules use the same cmake dir too
        vtk_cmake_dirs = [os.path.join("lib","cmake","vtk")]

        for comp in components:
            self.cpp_info.components[comp].set_property("cmake_target_name", "VTK::" + comp)
            self.cpp_info.components[comp].libs          = ["vtk" + comp]
            self.cpp_info.components[comp].includedirs   = vtk_include_dirs
            self.cpp_info.components[comp].builddirs     = vtk_cmake_dirs
            self.cpp_info.components[comp].build_modules = vtk_cmake_dirs
            self.cpp_info.components[comp].requires      = all_targets
            self.cpp_info.components[comp].set_property("cmake_build_modules", [self._module_file_rel_path])


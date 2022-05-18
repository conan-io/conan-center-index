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
# - Read vtk's Documentation/release/9.1.md for important notes about versions and forks
# - Also read vtk's Documentation/build.md for information about build settings and flags
# - Modify build_requirements() to match the version of CMake that VTK tested with that release.

import os
import textwrap
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import apply_conandata_patches
from conan.tools.system.package_manager import Apt
from conans.errors import ConanInvalidConfiguration

# TODO upgrade to new conan.* imports
from conans.tools import get, remove_files_by_mask, save, rmdir, rename, collect_libs, check_min_cppstd, Version

# Enable to keep VTK-generated cmake files, to check contents
_debug_packaging = False


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
    no_copy_source = False

    generators = "CMakeDeps"

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
    # expat:            conan (expat)
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
    # libharu:          VTK (heavily patched)
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
    # theora:           conan (theora)
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
            "shared": [True, False],
            "fPIC": [True, False],

            "use_source_from_git": [True, False],

            ### Debugging / future proofing ###
            "legacy_remove":    [True, False],
            "legacy_silent":    [True, False],
            "use_future_const": [True, False],
            "debug_leaks":      [True, False],

            ### Compile options ###
            "use_64bit_ids": ["Auto", True, False], # default: 32 bit on 32 bit platforms.  64 on 64 bit platforms.
            "enable_kits":   [True, False],         # VTK_ENABLE_KITS - smaller set of libraries - ONLY for shared mode
            "enable_logging": [True, False],

            ### Wrapping support ###
            "enable_wrapping": [True, False],
            "wrap_java":       [True, False],
            "wrap_python":     [True, False],
            "use_tk":          [True, False],   # requires wrap_python

            ### Advanced tech ###
            "use_cuda":    [True, False],
            "use_memkind": [True, False],
            "use_mpi":     [True, False],

            ### SMP ###
            "smp_implementation_type": ["Sequential", "STDThread", "OpenMP", "TBB"],
            "smp_enable_Sequential":   [True, False],
            "smp_enable_STDThread":    [True, False],
            "smp_enable_OpenMP":       [True, False],
            "smp_enable_TBB":          [True, False],

            ### Modules ###
            "build_all_modules": [True, False],     # The big one, build everything - good for pre-built CCI

            # Groups of modules
            "group_enable_Qt":         [True, False],   # can set to False, and use modules for enabling parts of Qt support
            "group_enable_Imaging":    [True, False],
            "group_enable_MPI":        [True, False],
            "group_enable_Rendering":  [True, False],
            "group_enable_StandAlone": [True, False],
            "group_enable_Views":      [True, False],
            "group_enable_Web":        [True, False],

            # Qt-specific modules
            "qt_version": ["Auto", "5", "6"],
            "module_enable_GUISupportQt":      [True, False],
            "module_enable_GUISupportQtQuick": [True, False],
            "module_enable_GUISupportQtSQL":   [True, False],
            "module_enable_RenderingQt":       [True, False],
            "module_enable_ViewsQt":           [True, False],
            }

    default_options = {
            "shared": False,
            "fPIC": True,

            "use_source_from_git": False, # False = use the tarball

            ### Debugging / future proofing ###
            "legacy_remove":    False,
            "legacy_silent":    False,
            "use_future_const": False,
            "debug_leaks":      False,

            ### Compile options ###
            "use_64bit_ids":   "Auto",
            "enable_kits":     False,
            "enable_logging":  False,

            ### Wrapping support ###
            "enable_wrapping": False,
            "wrap_java":       False,
            "wrap_python":     False,
            "use_tk":          False,

            ### Advanced tech ###
            "use_cuda":    False,
            "use_memkind": False,
            "use_mpi":     False,

            ### SMP ###
            "smp_implementation_type": "Sequential",
            "smp_enable_Sequential":   False,
            "smp_enable_STDThread":    False,
            "smp_enable_OpenMP":       False,
            "smp_enable_TBB":          False,

            ### Modules ###
            "build_all_modules":       False, # TODO - not read yet... True, # disable to pick+choose modules

            # Groups of modules
            "group_enable_Imaging":    False,
            "group_enable_MPI":        False,
            "group_enable_Rendering":  False,
            "group_enable_StandAlone": False,
            "group_enable_Views":      False,
            "group_enable_Web":        False,

            # Qt-specific modules
            "qt_version":                      "Auto",
            "group_enable_Qt":                 False,   # can keep this false, enable specific QT modules
            "module_enable_GUISupportQt":      False,
            "module_enable_GUISupportQtQuick": False,
            "module_enable_GUISupportQtSQL":   False,
            "module_enable_RenderingQt":       False,
            "module_enable_ViewsQt":           False,

            # TODO try supporting more modules
            # I chose hdf5 randomly...
            # HDF5 requires 'parallel' to be enabledwhich also brings in the MPI requirements.
            # HDF5 is expected to have "parallel" enabled
            # "hdf5:parallel":   True,
            # "hdf5:enable_cxx": False,  # can't be enabled with parallel
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
# ALLOW FINDERS #        remove_files_by_mask(os.path.join(self._source_subfolder,"CMake"), "Find*.cmake")

        # Delete VTK's cmake patches (these support older cmake programs).
        # We do not have to support old cmake: we require an updated cmake instead.
# ALLOW FINDERS #        if _support_old_ci_20220514:
# ALLOW FINDERS #            rmdir(os.path.join(self._source_subfolder,"CMake","patches"))
# ALLOW FINDERS #        else:
# ALLOW FINDERS #            rmdir(self, os.path.join(self._source_subfolder,"CMake","patches"))

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
                    destination=self._source_subfolder)

        if self.no_copy_source:
            self._patch_source()


    def _third_party(self):
        parties = {
                # LEFT field:  target name for linking, will be used as TARGET::TARGET in package_info()
                # RIGHT field: package/version to require
                "double-conversion": "double-conversion/3.2.0",
                "eigen":             "eigen/3.4.0",
                "expat":             "expat/2.4.8",
                "exprtk":            "exprtk/0.0.1",
                "fmt":               "fmt/8.1.1",      # 9.1.0 release docs mention a PR - confirmed merged 8.1.0
                "freetype":          "freetype/2.11.1",
                "glew":              "glew/2.2.0",
                "jsoncpp":           "jsoncpp/1.9.5",
                # "libharu": "libharu/2.3.0", -- use VTK's bundled version - heavily patched
                "lz4":               "lz4/1.9.3",
                "proj":              "proj/9.0.0", # if MAJOR version changes, update ThirdParty/libproj/CMakeLists.txt
                "pugixml":           "pugixml/1.12.1",
                "sqlite3":           "sqlite3/3.38.1",
                "utfcpp":            "utfcpp/3.2.1",
                "xz_utils":          "xz_utils/5.2.5", # note: VTK calls this lzma
                }

        if self.options.group_enable_StandAlone:
            parties["hdf5"] = "hdf5/1.12.1"
            parties["theora"] = "theora/1.1.1"

        # TODO figure out how we want to support modules...
        # VTK already has an extensive module system, we would want to mirror or use it
        # if self.options.module_hdf5:
        # parties["hdf5"] = "hdf5/1.12.1"

        if (self.options.group_enable_Qt
                or self.options.module_enable_GUISupportQt
                or self.options.module_enable_GUISupportQtQuick
                or self.options.module_enable_GUISupportQtSQL
                or self.options.module_enable_RenderingQt
                or self.options.module_enable_ViewsQt):
            parties["qt"] = "qt/6.2.4"

            # NOTE: could also try QT's offical QT
            # self.requires("qtbase/6.2.4@qt/everywhere")

        return parties


    def requirements(self):
        if self.options.group_enable_Rendering:
            self.requires("opengl/system")
            self.requires("xorg/system")

        for pack in self._third_party().values():
            self.requires(pack)

        # cmake requires an older openssl than libcurl, so override here
        self.requires("openssl/1.1.1o", override=True)

        # HACK TODO working around a dependency bug in conan
        self.requires("cmake/3.22.4")


    def build_requirements(self):
        # Recipe Maintainers:
        # Check the CMake/patches folder, and use the most recent cmake
        # that matches the largest major version in the list.
        # That should be the last cmake that was tested by VTK.
        # Also adjust our CMakeLists.txt to match this number.
        # TODO automate this?  Put this version number in conandata.yml?

        # Note that 3.22.4 may have been the last version that Kitware tested, so we'll use that.
        # TODO SHOULD BE HERE, but doesn't work
        # self.tool_requires("cmake/3.22.4")
        pass

    def validate(self):
        if not self.options.shared and self.options.enable_kits:
            raise ConanInvalidConfiguration("KITS can only be enabled with shared")

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC


    def _ensure_cpp17(self):
        compilers_minimum_version = {
                "gcc": "9",
                "Visual Studio": "15.7",
                "clang": "7",
                "apple-clang": "11",
            }

        # TODO for debugging weird behaviour on mac on CCI
        if (str(self.settings.compiler) != "apple-clang":
            raise ConanInvalidConfiguration("Not building, just want to focus on apple-clang for now")

        # VTK needs C++17 to compile
        # This code was copied from p-ranav-glob
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 17)
        minimum_version = compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))




    def configure(self):
        self._ensure_cpp17()
        if self.options.shared:
            del self.options.fPIC


    def layout(self):
        cmake_layout(self)


    def generate(self):
        tc = CMakeToolchain(self)

        # for debugging the conan recipe
        # tc.variables["CMAKE_FIND_DEBUG_MODE"] = True

        # 64 / 32 bit IDs
        if self.options.use_64bit_ids != "Auto":
            tc.variables["VTK_USE_64BIT_IDS"] = self.options.use_64bit_ids

        # Be sure to set this, otherwise vtkCompilerChecks.cmake will downgrade our CXX standard to 11
        tc.variables["VTK_IGNORE_CMAKE_CXX11_CHECKS"] = True


        # no need for versions on installed names?
        tc.variables["VTK_VERSIONED_INSTALL"] = False

        # Turn these off for CCI
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_DOCUMENTATION"] = False


        # Needed or not? Nothing gets installed without this ON at the moment.
        # tc.variables["VTK_INSTALL_SDK"] = False


        # future-proofing for your code
        tc.variables["VTK_LEGACY_REMOVE"] = self.options.legacy_remove # disable legacy APIs
        tc.variables["VTK_LEGACY_SILENT"] = self.options.legacy_silent # requires legacy_remove to be off. deprecated APIs will not cause warnings
        tc.variables["VTK_USE_FUTURE_CONST"] = self.options.use_future_const # use the newer const-correct APIs
        tc.variables["VTK_ENABLE_LOGGING"] = self.options.enable_logging


        # development debugging
        tc.variables["VTK_DEBUG_LEAKS"] = self.options.debug_leaks



        # Enable KITs - Quote: "Compiles VTK into a smaller set of libraries."
        # Quote: "Can be useful on platforms where VTK takes a long time to launch due to expensive disk access."
        tc.variables["VTK_ENABLE_KITS"] = self.options.enable_kits


        tc.variables["VTK_ENABLE_WRAPPING"] = self.options.enable_wrapping
        tc.variables["VTK_WRAP_JAVA"] = self.options.wrap_java
        tc.variables["VTK_WRAP_PYTHON"] = self.options.wrap_python
        tc.variables["VTK_USE_TK"] = self.options.use_tk    # requires wrap_python


        #### CUDA / MPI / MEMKIND ####
        tc.variables["VTK_USE_CUDA"]    = self.options.use_cuda
        tc.variables["VTK_USE_MEMKIND"] = self.options.use_memkind
        tc.variables["VTK_USE_MPI"]     = self.options.use_mpi


        ### Modules ###
        tc.variables["VTK_BUILD_ALL_MODULES"] = self.options.build_all_modules


        # There are LOTS of these modules now ...
        # for vtkModule in self.required_modules:
            # tc.variables["VTK_MODULE_ENABLE_VTK_" + vtkModule] = _yesno(True)

        # TODO support more modules - see notes above re hdf5
        # tc.variables["VTK_MODULE_ENABLE_VTK_hdf5"] = _yesno(True)

        # https://gitlab.kitware.com/vtk/vtk/-/blob/master/Documentation/dev/build.md
        # TODO try VTK_USE_VIDEO_FOR_WINDOWS   for video capture
        # TODO try VTK_USE_VIDEO_FOR_WINDOWS_CAPTURE   for video capture
        # TODO try VTK_USE_MICROSOFT_MEDIA_FOUNDATION   for video capture (MP4)


        # if flag is false, then sets to "DEFAULT" ie WILL build if wanted by some other YES
        # could also: "YES" "NO" "WANT" "DONT_WANT"
        # where yes/no is enforced, and want/dont_want are hints
        def _yesno(flag):
            return "YES" if flag else "DEFAULT"


        # groups can be:  DEFAULT   DONT_WANT   WANT   YES   NO
        # Note that YES is like WANT, but will show errors if can't make everything
        # NO is also more forceful than DONT_WANT
        # Default is DONT_WANT, let it auto-enable when required
        tc.variables["VTK_GROUP_ENABLE_Imaging"]    = _yesno(self.options.group_enable_Imaging)    # TODO test
        tc.variables["VTK_GROUP_ENABLE_MPI"]        = _yesno(self.options.group_enable_MPI)        # TODO test
        tc.variables["VTK_GROUP_ENABLE_Rendering"]  = _yesno(self.options.group_enable_Rendering)
        tc.variables["VTK_GROUP_ENABLE_StandAlone"] = _yesno(self.options.group_enable_StandAlone)  # TODO test
        tc.variables["VTK_GROUP_ENABLE_Views"]      = _yesno(self.options.group_enable_Views)       # TODO test
        tc.variables["VTK_GROUP_ENABLE_Web"]        = _yesno(self.options.group_enable_Web)         # TODO test

        # for Qt, can also use the more specific MODULE options below
        tc.variables["VTK_GROUP_ENABLE_Qt"] = _yesno(self.options.group_enable_Qt)


        ##### QT ######
        # QT has a few modules, we'll be specific
        tc.variables["VTK_QT_VERSION"] = self.options.qt_version
        tc.variables["VTK_MODULE_ENABLE_VTK_GUISupportQt"]      = _yesno(self.options.module_enable_GUISupportQt)
        tc.variables["VTK_MODULE_ENABLE_VTK_GUISupportQtQuick"] = _yesno(self.options.module_enable_GUISupportQtQuick)
        tc.variables["VTK_MODULE_ENABLE_VTK_GUISupportQtSQL"]   = _yesno(self.options.module_enable_GUISupportQtSQL)
        tc.variables["VTK_MODULE_ENABLE_VTK_RenderingQt"]   = _yesno(self.options.module_enable_RenderingQt)
        tc.variables["VTK_MODULE_ENABLE_VTK_ViewsQt"]   = _yesno(self.options.module_enable_ViewsQt)


        ##### SMP parallelism ####  Sequential  STDThread  OpenMP  TBB
        # Note that STDThread seems to be available by default
        tc.variables["VTK_SMP_IMPLEMENTATION_TYPE"] = self.options.smp_implementation_type
        # Change change the mode during runtime, if you enable the backends like so:
        tc.variables["VTK_SMP_ENABLE_Sequential"]   = self.options.smp_enable_Sequential
        tc.variables["VTK_SMP_ENABLE_STDThread"]    = self.options.smp_enable_STDThread
        tc.variables["VTK_SMP_ENABLE_OpenMP"]       = self.options.smp_enable_OpenMP
        tc.variables["VTK_SMP_ENABLE_TBB"]          = self.options.smp_enable_TBB


        #### Use the Internal VTK bundled libraries for these Third Party dependencies ...
        # Ask VTK to use their bundled versions for these:
        #
        # VTK uses a heavily-forked version they call 2.4.0.  Upstream libharu is currently unmaintained.
        tc.variables["VTK_MODULE_USE_EXTERNAL_VTK_libharu"] = False
        #
        # CCI does not have gl2ps yet.  Note that cern-root is also waiting for gl2ps.
        tc.variables["VTK_MODULE_USE_EXTERNAL_VTK_gl2ps"] = False
        #

        ###


        # Everything else should come from conan.
        # TODO check if anything is coming from the system CMake,
        # and change it to conan or add as a build_requirement for the system to install.
        # SOME of VTK's bundled Third Party libs are heavily forked and patched, so system versions may
        # not be appropriate to use externally (like libharu).
        tc.variables["VTK_USE_EXTERNAL"] = True

        tc.generate()


    def build(self):
        if not self.no_copy_source:
            self._patch_source()
        cmake = CMake(self)
        cmake.configure(build_script_folder=self._source_subfolder)
        cmake.build()


    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "vtk", "conan-official-{}-variables.cmake".format(self.name))


    def package(self):
        cmake = CMake(self)
        cmake.install()

        # VTK installs the licenses under the res/licenses/VTK directory, move it
        rename( os.path.join(self.package_folder,"res","licenses","VTK"),
                os.path.join(self.package_folder,"licenses"))

        # keep copy of generated VTK cmake files, for inspection
        if _debug_packaging:
            rename( os.path.join(self.package_folder,"lib","cmake"),
                    os.path.join(self.package_folder,"vtk-cmake-backup"))
        else:
            # delete VTK-installed cmake files
            rmdir(os.path.join(self.package_folder,"lib","cmake"))

        # create a cmake file with our special variables
        content = textwrap.dedent("""\
                set (VTK_ENABLE_KITS {})
                """
                .format(self.options.enable_kits)
                )
        save(os.path.join(self.package_folder, self._module_file_rel_path),
                content
                )


    def package_info(self):
        # Note: I don't currently import the explicit dependency list for each component from VTK,
        # so every module will depend on "everything" external, and there are no internal dependencies.
        # Consumers just have to figure out what they have to link.

        # get keys as a list and make a list of target::target
        all_requires = [k + "::" + k for k in self._third_party().keys()]

        if self.options.group_enable_Rendering:
            all_requires += [
                    "opengl::opengl",
                    "xorg::xorg",
                    ]
        all_requires.sort()

        # All modules use the same include dir.
        #
        # Cannot just be vtk_include_dirs = "include",
        # as vtk files include themselves with #include <vtkCommand.h>
        # and the files can't find each other in the same dir when included with <>
        #
        # Plus, it is standard to include vtk files with #include <vtkWhatever.h>
        #
        # Note also we aren't using "-9" in include/vtk-9: VTK_VERSIONED_INSTALL=False
        # With versioned_install, we would do: "include/vtk-%s" % self.short_version,
        #
        vtk_include_dirs   = [os.path.join("include", "vtk")]

        # auto-include these .cmake files (generated by conan)
        vtk_cmake_build_modules = [self._module_file_rel_path]


        # Needed?
        # if self.settings.os == "Linux":
        #     self.cpp_info.system_libs += ["dl","pthread"]

        # Just generate 'config' version, FindVTK.cmake hasn't existed since CMake 3.1, according to:
        # https://cmake.org/cmake/help/latest/module/FindVTK.html

        components = list(l[3:] for l in collect_libs(self, folder="lib"))

        self.cpp_info.set_property("cmake_file_name", "VTK")
        self.cpp_info.set_property("cmake_target_name", "VTK::VTK")
        self.cpp_info.builddirs = [os.path.join("lib", "cmake", "vtk")]

        # Should not be added to the VTK::VTK target... right?
        # self.cpp_info.libdirs   = ["lib"]

        for comp in components:
            self.cpp_info.components[comp].set_property("cmake_target_name", "VTK::" + comp)
            self.cpp_info.components[comp].libs          = ["vtk" + comp]
            self.cpp_info.components[comp].libdirs       = ["lib"]
            self.cpp_info.components[comp].includedirs   = vtk_include_dirs
            self.cpp_info.components[comp].requires      = all_requires
            self.cpp_info.components[comp].set_property("cmake_build_modules", vtk_cmake_build_modules)
            if self.settings.os == "Linux":
                self.cpp_info.components[comp].system_libs = ["m"]


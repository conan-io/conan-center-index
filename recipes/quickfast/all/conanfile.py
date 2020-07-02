from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
import os
import shutil


class QuickfastConan(ConanFile):
    name = "quickfast"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://objectcomputing.com/"
    description = "QuickFAST is an Open Source native C++ implementation of the FAST Protocol"
    topics = ("conan", "QuickFAST", "FAST", "FIX", "Fix Adapted for STreaming", "Financial Information Exchange",
              "libraries", "cpp")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False}
    requires = ["boost/1.73.0", "xerces-c/3.2.3"]
    build_requires = "makefile-project-workspace-creator/4.1.46"
    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version.replace(".", "_"), self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        if self.settings.compiler == "Visual Studio":
            self.generators = "visual_studio",
        else:
            self.generators = "make",

        self.options['boost'].shared = True

    def build(self):
        # Patch taken from:
        # https://raw.githubusercontent.com/microsoft/vcpkg/master/ports/quickfast/00001-fix-boost-asio.patch
        patches = self.conan_data["patches"][self.version]
        for patch in patches:
            tools.patch(**patch)

        with tools.chdir(self._source_subfolder):
            if self.settings.os == "Windows":
                pass
            else:
                env_build = AutoToolsBuildEnvironment(self)
                args = ['CONAN_MAKE_FILE=' + os.path.join(self.build_folder, "conanbuildinfo.mak")]

                with tools.environment_append(
                        {**env_build.vars,
                         **{"QUICKFAST_ROOT": os.path.join(self.build_folder, self._source_subfolder),
                            "XERCESCROOT": self.deps_cpp_info["xerces-c"].rootpath,
                            }}):
                    fpic = '-fPIC' if self.options.get_safe("fPIC", default=True) else ''
                    self.run('mwc.pl -type make -exclude src/Examples' + (' ' if self.options.shared else ' -static') +
                             ' -value_template "pic={}"'.format(fpic) +
                             ' -value_template platforms=macosx'
                             ' -value_template "linkflags+=-framework CoreServices -framework CoreFoundation"'
                             ' -value_template extracppflags+=-DBOOST_BIND_GLOBAL_PLACEHOLDERS'
                             ' QuickFAST.mwc')
                    env_build.make(args=args, target="QuickFAST")

    def package(self):
        self.copy("*.dylib", dst="lib", src=os.path.join(self._source_subfolder, "lib"))
        self.copy("*.a", dst="lib", src=os.path.join(self._source_subfolder, "lib"))
        self.copy("*.h", dst="include/quickfast", src=os.path.join(self._source_subfolder, "src"))
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "quickfast"))
        self.cpp_info.defines.append("BOOST_BIND_NO_PLACEHOLDERS")
        self.cpp_info.defines.append("XML_USE_PTHREADS")
        if self.options.shared:
            self.cpp_info.defines.append("QUICKFAST_BUILD_DLL")

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob


class ConanFileDefault(ConanFile):
    name = "flex"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/westes/flex"
    description = "Flex, the fast lexical analyzer generator"
    topics = ("conan", "flex", "lex", "lexer", "lexical analyzer generator")
    license = "BSD-2-Clause"    

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    requires = ("m4/1.4.18",)

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Flex package is not compatible with Windows. Consider using winflexbison instead.")

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        configure_args = ["--disable-nls", "HELP2MAN=/bin/true", "M4=m4"]
        if self.options.shared:
            configure_args.extend(["--enable-shared", "--disable-static"])
        else:
            configure_args.extend(["--disable-shared", "--enable-static"])

        with tools.chdir(self._source_subfolder):
            if self.settings.os == "Linux":
                # https://github.com/westes/flex/issues/247
                configure_args.extend(["ac_cv_func_malloc_0_nonnull=yes", "ac_cv_func_realloc_0_nonnull=yes"])
                # https://github.com/easybuilders/easybuild-easyconfigs/pull/5792
                configure_args.append("ac_cv_func_reallocarray=no")
            if tools.cross_building(self.settings, skip_x64_x86=True):
                # stage1flex must be built on native arch: https://github.com/westes/flex/issues/78
                self.run("./configure %s" % " ".join(configure_args))
                env_build.make(args=["-C", "src", "stage1flex"])
                self.run("mv src/stage1flex src/stage1flex.build")
                env_build.make(args=["distclean"])
                with tools.environment_append(env_build.vars):
                    env_build.configure(args=configure_args)
                    cpu_count_option = "-j%s" % tools.cpu_count()
                    self.run("make -C src %s || true" % cpu_count_option)
                    self.run("mv src/stage1flex.build src/stage1flex")
                    self.run("touch src/stage1flex")
                    env_build.make(args=["-C", "src"])
            else:
                with tools.environment_append(env_build.vars):
                    env_build.configure(args=configure_args)
                    env_build.make()
            env_build.make(args=["install"])

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        with tools.chdir(os.path.join(self.package_folder, "lib")):
            for filename in glob.glob("*.la"):
                os.unlink(filename)

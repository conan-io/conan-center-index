from conans import tools, ConanFile, Meson
import glob
import os
import shutil


class FriBiDiCOnan(ConanFile):
    name = "fribidi"
    description = "The Free Implementation of the Unicode Bidirectional Algorithm"
    topics = ("conan", "fribidi", "unicode", "bidirectional", "text")
    license = "LGPL-2.1"
    homepage = "https://github.com/fribidi/fribidi"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_deprecated": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_deprecated": True,
    }

    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        if not tools.which("meson"):
            self.build_requires("meson/0.53.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("fribidi-{}".format(self.version), self._source_subfolder)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        self._meson.options["deprecated"] = self.options.with_deprecated
        self._meson.options["docs"] = False
        self._meson.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)
        return self._meson

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"),
                              "subdir('bin')",
                              "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"),
                              "subdir('test')",
                              "")

    def build(self):
        self._patch_sources()
        meson = self._configure_meson()
        meson.build()

    def _fix_library_names(self, path):
        # regression in 1.16
        if self.settings.compiler == "Visual Studio":
            with tools.chdir(path):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info("rename %s into %s" % (filename_old, filename_new))
                    shutil.move(filename_old, filename_new)

    def package(self):
        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        meson = self._configure_meson()
        meson.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["fribidi"]
        self.cpp_info.includedirs.append(os.path.join("include", "fribidi"))
        if not self.options.shared:
            self.cpp_info.defines.append("FRIBIDI_STATIC")

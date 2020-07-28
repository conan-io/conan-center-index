from conans import ConanFile, tools, Meson, VisualStudioBuildEnvironment
import glob
import os
import shutil


class GStreamerConan(ConanFile):
    name = "gstreamer"
    version = "1.16.0"
    description = "GStreamer is a development framework for creating applications like media players, video editors, streaming media broadcasters and so on"
    topics = ("conan", "gstreamer", "multimedia", "video", "audio", "broadcasting", "framework", "media")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gstreamer.freedesktop.org/"
    license = "GPL-2.0-only"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    exports_sources = ["patches/*.diff"]

    requires = ("glib/2.65.0",)
    generators = "pkg_config"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("meson/0.54.2")
        if not tools.which("pkg-config") or self.settings.os == "Windows":
            self.build_requires("pkgconf/1.7.3")
        self.build_requires("bison/3.5.3")
        self.build_requires("flex/2.6.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("%s-%s" % (self.name, self.version), self._source_subfolder)

    def _apply_patches(self):
        for p in self.conan_data["patches"][self.version]:
            tools.patch(**p)

    def _configure_meson(self):
        meson = Meson(self)
        defs = dict()
        if self.settings.compiler == "Visual Studio":
            if int(str(self.settings.compiler.version)) < 14:
                defs["c_args"] = " -Dsnprintf=_snprintf"
                defs["cpp_args"] = " -Dsnprintf=_snprintf"
        if self.settings.get_safe("compiler.runtime"):
            defs["b_vscrt"] = str(self.settings.compiler.runtime).lower()
        defs["tools"] = "disabled"
        defs["examples"] = "disabled"
        defs["benchmarks"] = "disabled"
        defs["tests"] = "disabled"
        meson.configure(build_folder=self._build_subfolder,
                        source_folder=self._source_subfolder,
                        defs=defs, args=['--wrap-mode=nofallback'])
        return meson

    def build(self):
        self._apply_patches()
        with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if self._is_msvc else tools.no_op():
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
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if self._is_msvc else tools.no_op():
            meson = self._configure_meson()
            meson.install()

        self._fix_library_names(os.path.join(self.package_folder, "lib"))
        self._fix_library_names(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = [os.path.join("include", "gstreamer-1.0")]

        gst_plugin_path = os.path.join(self.package_folder, "lib", "gstreamer-1.0")
        if self.options.shared:
            self.output.info("Appending GST_PLUGIN_PATH env var : %s" % gst_plugin_path)
            self.env_info.GST_PLUGIN_PATH.append(gst_plugin_path)
        else:
            self.cpp_info.libdirs.append(gst_plugin_path)
            self.cpp_info.libs.extend(["gstcoreelements",
                                       "gstcoretracers"])
        self.cpp_info.libs.extend(["gstreamer-1.0", "gstbase-1.0", "gstcontroller-1.0", "gstnet-1.0"])

        if self.settings.os == "Linux":
            self.cpp_info.libs.append("dl")
        elif self.settings.os == "Windows":
            self.cpp_info.libs.append("ws2_32")
        if not self.options.shared:
            self.cpp_info.defines.append("GST_STATIC_COMPILATION")
        gstreamer_root = self.package_folder
        self.output.info("Creating GSTREAMER_ROOT env var : %s" % gstreamer_root)
        self.env_info.GSTREAMER_ROOT = gstreamer_root
        gst_plugin_scanner = "gst-plugin-scanner.exe" if self.settings.os == "Windows" else "gst-plugin-scanner"
        gst_plugin_scanner = os.path.join(self.package_folder, "bin", "gstreamer-1.0", gst_plugin_scanner)
        self.output.info("Creating GST_PLUGIN_SCANNER env var : %s" % gst_plugin_scanner)
        self.env_info.GST_PLUGIN_SCANNER = gst_plugin_scanner
        if self.settings.arch == "x86":
            self.output.info("Creating GSTREAMER_ROOT_X86 env var : %s" % gstreamer_root)
            self.env_info.GSTREAMER_ROOT_X86 = gstreamer_root
        elif self.settings.arch == "x86_64":
            self.output.info("Creating GSTREAMER_ROOT_X86_64 env var : %s" % gstreamer_root)
            self.env_info.GSTREAMER_ROOT_X86_64 = gstreamer_root


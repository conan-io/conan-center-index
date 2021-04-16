from conans import ConanFile, tools, Meson, VisualStudioBuildEnvironment
import glob
import os
import shutil

required_conan_version = ">=1.29"

class GStreamerConan(ConanFile):
    name = "gstreamer"
    description = "GStreamer is a development framework for creating applications like media players, video editors, streaming media broadcasters and so on"
    topics = ("conan", "gstreamer", "multimedia", "video", "audio", "broadcasting", "framework", "media")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gstreamer.freedesktop.org/"
    license = "GPL-2.0-only"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "pkg_config"
    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("glib/2.67.1")

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("meson/0.56.2")
        self.build_requires("pkgconf/1.7.3")
        if self.settings.os == 'Windows':
            self.build_requires("winflexbison/2.5.22")
        else:
            self.build_requires("bison/3.7.1")
            self.build_requires("flex/2.6.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("%s-%s" % (self.name, self.version), self._source_subfolder)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        meson = Meson(self)
        if self._is_msvc:
            if tools.Version(self.settings.compiler.version) < "14":
                meson.options["c_args"] = " -Dsnprintf=_snprintf"
                meson.options["cpp_args"] = " -Dsnprintf=_snprintf"
        if self.settings.get_safe("compiler.runtime"):
            meson.options["b_vscrt"] = str(self.settings.compiler.runtime).lower()
        meson.options["tools"] = "disabled"
        meson.options["examples"] = "disabled"
        meson.options["benchmarks"] = "disabled"
        meson.options["tests"] = "disabled"
        meson.configure(build_folder=self._build_subfolder,
                        source_folder=self._source_subfolder,
                        args=['--wrap-mode=nofallback'])
        self._meson = meson
        return self._meson

    def build(self):
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
        tools.rmdir(os.path.join(self.package_folder, "lib", "gstreamer-1.0", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(self.package_folder, "*.pdb")

    def package_info(self):
        gst_plugin_path = os.path.join(self.package_folder, "lib", "gstreamer-1.0")

        self.cpp_info.components["gstreamer-1.0"].names["pkg_config"] = "gstreamer-1.0"
        self.cpp_info.components["gstreamer-1.0"].requires = ["glib::glib-2.0", "glib::gobject-2.0"]
        if not self.options.shared:
            self.cpp_info.components["gstreamer-1.0"].requires.append("glib::gmodule-no-export-2.0")
            self.cpp_info.components["gstreamer-1.0"].defines.append("GST_STATIC_COMPILATION")
        self.cpp_info.components["gstreamer-1.0"].libs = ["gstreamer-1.0"]
        self.cpp_info.components["gstreamer-1.0"].includedirs = [os.path.join("include", "gstreamer-1.0")]
                                       
        self.cpp_info.components["gstreamer-base-1.0"].names["pkg_config"] = "gstreamer-base-1.0"
        self.cpp_info.components["gstreamer-base-1.0"].requires = ["gstreamer-1.0"]
        self.cpp_info.components["gstreamer-base-1.0"].libs = ["gstbase-1.0"]
        self.cpp_info.components["gstreamer-base-1.0"].includedirs = [os.path.join("include", "gstreamer-1.0")]
                                       
        self.cpp_info.components["gstreamer-controller-1.0"].names["pkg_config"] = "gstreamer-controller-1.0"
        self.cpp_info.components["gstreamer-controller-1.0"].requires = ["gstreamer-1.0"]
        self.cpp_info.components["gstreamer-controller-1.0"].libs = ["gstcontroller-1.0"]
        self.cpp_info.components["gstreamer-controller-1.0"].includedirs = [os.path.join("include", "gstreamer-1.0")]
                                       
        self.cpp_info.components["gstreamer-net-1.0"].names["pkg_config"] = "gstreamer-net-1.0"
        self.cpp_info.components["gstreamer-net-1.0"].requires = ["gstreamer-1.0", "glib::gio-2.0"]
        self.cpp_info.components["gstreamer-net-1.0"].libs = ["gstnet-1.0"]
        self.cpp_info.components["gstreamer-net-1.0"].includedirs = [os.path.join("include", "gstreamer-1.0")]
                                       
        self.cpp_info.components["gstreamer-check-1.0"].names["pkg_config"] = "gstreamer-check-1.0"
        self.cpp_info.components["gstreamer-check-1.0"].requires = ["gstreamer-1.0"]
        self.cpp_info.components["gstreamer-check-1.0"].libs = ["gstcheck-1.0"]
        self.cpp_info.components["gstreamer-check-1.0"].includedirs = [os.path.join("include", "gstreamer-1.0")]
                                       
        # gstcoreelements and gstcoretracers are plugins which should be loaded dynamicaly, and not linked to directly
        if not self.options.shared:
            self.cpp_info.components["gstcoreelements"].names["pkg_config"] = "gstcoreelements"
            self.cpp_info.components["gstcoreelements"].requires = ["glib::gobject-2.0", "glib::glib-2.0", "gstreamer-1.0", "gstreamer-base-1.0"]
            self.cpp_info.components["gstcoreelements"].libs = ["gstcoreelements"]
            self.cpp_info.components["gstcoreelements"].includedirs = [os.path.join("include", "gstreamer-1.0")]
            self.cpp_info.components["gstcoreelements"].libdirs = [gst_plugin_path]

            self.cpp_info.components["gstcoretracers"].names["pkg_config"] = "gstcoretracers"
            self.cpp_info.components["gstcoretracers"].requires = ["gstreamer-1.0"]
            self.cpp_info.components["gstcoretracers"].libs = ["gstcoretracers"]
            self.cpp_info.components["gstcoretracers"].includedirs = [os.path.join("include", "gstreamer-1.0")]
            self.cpp_info.components["gstcoretracers"].libdirs = [gst_plugin_path]

        if self.options.shared:
            self.output.info("Appending GST_PLUGIN_PATH env var : %s" % gst_plugin_path)
            self.env_info.GST_PLUGIN_PATH.append(gst_plugin_path)
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

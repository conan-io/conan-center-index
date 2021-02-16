from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.29.0"

class LibnameConan(ConanFile):
    name = "graphene"
    description = "A thin layer of graphic data types."
    topics = ("conan", "graphene")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://ebassi.github.io/graphene/"
    license = "MIT"
    generators = "pkg_config"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_glib": [True, False],
        }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_glib": True,
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler == "gcc":
            if tools.Version(self.settings.compiler.version) < "5.0":
                raise ConanInvalidConfiguration("graphene does not support GCC before 5.0")
    
    def build_requirements(self):
        self.build_requires("meson/0.56.2")
        self.build_requires("pkgconf/1.7.3")
    
    def requirements(self):
        if self.options.with_glib:
            self.requires("glib/2.67.3")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_meson(self):
        meson = Meson(self)
        defs = {}
        defs["gobject_types"] = "true" if self.options.with_glib else "false"
        if tools.Version(self.version) < "1.10.4":
            defs["introspection"] = "false"
        else:
            defs["introspection"] = "disabled"
        defs["tests"] = "false"
        defs["installed_tests"] = "false"
        defs["gtk_doc"] = "false"
        args=[]
        args.append("--wrap-mode=nofallback")
        meson.configure(defs=defs, build_folder=self._build_subfolder, source_folder=self._source_subfolder, pkg_config_paths=[self.install_folder], args=args)
        return meson

    def build(self):
        with tools.environment_append(tools.RunEnvironment(self).vars):
            meson = self._configure_meson()
            meson.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        with tools.environment_append({"PKG_CONFIG_PATH": self.install_folder}):
            meson.install()
        
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            with tools.chdir(os.path.join(self.package_folder, "lib")):
                if os.path.isfile("libgraphene-1.0.a"):
                    tools.rename("libgraphene-1.0.a", "graphene-1.0.lib")
                
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(self.package_folder, "*.pdb")

    def package_info(self):
        self.cpp_info.components["graphene-1.0"].libs = ["graphene-1.0"]
        self.cpp_info.components["graphene-1.0"].includedirs = [os.path.join("include", "graphene-1.0"), os.path.join("lib", "graphene-1.0", "include")]
        self.cpp_info.components["graphene-1.0"].names["pkg_config"] = "graphene-1.0"
        if self.options.with_glib:
            self.cpp_info.components["graphene-1.0"].requires = ["glib::gobject-2.0"]

        if self.options.with_glib:
            self.cpp_info.components["graphene-gobject-1.0"].includedirs = [os.path.join("include", "graphene-1.0")]
            self.cpp_info.components["graphene-gobject-1.0"].names["pkg_config"] = "graphene-gobject-1.0"
            self.cpp_info.components["graphene-gobject-1.0"].requires = ["graphene-1.0", "glib::gobject-2.0"]

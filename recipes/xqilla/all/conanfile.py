from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.33.0"


class ConanXqilla(ConanFile):
    name = "xqilla"
    
    description = (
        "XQilla is an XQuery and XPath 2 library and command line utility written in C++, implemented on top of the Xerces-C library"
    )
    topics = ("xqilla", "xml", "xquery")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://xqilla.sourceforge.net/HomePage"
    license = "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "patches/**"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("xerces-c/3.2.3")

    @property
    def _doc_folder(self):
        return os.path.join(
            self._source_subfolder,
            "doc"
        )

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("The xqilla recipe currently only supports Linux.")
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def build_requirements(self):
        self.build_requires("gnu-config/cci.20210814")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        conf_args = [
            "--with-xerces={}".format(tools.unix_path(self.deps_cpp_info["xerces-c"].rootpath)),
        ]
        
        if not self.settings.compiler.cppstd:
            self._autotools.cppstd_flag = "-std=c++11"

        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])

        if self.options.get_safe("fPIC", True):
            conf_args.extend(["--with-pic"])

        self._autotools.configure(configure_dir=self._source_subfolder, args=conf_args)
        return self._autotools

    @property 
    def _user_info_build(self): 
        return getattr(self, "user_info_build", self.deps_user_info) 

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "autotools","config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "autotools","config.guess"))
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        autotools = self._configure_autotools()
        autotools.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("README", dst="licenses/LICENSE.mapm", src=os.path.join(self._source_subfolder, "src", "mapm"))

        tmp = tools.load(os.path.join(self._source_subfolder, "src", "yajl", "yajl_buf.h"))
        license_contents = tmp[2:tmp.find("*/", 1)] 
        tools.save("LICENSE", license_contents)
        self.copy("LICENSE", dst="licenses/LICENSE.yajl",  ignore_case=True, keep_path=False)

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "share"))
        
    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libxqilla"
        self.cpp_info.libs =  tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.path.append(bin_path)


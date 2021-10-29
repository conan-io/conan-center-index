from conans import ConanFile, tools
import os


class NSSConan(ConanFile):
    name = "nss"
    license = "Mozilla Public License"
    homepage = "https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSS"
    url = "https://github.com/conan-io/conan-center-index"
    description = "<Description of Libxshmfence here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("nspr/4.32")
        self.requires("sqlite3/3.36.0")
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(os.path.join(self._source_subfolder, "nss")):
            args = []
            args.append("USE_64=1")
            args.append("NSPR_INCLUDE_DIR=%s" % self.deps_cpp_info["nspr"].include_paths[1])
            args.append("NSPR_LIB_DIR=%s" % self.deps_cpp_info["nspr"].lib_paths[0])
            args.append("OS_TARGET=Linux")
            args.append("USE_SYSTEM_ZLIB=1")
            args.append("NSS_USE_SYSTEM_SQLITE=1")
            args.append("SQLITE_INCLUDE_DIR=%s" % self.deps_cpp_info["sqlite3"].include_paths[0])
            args.append("SQLITE_LIB_DIR=%s" % self.deps_cpp_info["sqlite3"].lib_paths[0])
            self.run("make %s" % " ".join(args))

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        pass

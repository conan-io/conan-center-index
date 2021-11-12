from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
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
        self.options["nspr"].shared = True

    def requirements(self):
        self.requires("nspr/4.32")
        self.requires("sqlite3/3.36.0")
        self.requires("zlib/1.2.11")

    def validate(self):
        if not self.options["nspr"].shared:
            raise ConanInvalidConfiguration("NSS cannot link to static NSPR. Please use option nspr:shared=True")

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
            args.append("NSS_DISABLE_GTESTS=1")
            # args.append("NSS_USE_SYSTEM_SQLITE=1")
            # args.append("SQLITE_INCLUDE_DIR=%s" % self.deps_cpp_info["sqlite3"].include_paths[0])
            # args.append("SQLITE_LIB_DIR=%s" % self.deps_cpp_info["sqlite3"].lib_paths[0])
            args.append("NSDISTMODE=copy")
            self.run("make %s" % " ".join(args))

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with tools.chdir(os.path.join(self._source_subfolder, "nss")):
            args = []
            args.append("USE_64=1")
            args.append("NSPR_INCLUDE_DIR=%s" % self.deps_cpp_info["nspr"].include_paths[1])
            args.append("NSPR_LIB_DIR=%s" % self.deps_cpp_info["nspr"].lib_paths[0])
            args.append("OS_TARGET=Linux")
            args.append("USE_SYSTEM_ZLIB=1")
            args.append("NSS_DISABLE_GTESTS=1")
            # args.append("NSS_USE_SYSTEM_SQLITE=1")
            # args.append("SQLITE_INCLUDE_DIR=%s" % self.deps_cpp_info["sqlite3"].include_paths[0])
            # args.append("SQLITE_LIB_DIR=%s" % self.deps_cpp_info["sqlite3"].lib_paths[0])
            args.append("NSDISTMODE=copy")
            self.run("make install %s" % " ".join(args))
        self.copy("*",
                  src=os.path.join(self._source_subfolder, "dist", "public", "nss"),
                  dst="include")
        for d in os.listdir(os.path.join(self._source_subfolder, "dist")):
            if d in ["private","public"]:
                continue
            f = os.path.join(self._source_subfolder, "dist", d)
            if not os.path.isdir(f):
                continue
            self.copy("*", src = f)

        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.a")
        else:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.so")

        self.copy("COPYING",
                  src = os.path.join(self._source_subfolder, "nss"),
                  dst = "licenses")


    def package_info(self):

        def _library_name(lib,vers):
            if self.options.shared:
                return "%s%s" % (lib,vers)
            else:
                return lib
        self.cpp_info.components["libnss"].libs.append(_library_name("nss", 3))
        self.cpp_info.components["libnss"].requires = ["nssutil", "nspr::nspr"]

        self.cpp_info.components["nssutil"].libs = [_library_name("nssutil", 3)]
        self.cpp_info.components["nssutil"].requires = ["nspr::nspr"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["nssutil"].system_libs = ["pthread"]

        self.cpp_info.components["softokn"].libs = [_library_name("softokn", 3)]
        self.cpp_info.components["softokn"].requires = ["sqlite3::sqlite3", "nssutil", "nspr::nspr"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["softokn"].system_libs = ["pthread"]

        self.cpp_info.components["freebl"].libs = [_library_name("freebl", 3)]

        self.cpp_info.components["freeblpriv"].libs = [_library_name("freeblpriv", 3)]

        self.cpp_info.components["nssdbm"].libs = [_library_name("nssdbm", 3)]
        self.cpp_info.components["nssdbm"].requires = ["nspr::nspr", "nssutil"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["nssdbm"].system_libs = ["pthread"]

        self.cpp_info.components["smime"].libs = [_library_name("smime", 3)]
        self.cpp_info.components["smime"].requires = ["nspr::nspr", "libnss", "nssutil"]

        self.cpp_info.components["ssl"].libs = [_library_name("ssl", 3)]
        self.cpp_info.components["ssl"].requires = ["nspr::nspr", "libnss", "nssutil"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ssl"].system_libs = ["pthread"]

        self.cpp_info.components["nss_executables"].requires = ["zlib::zlib"]

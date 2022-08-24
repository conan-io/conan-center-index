from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

class NcbiCxxToolkit(ConanFile):
    name = "ncbi-cxx-toolkit-public"
    license = "CC0-1.0"
    homepage = "https://ncbi.github.io/cxx-toolkit"
    url = "https://github.com/conan-io/conan-center-index"
    description = "NCBI C++ Toolkit -- a cross-platform application framework and a collection of libraries for working with biological data."
    topics = ("ncbi", "biotechnology", "bioinformatics", "genbank", "gene",
              "genome", "genetic", "sequence", "alignment", "blast",
              "biological", "toolkit", "c++")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    short_paths = True

    options = {
        "shared":     [True, False],
        "fPIC":       [True, False],
        "with_projects": "ANY",
        "with_targets":  "ANY"
    }
    default_options = {
        "shared":     False,
        "fPIC":       True,
        "with_projects":  "",
        "with_targets":   "",
    }
    NCBI_to_Conan_requires = {
        "BerkeleyDB":   "libdb/5.3.28",
        "BZ2":          "bzip2/1.0.8",
        "CASSANDRA":    "cassandra-cpp-driver/2.15.3",
        "GIF":          "giflib/5.2.1",
        "JPEG":         "libjpeg/9d",
        "LMDB":         "lmdb/0.9.29",
        "LZO":          "lzo/2.10",
        "MySQL":        "libmysqlclient/8.0.25",
        "NGHTTP2":      "libnghttp2/1.46.0",
        "PCRE":         "pcre/8.45",
        "PNG":          "libpng/1.6.37",
        "SQLITE3":      "sqlite3/3.37.2",
        "TIFF":         "libtiff/4.3.0",
        "XML":          "libxml2/2.9.12",
        "XSLT":         "libxslt/1.1.34",
        "UV":           "libuv/1.42.0",
        "Z":            "zlib/1.2.11",
        "OpenSSL":      "openssl/1.1.1l",
        "ZSTD":         "zstd/1.5.2"
    }

#----------------------------------------------------------------------------
    def _get_RequiresMapKeys(self):
        return self.NCBI_to_Conan_requires.keys()

#----------------------------------------------------------------------------
    def _translate_ReqKey(self, key):
        if key in self.NCBI_to_Conan_requires.keys():
            if key == "BerkeleyDB" and self.settings.os == "Windows":
                return None
            if key == "CASSANDRA" and (self.settings.os == "Windows" or self.settings.os == "Macos"):
                return None
            if key == "NGHTTP2" and self.settings.os == "Windows":
                return None
            return self.NCBI_to_Conan_requires[key]
        return None

#----------------------------------------------------------------------------
    @property
    def _source_subfolder(self):
        return "src"

#----------------------------------------------------------------------------
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["NCBI_PTBCFG_PACKAGING"] = "TRUE"
        if self.options.with_projects != "":
            cmake.definitions["NCBI_PTBCFG_PROJECT_LIST"] = self.options.with_projects
        if self.options.with_targets != "":
            cmake.definitions["NCBI_PTBCFG_PROJECT_TARGETS"] = self.options.with_targets
        return cmake

#----------------------------------------------------------------------------
    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 17)
        if self.settings.os not in ["Linux", "Macos", "Windows"]:   
            raise ConanInvalidConfiguration("This operating system is not supported")
        if self.settings.compiler == "Visual Studio" and tools.scm.Version(self.settings.compiler.version) < "16":
            raise ConanInvalidConfiguration("This version of Visual Studio is not supported")
        if self.settings.compiler == "Visual Studio" and self.options.shared and "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("This configuration is not supported")
        if self.settings.compiler == "gcc" and tools.scm.Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration("This version of GCC is not supported")
        if hasattr(self, "settings_build") and tools.build.cross_building(self, self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross compilation is not supported")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

#----------------------------------------------------------------------------
    def requirements(self):
        NCBIreqs = self._get_RequiresMapKeys()
        for req in NCBIreqs:
            pkg = self._translate_ReqKey(req)
            if pkg is not None:
                self.requires(pkg)

#----------------------------------------------------------------------------
    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root = True)

#----------------------------------------------------------------------------
    def build(self):
        cmake = self._configure_cmake()
        cmake.configure(source_folder=self._source_subfolder)
# Visual Studio sometimes runs "out of heap space"
        if self.settings.compiler == "Visual Studio":
            cmake.parallel = False
        cmake.build()

#----------------------------------------------------------------------------
    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

#----------------------------------------------------------------------------
    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.components["ORIGLIBS"].system_libs = ["ws2_32", "dbghelp"]
            self.cpp_info.components["NETWORKLIBS"].system_libs = []
        elif self.settings.os == "Linux":
            self.cpp_info.components["ORIGLIBS"].system_libs = ["dl", "rt", "m", "pthread"]
            self.cpp_info.components["NETWORKLIBS"].system_libs = ["resolv"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["ORIGLIBS"].system_libs = ["dl", "c", "m", "pthread"]
            self.cpp_info.components["NETWORKLIBS"].system_libs = ["resolv"]

        NCBIreqs = self._get_RequiresMapKeys()
        for req in NCBIreqs:
            pkg = self._translate_ReqKey(req)
            if pkg is not None:
                pkg = pkg[:pkg.find("/")]
                ref = pkg + "::" + pkg
                self.cpp_info.components[req].requires = [ref]
                self.cpp_info.components["ORIGLIBS"].requires.append(ref)
            else:
                self.cpp_info.components[req].libs = []

        allexports = {}
        impfile = os.path.join(self.package_folder, "res", "ncbi-cpp-toolkit.imports")
        if os.path.isfile(impfile):
            allexports = set(open(impfile).read().split())

#============================================================================
        if self.settings.os == "Windows" and self.options.shared:
#12--------------------------------------------------------------------------
            if "blast_app_util" in allexports:
                self.cpp_info.components["blast_app_util"].libs = ["blast_app_util"]
                self.cpp_info.components["blast_app_util"].requires = ["ncbi_blastinput"]
            if "vdb2blast" in allexports:
                self.cpp_info.components["vdb2blast"].libs = ["vdb2blast"]
                self.cpp_info.components["vdb2blast"].requires = ["ncbi_blastinput", "VDB"]
            if "xbma_refiner_gui" in allexports:
                self.cpp_info.components["xbma_refiner_gui"].libs = ["xbma_refiner_gui"]
                self.cpp_info.components["xbma_refiner_gui"].requires = ["ncbi_algo_structure", "wx_tools", "wxWidgets"]
            if "xngalign" in allexports:
                self.cpp_info.components["xngalign"].libs = ["xngalign"]
                self.cpp_info.components["xngalign"].requires = ["ncbi_blastinput", "xmergetree"]
#11--------------------------------------------------------------------------
            if "blast_unit_test_util" in allexports:
                self.cpp_info.components["blast_unit_test_util"].libs = ["blast_unit_test_util"]
                self.cpp_info.components["blast_unit_test_util"].requires = ["ncbi_algo", "test_boost", "Boost"]
            if "igblast" in allexports:
                self.cpp_info.components["igblast"].libs = ["igblast"]
                self.cpp_info.components["igblast"].requires = ["ncbi_algo"]
            if "ncbi_algo_ms" in allexports:
                self.cpp_info.components["ncbi_algo_ms"].libs = ["ncbi_algo_ms"]
                self.cpp_info.components["ncbi_algo_ms"].requires = ["ncbi_algo"]
            if "ncbi_algo_structure" in allexports:
                self.cpp_info.components["ncbi_algo_structure"].libs = ["ncbi_algo_structure"]
                self.cpp_info.components["ncbi_algo_structure"].requires = ["ncbi_mmdb", "ncbi_algo"]
            if "ncbi_blastinput" in allexports:
                self.cpp_info.components["ncbi_blastinput"].libs = ["ncbi_blastinput"]
                self.cpp_info.components["ncbi_blastinput"].requires = ["ncbi_xloader_blastdb_rmt", "ncbi_algo"]
            if "xaligncleanup" in allexports:
                self.cpp_info.components["xaligncleanup"].libs = ["xaligncleanup"]
                self.cpp_info.components["xaligncleanup"].requires = ["ncbi_algo"]
#10--------------------------------------------------------------------------
            if "ncbi_algo" in allexports:
                self.cpp_info.components["ncbi_algo"].libs = ["ncbi_algo"]
                self.cpp_info.components["ncbi_algo"].requires = ["sqlitewrapp", "ncbi_align_format", "utrtprof"]
            if "xalntool" in allexports:
                self.cpp_info.components["xalntool"].libs = ["xalntool"]
                self.cpp_info.components["xalntool"].requires = ["ncbi_align_format"]
#9--------------------------------------------------------------------------
            if "data_loaders_util" in allexports:
                self.cpp_info.components["data_loaders_util"].libs = ["data_loaders_util"]
#                self.cpp_info.components["data_loaders_util"].requires = ["ncbi_xdbapi_ftds", "ncbi_xloader_asn_cache", "ncbi_xloader_blastdb", "ncbi_xloader_genbank", "ncbi_xloader_lds2", "ncbi_xreader_pubseqos", "ncbi_xreader_pubseqos2", "ncbi_xloader_csra", "ncbi_xloader_wgs"]
                self.cpp_info.components["data_loaders_util"].requires = ["ncbi_xdbapi_ftds", "ncbi_xloader_asn_cache", "ncbi_xloader_blastdb", "ncbi_xloader_genbank", "ncbi_xloader_lds2", "ncbi_xreader_pubseqos", "ncbi_xreader_pubseqos2"]
            if "hgvs" in allexports:
                self.cpp_info.components["hgvs"].libs = ["hgvs"]
                self.cpp_info.components["hgvs"].requires = ["ncbi_xloader_genbank", "Boost"]
            if "ncbi_align_format" in allexports:
                self.cpp_info.components["ncbi_align_format"].libs = ["ncbi_align_format"]
                self.cpp_info.components["ncbi_align_format"].requires = ["ncbi_xloader_genbank", "ncbi_web"]
            if "ncbi_xobjsimple" in allexports:
                self.cpp_info.components["ncbi_xobjsimple"].libs = ["ncbi_xobjsimple"]
                self.cpp_info.components["ncbi_xobjsimple"].requires = ["ncbi_xloader_genbank"]
            if "xflatfile" in allexports:
                self.cpp_info.components["xflatfile"].libs = ["xflatfile"]
                self.cpp_info.components["xflatfile"].requires = ["ncbi_xdbapi_ftds", "ncbi_xloader_genbank"]
#8--------------------------------------------------------------------------
            if "ncbi_xloader_genbank" in allexports:
                self.cpp_info.components["ncbi_xloader_genbank"].libs = ["ncbi_xloader_genbank"]
                self.cpp_info.components["ncbi_xloader_genbank"].requires = ["ncbi_xreader_cache", "ncbi_xreader_id1", "ncbi_xreader_id2", "psg_client"]
#7--------------------------------------------------------------------------
            if "blast_sra_input" in allexports:
                self.cpp_info.components["blast_sra_input"].libs = ["blast_sra_input"]
                self.cpp_info.components["blast_sra_input"].requires = ["sraread", "VDB"]
            if "ncbi_xloader_blastdb_rmt" in allexports:
                self.cpp_info.components["ncbi_xloader_blastdb_rmt"].libs = ["ncbi_xloader_blastdb_rmt"]
                self.cpp_info.components["ncbi_xloader_blastdb_rmt"].requires = ["ncbi_xloader_blastdb"]
            if "ncbi_xloader_cdd" in allexports:
                self.cpp_info.components["ncbi_xloader_cdd"].libs = ["ncbi_xloader_cdd"]
                self.cpp_info.components["ncbi_xloader_cdd"].requires = ["cdd_access"]
            if "ncbi_xloader_csra" in allexports:
                self.cpp_info.components["ncbi_xloader_csra"].libs = ["ncbi_xloader_csra"]
                self.cpp_info.components["ncbi_xloader_csra"].requires = ["sraread", "VDB"]
            if "ncbi_xloader_lds2" in allexports:
                self.cpp_info.components["ncbi_xloader_lds2"].libs = ["ncbi_xloader_lds2"]
                self.cpp_info.components["ncbi_xloader_lds2"].requires = ["ncbi_lds2"]
            if "ncbi_xloader_snp" in allexports:
                self.cpp_info.components["ncbi_xloader_snp"].libs = ["ncbi_xloader_snp"]
                self.cpp_info.components["ncbi_xloader_snp"].requires = ["sraread", "dbsnp_ptis", "VDB", "GRPC"]
            if "ncbi_xloader_sra" in allexports:
                self.cpp_info.components["ncbi_xloader_sra"].libs = ["ncbi_xloader_sra"]
                self.cpp_info.components["ncbi_xloader_sra"].requires = ["sraread", "VDB"]
            if "ncbi_xloader_vdbgraph" in allexports:
                self.cpp_info.components["ncbi_xloader_vdbgraph"].libs = ["ncbi_xloader_vdbgraph"]
                self.cpp_info.components["ncbi_xloader_vdbgraph"].requires = ["sraread", "VDB"]
            if "ncbi_xloader_wgs" in allexports:
                self.cpp_info.components["ncbi_xloader_wgs"].libs = ["ncbi_xloader_wgs"]
                self.cpp_info.components["ncbi_xloader_wgs"].requires = ["sraread", "VDB"]
            if "ncbi_xreader_cache" in allexports:
                self.cpp_info.components["ncbi_xreader_cache"].libs = ["ncbi_xreader_cache"]
                self.cpp_info.components["ncbi_xreader_cache"].requires = ["ncbi_xreader"]
            if "ncbi_xreader_gicache" in allexports:
                self.cpp_info.components["ncbi_xreader_gicache"].libs = ["ncbi_xreader_gicache"]
                self.cpp_info.components["ncbi_xreader_gicache"].requires = ["ncbi_xreader", "LMDB"]
            if "ncbi_xreader_id1" in allexports:
                self.cpp_info.components["ncbi_xreader_id1"].libs = ["ncbi_xreader_id1"]
                self.cpp_info.components["ncbi_xreader_id1"].requires = ["ncbi_xreader"]
            if "ncbi_xreader_id2" in allexports:
                self.cpp_info.components["ncbi_xreader_id2"].libs = ["ncbi_xreader_id2"]
                self.cpp_info.components["ncbi_xreader_id2"].requires = ["ncbi_xreader"]
            if "ncbi_xreader_pubseqos" in allexports:
                self.cpp_info.components["ncbi_xreader_pubseqos"].libs = ["ncbi_xreader_pubseqos"]
                self.cpp_info.components["ncbi_xreader_pubseqos"].requires = ["ncbi_dbapi_driver", "ncbi_xreader"]
            if "ncbi_xreader_pubseqos2" in allexports:
                self.cpp_info.components["ncbi_xreader_pubseqos2"].libs = ["ncbi_xreader_pubseqos2"]
                self.cpp_info.components["ncbi_xreader_pubseqos2"].requires = ["ncbi_dbapi_driver", "ncbi_xreader", "eMyNCBI_result"]
#6--------------------------------------------------------------------------
            if "cdd_access" in allexports:
                self.cpp_info.components["cdd_access"].libs = ["cdd_access"]
                self.cpp_info.components["cdd_access"].requires = ["ncbi_seqext"]
            if "eMyNCBI_result" in allexports:
                self.cpp_info.components["eMyNCBI_result"].libs = ["eMyNCBI_result"]
                self.cpp_info.components["eMyNCBI_result"].requires = ["ncbi_seqext"]
            if "fix_pub" in allexports:
                self.cpp_info.components["fix_pub"].libs = ["fix_pub"]
                self.cpp_info.components["fix_pub"].requires = ["eutils_client", "ncbi_seqext"]
            if "gene_info_writer" in allexports:
                self.cpp_info.components["gene_info_writer"].libs = ["gene_info_writer"]
                self.cpp_info.components["gene_info_writer"].requires = ["ncbi_seqext"]
            if "ncbi_lds2" in allexports:
                self.cpp_info.components["ncbi_lds2"].libs = ["ncbi_lds2"]
                self.cpp_info.components["ncbi_lds2"].requires = ["ncbi_seqext", "sqlitewrapp", "SQLITE3"]
            if "ncbi_validator" in allexports:
                self.cpp_info.components["ncbi_validator"].libs = ["ncbi_validator"]
                self.cpp_info.components["ncbi_validator"].requires = ["ncbi_seqext"]
            if "ncbi_xdiscrepancy" in allexports:
                self.cpp_info.components["ncbi_xdiscrepancy"].libs = ["ncbi_xdiscrepancy"]
                self.cpp_info.components["ncbi_xdiscrepancy"].requires = ["macro", "ncbi_seqext"]
            if "ncbi_xloader_asn_cache" in allexports:
                self.cpp_info.components["ncbi_xloader_asn_cache"].libs = ["ncbi_xloader_asn_cache"]
                self.cpp_info.components["ncbi_xloader_asn_cache"].requires = ["asn_cache", "ncbi_seqext"]
            if "ncbi_xloader_bam" in allexports:
                self.cpp_info.components["ncbi_xloader_bam"].libs = ["ncbi_xloader_bam"]
                self.cpp_info.components["ncbi_xloader_bam"].requires = ["bamread", "ncbi_seqext", "VDB"]
            if "ncbi_xloader_blastdb" in allexports:
                self.cpp_info.components["ncbi_xloader_blastdb"].libs = ["ncbi_xloader_blastdb"]
                self.cpp_info.components["ncbi_xloader_blastdb"].requires = ["ncbi_seqext"]
            if "ncbi_xloader_patcher" in allexports:
                self.cpp_info.components["ncbi_xloader_patcher"].libs = ["ncbi_xloader_patcher"]
                self.cpp_info.components["ncbi_xloader_patcher"].requires = ["ncbi_seqext"]
            if "ncbi_xreader" in allexports:
                self.cpp_info.components["ncbi_xreader"].libs = ["ncbi_xreader"]
                self.cpp_info.components["ncbi_xreader"].requires = ["ncbi_seqext"]
            if "psg_client" in allexports:
                self.cpp_info.components["psg_client"].libs = ["psg_client"]
                self.cpp_info.components["psg_client"].requires = ["ncbi_seqext", "xxconnect2", "UV", "NGHTTP2"]
            if "sraread" in allexports:
                self.cpp_info.components["sraread"].libs = ["sraread"]
                self.cpp_info.components["sraread"].requires = ["ncbi_seqext", "VDB"]
            if "xalgoblastdbindex_search" in allexports:
                self.cpp_info.components["xalgoblastdbindex_search"].libs = ["xalgoblastdbindex_search"]
                self.cpp_info.components["xalgoblastdbindex_search"].requires = ["ncbi_seqext"]
            if "xbiosample_util" in allexports:
                self.cpp_info.components["xbiosample_util"].libs = ["xbiosample_util"]
                self.cpp_info.components["xbiosample_util"].requires = ["xmlwrapp", "ncbi_seqext", "macro"]
            if "xmergetree" in allexports:
                self.cpp_info.components["xmergetree"].libs = ["xmergetree"]
                self.cpp_info.components["xmergetree"].requires = ["ncbi_seqext"]
#5--------------------------------------------------------------------------
            if "dbsnp_tooltip_service" in allexports:
                self.cpp_info.components["dbsnp_tooltip_service"].libs = ["dbsnp_tooltip_service"]
                self.cpp_info.components["dbsnp_tooltip_service"].requires = ["ncbi_trackmgr"]
            if "ncbi_seqext" in allexports:
                self.cpp_info.components["ncbi_seqext"].libs = ["ncbi_seqext"]
                self.cpp_info.components["ncbi_seqext"].requires = ["ncbi_misc", "ncbi_eutils", "ncbi_trackmgr", "LMDB"]
            if "pcassay2" in allexports:
                self.cpp_info.components["pcassay2"].libs = ["pcassay2"]
                self.cpp_info.components["pcassay2"].requires = ["ncbi_misc"]
            if "searchbyrsid" in allexports:
                self.cpp_info.components["searchbyrsid"].libs = ["searchbyrsid"]
                self.cpp_info.components["searchbyrsid"].requires = ["ncbi_trackmgr"]
            if "trackmgrgridcli" in allexports:
                self.cpp_info.components["trackmgrgridcli"].libs = ["trackmgrgridcli"]
                self.cpp_info.components["trackmgrgridcli"].requires = ["ncbi_trackmgr", "LZO"]
            if "xcddalignview" in allexports:
                self.cpp_info.components["xcddalignview"].libs = ["xcddalignview"]
                self.cpp_info.components["xcddalignview"].requires = ["ncbi_mmdb"]
#4--------------------------------------------------------------------------
            if "asn_cache" in allexports:
                self.cpp_info.components["asn_cache"].libs = ["asn_cache"]
                self.cpp_info.components["asn_cache"].requires = ["ncbi_bdb", "ncbi_seq"]
            if "bamread" in allexports:
                self.cpp_info.components["bamread"].libs = ["bamread"]
                self.cpp_info.components["bamread"].requires = ["ncbi_seq", "VDB"]
            if "dbsnp_ptis" in allexports:
                self.cpp_info.components["dbsnp_ptis"].libs = ["dbsnp_ptis"]
                self.cpp_info.components["dbsnp_ptis"].requires = ["ncbi_seq", "grpc_integration", "PROTOBUF", "GRPC", "Z"]
            if "eutils_client" in allexports:
                self.cpp_info.components["eutils_client"].libs = ["eutils_client"]
                self.cpp_info.components["eutils_client"].requires = ["ncbi_seq", "xmlwrapp"]
            if "gencoll_client" in allexports:
                self.cpp_info.components["gencoll_client"].libs = ["gencoll_client"]
                self.cpp_info.components["gencoll_client"].requires = ["ncbi_seq", "sqlitewrapp", "SQLITE3"]
            if "homologene" in allexports:
                self.cpp_info.components["homologene"].libs = ["homologene"]
                self.cpp_info.components["homologene"].requires = ["ncbi_seq"]
            if "local_taxon" in allexports:
                self.cpp_info.components["local_taxon"].libs = ["local_taxon"]
                self.cpp_info.components["local_taxon"].requires = ["ncbi_seq", "sqlitewrapp", "SQLITE3"]
            if "macro" in allexports:
                self.cpp_info.components["macro"].libs = ["macro"]
                self.cpp_info.components["macro"].requires = ["ncbi_seq"]
            if "ncbi_misc" in allexports:
                self.cpp_info.components["ncbi_misc"].libs = ["ncbi_misc"]
                self.cpp_info.components["ncbi_misc"].requires = ["ncbi_seq"]
            if "ncbi_mmdb" in allexports:
                self.cpp_info.components["ncbi_mmdb"].libs = ["ncbi_mmdb"]
                self.cpp_info.components["ncbi_mmdb"].requires = ["ncbi_seq"]
            if "ncbi_trackmgr" in allexports:
                self.cpp_info.components["ncbi_trackmgr"].libs = ["ncbi_trackmgr"]
                self.cpp_info.components["ncbi_trackmgr"].requires = ["ncbi_seq"]
            if "seqalign_util" in allexports:
                self.cpp_info.components["seqalign_util"].libs = ["seqalign_util"]
                self.cpp_info.components["seqalign_util"].requires = ["ncbi_seq", "test_boost", "Boost"]
#3--------------------------------------------------------------------------
            if "dbapi_sample_base" in allexports:
                self.cpp_info.components["dbapi_sample_base"].libs = ["dbapi_sample_base"]
#                self.cpp_info.components["dbapi_sample_base"].requires = ["ncbi_xdbapi_ftds", "ncbi_xdbapi_ftds100", "ncbi_xdbapi_ctlib", "ncbi_xdbapi_odbc", "Sybase", "ODBC"]
                self.cpp_info.components["dbapi_sample_base"].requires = ["ncbi_xdbapi_ftds", "ncbi_xdbapi_ftds100"]
            if "ncbi_seq" in allexports:
                self.cpp_info.components["ncbi_seq"].libs = ["ncbi_seq"]
                self.cpp_info.components["ncbi_seq"].requires = ["ncbi_pub"]
            if "odbc_ftds100" in allexports:
                self.cpp_info.components["odbc_ftds100"].libs = ["odbc_ftds100"]
                self.cpp_info.components["odbc_ftds100"].requires = ["tds_ftds100", "ncbi_xdbapi_odbc", "ODBC"]
            if "python_ncbi_dbapi" in allexports:
                self.cpp_info.components["python_ncbi_dbapi"].libs = ["python_ncbi_dbapi"]
                self.cpp_info.components["python_ncbi_dbapi"].requires = ["ncbi_dbapi", "PYTHON"]
            if "sdbapi" in allexports:
                self.cpp_info.components["sdbapi"].libs = ["sdbapi"]
                self.cpp_info.components["sdbapi"].requires = ["ncbi_dbapi", "dbapi_util_blobstore", "ncbi_xdbapi_ftds", "ncbi_xdbapi_ftds100"]
#2--------------------------------------------------------------------------
            if "ctransition_nlmzip" in allexports:
                self.cpp_info.components["ctransition_nlmzip"].libs = ["ctransition_nlmzip"]
                self.cpp_info.components["ctransition_nlmzip"].requires = ["ctransition"]
            if "dbapi_util_blobstore" in allexports:
                self.cpp_info.components["dbapi_util_blobstore"].libs = ["dbapi_util_blobstore"]
                self.cpp_info.components["dbapi_util_blobstore"].requires = ["ncbi_dbapi_driver"]
            if "hydra_client" in allexports:
                self.cpp_info.components["hydra_client"].libs = ["hydra_client"]
                self.cpp_info.components["hydra_client"].requires = ["xmlwrapp"]
            if "ncbi_dbapi" in allexports:
                self.cpp_info.components["ncbi_dbapi"].libs = ["ncbi_dbapi"]
                self.cpp_info.components["ncbi_dbapi"].requires = ["ncbi_dbapi_driver"]
            if "ncbi_pub" in allexports:
                self.cpp_info.components["ncbi_pub"].libs = ["ncbi_pub"]
                self.cpp_info.components["ncbi_pub"].requires = ["ncbi_general"]
            if "ncbi_xcache_bdb" in allexports:
                self.cpp_info.components["ncbi_xcache_bdb"].libs = ["ncbi_xcache_bdb"]
                self.cpp_info.components["ncbi_xcache_bdb"].requires = ["ncbi_bdb", "BerkeleyDB"]
            if "ncbi_xdbapi_ctlib" in allexports:
                self.cpp_info.components["ncbi_xdbapi_ctlib"].libs = ["ncbi_xdbapi_ctlib"]
                self.cpp_info.components["ncbi_xdbapi_ctlib"].requires = ["ncbi_dbapi_driver", "Sybase"]
            if "ncbi_xdbapi_ftds" in allexports:
                self.cpp_info.components["ncbi_xdbapi_ftds"].libs = ["ncbi_xdbapi_ftds"]
                self.cpp_info.components["ncbi_xdbapi_ftds"].requires = ["ncbi_dbapi_driver", "ct_ftds100"]
            if "ncbi_xdbapi_ftds100" in allexports:
                self.cpp_info.components["ncbi_xdbapi_ftds100"].libs = ["ncbi_xdbapi_ftds100"]
                self.cpp_info.components["ncbi_xdbapi_ftds100"].requires = ["ct_ftds100", "ncbi_dbapi_driver"]
            if "ncbi_xdbapi_mysql" in allexports:
                self.cpp_info.components["ncbi_xdbapi_mysql"].libs = ["ncbi_xdbapi_mysql"]
                self.cpp_info.components["ncbi_xdbapi_mysql"].requires = ["ncbi_dbapi_driver"]
            if "ncbi_xdbapi_odbc" in allexports:
                self.cpp_info.components["ncbi_xdbapi_odbc"].libs = ["ncbi_xdbapi_odbc"]
                self.cpp_info.components["ncbi_xdbapi_odbc"].requires = ["ncbi_dbapi_driver", "ODBC", "SQLServer"]
            if "ncbi_xgrid2cgi" in allexports:
                self.cpp_info.components["ncbi_xgrid2cgi"].libs = ["ncbi_xgrid2cgi"]
                self.cpp_info.components["ncbi_xgrid2cgi"].requires = ["ncbi_web"]
            if "netstorage" in allexports:
                self.cpp_info.components["netstorage"].libs = ["netstorage"]
                self.cpp_info.components["netstorage"].requires = ["ncbi_xcache_netcache"]
            if "pmcidconv_client" in allexports:
                self.cpp_info.components["pmcidconv_client"].libs = ["pmcidconv_client"]
                self.cpp_info.components["pmcidconv_client"].requires = ["xmlwrapp"]
            if "psg_cache" in allexports:
                self.cpp_info.components["psg_cache"].libs = ["psg_cache"]
                self.cpp_info.components["psg_cache"].requires = ["psg_protobuf", "psg_cassandra", "LMDB", "PROTOBUF"]
            if "sample_asn" in allexports:
                self.cpp_info.components["sample_asn"].libs = ["sample_asn"]
                self.cpp_info.components["sample_asn"].requires = ["ncbi_general"]
            if "xasn" in allexports:
                self.cpp_info.components["xasn"].libs = ["xasn"]
                self.cpp_info.components["xasn"].requires = ["ncbi_web", "NCBI_C"]
            if "xfcgi_mt" in allexports:
                self.cpp_info.components["xfcgi_mt"].libs = ["xfcgi_mt"]
                self.cpp_info.components["xfcgi_mt"].requires = ["ncbi_web"]
            if "xmlreaders" in allexports:
                self.cpp_info.components["xmlreaders"].libs = ["xmlreaders"]
                self.cpp_info.components["xmlreaders"].requires = ["xmlwrapp"]
            if "xsoap_server" in allexports:
                self.cpp_info.components["xsoap_server"].libs = ["xsoap_server"]
                self.cpp_info.components["xsoap_server"].requires = ["ncbi_web", "xsoap"]
#1--------------------------------------------------------------------------
            if "asn_sample_lib" in allexports:
                self.cpp_info.components["asn_sample_lib"].libs = ["asn_sample_lib"]
                self.cpp_info.components["asn_sample_lib"].requires = ["ncbi_core"]
            if "basic_sample_lib" in allexports:
                self.cpp_info.components["basic_sample_lib"].libs = ["basic_sample_lib"]
                self.cpp_info.components["basic_sample_lib"].requires = ["ncbi_core"]
            if "ct_ftds100" in allexports:
                self.cpp_info.components["ct_ftds100"].libs = ["ct_ftds100"]
                self.cpp_info.components["ct_ftds100"].requires = ["tds_ftds100"]
            if "ctransition" in allexports:
                self.cpp_info.components["ctransition"].libs = ["ctransition"]
                self.cpp_info.components["ctransition"].requires = ["ncbi_core"]
            if "dtd_sample_lib" in allexports:
                self.cpp_info.components["dtd_sample_lib"].libs = ["dtd_sample_lib"]
                self.cpp_info.components["dtd_sample_lib"].requires = ["ncbi_core"]
            if "grpc_integration" in allexports:
                self.cpp_info.components["grpc_integration"].libs = ["grpc_integration"]
                self.cpp_info.components["grpc_integration"].requires = ["ncbi_core", "GRPC", "Z"]
            if "gumbelparams" in allexports:
                self.cpp_info.components["gumbelparams"].libs = ["gumbelparams"]
                self.cpp_info.components["gumbelparams"].requires = ["ncbi_core"]
            if "jaeger_tracer" in allexports:
                self.cpp_info.components["jaeger_tracer"].libs = ["jaeger_tracer"]
                self.cpp_info.components["jaeger_tracer"].requires = ["ncbi_core"]
            if "jsd_sample_lib" in allexports:
                self.cpp_info.components["jsd_sample_lib"].libs = ["jsd_sample_lib"]
                self.cpp_info.components["jsd_sample_lib"].requires = ["ncbi_core"]
            if "msbuild_dataobj" in allexports:
                self.cpp_info.components["msbuild_dataobj"].libs = ["msbuild_dataobj"]
                self.cpp_info.components["msbuild_dataobj"].requires = ["ncbi_core"]
            if "ncbi_bdb" in allexports:
                self.cpp_info.components["ncbi_bdb"].libs = ["ncbi_bdb"]
                self.cpp_info.components["ncbi_bdb"].requires = ["ncbi_core", "BerkeleyDB"]
            if "ncbi_dbapi_driver" in allexports:
                self.cpp_info.components["ncbi_dbapi_driver"].libs = ["ncbi_dbapi_driver"]
                self.cpp_info.components["ncbi_dbapi_driver"].requires = ["ncbi_core"]
            if "ncbi_eutils" in allexports:
                self.cpp_info.components["ncbi_eutils"].libs = ["ncbi_eutils"]
                self.cpp_info.components["ncbi_eutils"].requires = ["ncbi_core"]
            if "ncbi_general" in allexports:
                self.cpp_info.components["ncbi_general"].libs = ["ncbi_general"]
                self.cpp_info.components["ncbi_general"].requires = ["ncbi_core"]
            if "ncbi_image" in allexports:
                self.cpp_info.components["ncbi_image"].libs = ["ncbi_image"]
                self.cpp_info.components["ncbi_image"].requires = ["ncbi_core", "Z", "JPEG", "PNG", "GIF", "TIFF"]
            if "ncbi_web" in allexports:
                self.cpp_info.components["ncbi_web"].libs = ["ncbi_web"]
                self.cpp_info.components["ncbi_web"].requires = ["ncbi_core"]
            if "ncbi_xblobstorage_netcache" in allexports:
                self.cpp_info.components["ncbi_xblobstorage_netcache"].libs = ["ncbi_xblobstorage_netcache"]
                self.cpp_info.components["ncbi_xblobstorage_netcache"].requires = ["ncbi_core"]
            if "ncbi_xcache_netcache" in allexports:
                self.cpp_info.components["ncbi_xcache_netcache"].libs = ["ncbi_xcache_netcache"]
                self.cpp_info.components["ncbi_xcache_netcache"].requires = ["ncbi_core"]
            if "psg_cassandra" in allexports:
                self.cpp_info.components["psg_cassandra"].libs = ["psg_cassandra"]
                self.cpp_info.components["psg_cassandra"].requires = ["ncbi_core"]
            if "psg_diag" in allexports:
                self.cpp_info.components["psg_diag"].libs = ["psg_diag"]
                self.cpp_info.components["psg_diag"].requires = ["ncbi_core"]
            if "soap_dataobj" in allexports:
                self.cpp_info.components["soap_dataobj"].libs = ["soap_dataobj"]
                self.cpp_info.components["soap_dataobj"].requires = ["ncbi_core"]
            if "sqlitewrapp" in allexports:
                self.cpp_info.components["sqlitewrapp"].libs = ["sqlitewrapp"]
                self.cpp_info.components["sqlitewrapp"].requires = ["ncbi_core", "SQLITE3"]
            if "sybdb_ftds100" in allexports:
                self.cpp_info.components["sybdb_ftds100"].libs = ["sybdb_ftds100"]
                self.cpp_info.components["sybdb_ftds100"].requires = ["tds_ftds100"]
            if "test_boost" in allexports:
                self.cpp_info.components["test_boost"].libs = ["test_boost"]
                self.cpp_info.components["test_boost"].requires = ["ncbi_core", "Boost"]
            if "test_mt" in allexports:
                self.cpp_info.components["test_mt"].libs = ["test_mt"]
                self.cpp_info.components["test_mt"].requires = ["ncbi_core"]
            if "utrtprof" in allexports:
                self.cpp_info.components["utrtprof"].libs = ["utrtprof"]
                self.cpp_info.components["utrtprof"].requires = ["ncbi_core"]
            if "varrep" in allexports:
                self.cpp_info.components["varrep"].libs = ["varrep"]
                self.cpp_info.components["varrep"].requires = ["ncbi_core"]
            if "wx_tools" in allexports:
                self.cpp_info.components["wx_tools"].libs = ["wx_tools"]
                self.cpp_info.components["wx_tools"].requires = ["ncbi_core", "wxWidgets"]
            if "xalgovmerge" in allexports:
                self.cpp_info.components["xalgovmerge"].libs = ["xalgovmerge"]
                self.cpp_info.components["xalgovmerge"].requires = ["ncbi_core"]
            if "xcser" in allexports:
                self.cpp_info.components["xcser"].libs = ["xcser"]
                self.cpp_info.components["xcser"].requires = ["ncbi_core"]
            if "xctools" in allexports:
                self.cpp_info.components["xctools"].libs = ["xctools"]
                self.cpp_info.components["xctools"].requires = ["ncbi_core", "NCBI_C"]
            if "xfcgi" in allexports:
                self.cpp_info.components["xfcgi"].libs = ["xfcgi"]
                self.cpp_info.components["xfcgi"].requires = ["ncbi_core", "FASTCGI"]
            if "xmlwrapp" in allexports:
                self.cpp_info.components["xmlwrapp"].libs = ["xmlwrapp"]
                self.cpp_info.components["xmlwrapp"].requires = ["ncbi_core", "XML", "XSLT"]
            if "xpbacktest" in allexports:
                self.cpp_info.components["xpbacktest"].libs = ["xpbacktest"]
                self.cpp_info.components["xpbacktest"].requires = ["ncbi_core"]
            if "xregexp_template_tester" in allexports:
                self.cpp_info.components["xregexp_template_tester"].libs = ["xregexp_template_tester"]
                self.cpp_info.components["xregexp_template_tester"].requires = ["ncbi_core", "PCRE"]
            if "xsd_sample_lib" in allexports:
                self.cpp_info.components["xsd_sample_lib"].libs = ["xsd_sample_lib"]
                self.cpp_info.components["xsd_sample_lib"].requires = ["ncbi_core"]
            if "xsoap" in allexports:
                self.cpp_info.components["xsoap"].libs = ["xsoap"]
                self.cpp_info.components["xsoap"].requires = ["ncbi_core"]
            if "xxconnect2" in allexports:
                self.cpp_info.components["xxconnect2"].libs = ["xxconnect2"]
                self.cpp_info.components["xxconnect2"].requires = ["ncbi_core", "UV", "NGHTTP2"]
#0--------------------------------------------------------------------------
            if "clog" in allexports:
                self.cpp_info.components["clog"].libs = ["clog"]
                self.cpp_info.components["clog"].requires = ["ORIGLIBS"]
            if "edit_imgt_file" in allexports:
                self.cpp_info.components["edit_imgt_file"].libs = ["edit_imgt_file"]
                self.cpp_info.components["edit_imgt_file"].requires = ["ORIGLIBS"]
            if "lapackwrapp" in allexports:
                self.cpp_info.components["lapackwrapp"].libs = ["lapackwrapp"]
                self.cpp_info.components["lapackwrapp"].requires = ["ORIGLIBS"]
            if "ncbi_core" in allexports:
                self.cpp_info.components["ncbi_core"].libs = ["ncbi_core"]
                self.cpp_info.components["ncbi_core"].requires = ["PCRE", "Z", "BZ2", "LZO", "ORIGLIBS"]
            if "psg_protobuf" in allexports:
                self.cpp_info.components["psg_protobuf"].libs = ["psg_protobuf"]
                self.cpp_info.components["psg_protobuf"].requires = ["PROTOBUF", "ORIGLIBS"]
            if "task_server" in allexports:
                self.cpp_info.components["task_server"].libs = ["task_server"]
                self.cpp_info.components["task_server"].requires = ["Boost", "ORIGLIBS"]
            if "tds_ftds100" in allexports:
                self.cpp_info.components["tds_ftds100"].libs = ["tds_ftds100"]
                self.cpp_info.components["tds_ftds100"].requires = ["ORIGLIBS"]
            if "test_dll" in allexports:
                self.cpp_info.components["test_dll"].libs = ["test_dll"]
                self.cpp_info.components["test_dll"].requires = ["ORIGLIBS"]
        else:
#============================================================================
#18--------------------------------------------------------------------------
            if "xaligncleanup" in allexports:
                self.cpp_info.components["xaligncleanup"].libs = ["xaligncleanup"]
                self.cpp_info.components["xaligncleanup"].requires = ["xalgoalignsplign", "prosplign"]
            if "xbma_refiner_gui" in allexports:
                self.cpp_info.components["xbma_refiner_gui"].libs = ["xbma_refiner_gui"]
                self.cpp_info.components["xbma_refiner_gui"].requires = ["xbma_refiner", "wx_tools", "wxWidgets"]
#17--------------------------------------------------------------------------
            if "blast_app_util" in allexports:
                self.cpp_info.components["blast_app_util"].libs = ["blast_app_util"]
                self.cpp_info.components["blast_app_util"].requires = ["blastdb", "xnetblast", "blastinput", "xblastformat"]
            if "prosplign" in allexports:
                self.cpp_info.components["prosplign"].libs = ["prosplign"]
                self.cpp_info.components["prosplign"].requires = ["xalgoalignutil"]
            if "vdb2blast" in allexports:
                self.cpp_info.components["vdb2blast"].libs = ["vdb2blast"]
                self.cpp_info.components["vdb2blast"].requires = ["xblast", "blastinput", "VDB"]
            if "xalgoalignsplign" in allexports:
                self.cpp_info.components["xalgoalignsplign"].libs = ["xalgoalignsplign"]
                self.cpp_info.components["xalgoalignsplign"].requires = ["xalgoalignnw", "xalgoalignutil"]
            if "xbma_refiner" in allexports:
                self.cpp_info.components["xbma_refiner"].libs = ["xbma_refiner"]
                self.cpp_info.components["xbma_refiner"].requires = ["xcd_utils", "xstruct_util", "cdd"]
            if "xngalign" in allexports:
                self.cpp_info.components["xngalign"].libs = ["xngalign"]
                self.cpp_info.components["xngalign"].requires = ["blastinput", "xalgoalignnw", "xalgoalignutil", "xmergetree"]
#16--------------------------------------------------------------------------
            if "blastinput" in allexports:
                self.cpp_info.components["blastinput"].libs = ["blastinput"]
                self.cpp_info.components["blastinput"].requires = ["seqset", "xnetblast", "align_format", "ncbi_xloader_blastdb_rmt", "xblast"]
            if "cobalt" in allexports:
                self.cpp_info.components["cobalt"].libs = ["cobalt"]
                self.cpp_info.components["cobalt"].requires = ["xalgoalignnw", "xalgophytree", "xblast"]
            if "igblast" in allexports:
                self.cpp_info.components["igblast"].libs = ["igblast"]
                self.cpp_info.components["igblast"].requires = ["xalnmgr", "xblast"]
            if "proteinkmer" in allexports:
                self.cpp_info.components["proteinkmer"].libs = ["proteinkmer"]
                self.cpp_info.components["proteinkmer"].requires = ["xblast"]
            if "xalgoalignutil" in allexports:
                self.cpp_info.components["xalgoalignutil"].libs = ["xalgoalignutil"]
                self.cpp_info.components["xalgoalignutil"].requires = ["xalgoseq", "xblast", "xqueryparse"]
            if "xalgocontig_assembly" in allexports:
                self.cpp_info.components["xalgocontig_assembly"].libs = ["xalgocontig_assembly"]
                self.cpp_info.components["xalgocontig_assembly"].requires = ["xalgoalignnw", "xalnmgr", "xblast"]
            if "xblastformat" in allexports:
                self.cpp_info.components["xblastformat"].libs = ["xblastformat"]
                self.cpp_info.components["xblastformat"].requires = ["blastxml", "blastxml2", "align_format", "xblast", "xformat"]
            if "xcd_utils" in allexports:
                self.cpp_info.components["xcd_utils"].libs = ["xcd_utils"]
                self.cpp_info.components["xcd_utils"].requires = ["blast_services", "entrez2cli", "id1cli", "ncbimime", "taxon1", "xblast", "xregexp"]
            if "xstruct_util" in allexports:
                self.cpp_info.components["xstruct_util"].libs = ["xstruct_util"]
                self.cpp_info.components["xstruct_util"].requires = ["xblast", "xstruct_dp"]
#15--------------------------------------------------------------------------
            if "phytree_format" in allexports:
                self.cpp_info.components["phytree_format"].libs = ["phytree_format"]
                self.cpp_info.components["phytree_format"].requires = ["align_format", "xalgophytree", "blastdb", "scoremat"]
            if "xalgoseqqa" in allexports:
                self.cpp_info.components["xalgoseqqa"].libs = ["xalgoseqqa"]
                self.cpp_info.components["xalgoseqqa"].requires = ["entrez2cli", "seqtest", "xalgognomon"]
            if "xalntool" in allexports:
                self.cpp_info.components["xalntool"].libs = ["xalntool"]
                self.cpp_info.components["xalntool"].requires = ["align_format"]
            if "xblast" in allexports:
                self.cpp_info.components["xblast"].libs = ["xblast"]
                self.cpp_info.components["xblast"].requires = ["xalgoblastdbindex", "xalgodustmask", "xalgowinmask", "xnetblastcli", "seq", "blastdb", "utrtprof"]
            if "xobjwrite" in allexports:
                self.cpp_info.components["xobjwrite"].libs = ["xobjwrite"]
                self.cpp_info.components["xobjwrite"].requires = ["variation_utils", "xformat", "xobjread"]
            if "xvalidate" in allexports:
                self.cpp_info.components["xvalidate"].libs = ["xvalidate"]
                self.cpp_info.components["xvalidate"].requires = ["taxon1", "valerr", "xformat", "xobjedit", "submit", "taxon3"]
#14--------------------------------------------------------------------------
            if "align_format" in allexports:
                self.cpp_info.components["align_format"].libs = ["align_format"]
                self.cpp_info.components["align_format"].requires = ["blast_services", "gene_info", "ncbi_xloader_genbank", "seqdb", "taxon1", "xalnmgr", "xcgi", "xhtml", "xobjread"]
            if "blast_unit_test_util" in allexports:
                self.cpp_info.components["blast_unit_test_util"].libs = ["blast_unit_test_util"]
                self.cpp_info.components["blast_unit_test_util"].requires = ["blastdb", "xnetblast", "blast", "ncbi_xloader_genbank", "test_boost", "xobjutil", "Boost"]
            if "data_loaders_util" in allexports:
                self.cpp_info.components["data_loaders_util"].libs = ["data_loaders_util"]
#                self.cpp_info.components["data_loaders_util"].requires = ["ncbi_xdbapi_ftds", "ncbi_xloader_asn_cache", "ncbi_xloader_blastdb", "ncbi_xloader_genbank", "ncbi_xloader_lds2", "ncbi_xreader_pubseqos", "ncbi_xreader_pubseqos2", "ncbi_xloader_csra", "ncbi_xloader_wgs"]
                self.cpp_info.components["data_loaders_util"].requires = ["ncbi_xdbapi_ftds", "ncbi_xloader_asn_cache", "ncbi_xloader_blastdb", "ncbi_xloader_genbank", "ncbi_xloader_lds2", "ncbi_xreader_pubseqos", "ncbi_xreader_pubseqos2"]
            if "hgvs" in allexports:
                self.cpp_info.components["hgvs"].libs = ["hgvs"]
                self.cpp_info.components["hgvs"].requires = ["entrez2cli", "ncbi_xloader_genbank", "objcoords", "variation", "xobjread", "xobjutil", "xregexp", "seq", "Boost"]
            if "ncbi_xloader_blastdb_rmt" in allexports:
                self.cpp_info.components["ncbi_xloader_blastdb_rmt"].libs = ["ncbi_xloader_blastdb_rmt"]
                self.cpp_info.components["ncbi_xloader_blastdb_rmt"].requires = ["blast_services", "ncbi_xloader_blastdb"]
            if "xalgognomon" in allexports:
                self.cpp_info.components["xalgognomon"].libs = ["xalgognomon"]
                self.cpp_info.components["xalgognomon"].requires = ["xalgoseq"]
            if "xalgowinmask" in allexports:
                self.cpp_info.components["xalgowinmask"].libs = ["xalgowinmask"]
                self.cpp_info.components["xalgowinmask"].requires = ["submit", "seqmasks_io"]
            if "xdiscrepancy" in allexports:
                self.cpp_info.components["xdiscrepancy"].libs = ["xdiscrepancy"]
                self.cpp_info.components["xdiscrepancy"].requires = ["xcompress", "macro", "xcleanup", "xobjedit"]
            if "xflatfile" in allexports:
                self.cpp_info.components["xflatfile"].libs = ["xflatfile"]
                self.cpp_info.components["xflatfile"].requires = ["xcleanup", "xlogging", "ncbi_xdbapi_ftds", "taxon1", "ncbi_xloader_genbank"]
            if "xformat" in allexports:
                self.cpp_info.components["xformat"].libs = ["xformat"]
                self.cpp_info.components["xformat"].requires = ["gbseq", "mlacli", "xalnmgr", "xcleanup"]
            if "xobjsimple" in allexports:
                self.cpp_info.components["xobjsimple"].libs = ["xobjsimple"]
                self.cpp_info.components["xobjsimple"].requires = ["ncbi_xloader_genbank", "seqset"]
            if "xprimer" in allexports:
                self.cpp_info.components["xprimer"].libs = ["xprimer"]
                self.cpp_info.components["xprimer"].requires = ["gene_info", "ncbi_xloader_genbank", "xalgoalignnw", "xalnmgr"]
#13--------------------------------------------------------------------------
            if "blastdb_format" in allexports:
                self.cpp_info.components["blastdb_format"].libs = ["blastdb_format"]
                self.cpp_info.components["blastdb_format"].requires = ["seqdb", "xobjutil", "seqset"]
            if "fix_pub" in allexports:
                self.cpp_info.components["fix_pub"].libs = ["fix_pub"]
                self.cpp_info.components["fix_pub"].requires = ["mlacli", "eutils_client", "xobjedit"]
            if "gene_info_writer" in allexports:
                self.cpp_info.components["gene_info_writer"].libs = ["gene_info_writer"]
                self.cpp_info.components["gene_info_writer"].requires = ["gene_info", "seqdb"]
            if "ncbi_xloader_bam" in allexports:
                self.cpp_info.components["ncbi_xloader_bam"].libs = ["ncbi_xloader_bam"]
                self.cpp_info.components["ncbi_xloader_bam"].requires = ["bamread", "xobjreadex", "seqset", "VDB"]
            if "ncbi_xloader_blastdb" in allexports:
                self.cpp_info.components["ncbi_xloader_blastdb"].libs = ["ncbi_xloader_blastdb"]
                self.cpp_info.components["ncbi_xloader_blastdb"].requires = ["seqdb", "seqset"]
            if "ncbi_xloader_genbank" in allexports:
                self.cpp_info.components["ncbi_xloader_genbank"].libs = ["ncbi_xloader_genbank"]
                self.cpp_info.components["ncbi_xloader_genbank"].requires = ["libgeneral", "ncbi_xreader_cache", "ncbi_xreader_id1", "ncbi_xreader_id2", "psg_client"]
            if "seqmasks_io" in allexports:
                self.cpp_info.components["seqmasks_io"].libs = ["seqmasks_io"]
                self.cpp_info.components["seqmasks_io"].requires = ["seqdb", "xobjread", "xobjutil"]
            if "writedb" in allexports:
                self.cpp_info.components["writedb"].libs = ["writedb"]
                self.cpp_info.components["writedb"].requires = ["seqdb", "xobjread", "LMDB"]
            if "xalgoblastdbindex" in allexports:
                self.cpp_info.components["xalgoblastdbindex"].libs = ["xalgoblastdbindex"]
                self.cpp_info.components["xalgoblastdbindex"].requires = ["blast", "seqdb", "xobjread", "xobjutil"]
            if "xalgophytree" in allexports:
                self.cpp_info.components["xalgophytree"].libs = ["xalgophytree"]
                self.cpp_info.components["xalgophytree"].requires = ["biotree", "fastme", "xalnmgr"]
            if "xalgoseq" in allexports:
                self.cpp_info.components["xalgoseq"].libs = ["xalgoseq"]
                self.cpp_info.components["xalgoseq"].requires = ["taxon1", "xalnmgr", "xregexp"]
            if "xbiosample_util" in allexports:
                self.cpp_info.components["xbiosample_util"].libs = ["xbiosample_util"]
                self.cpp_info.components["xbiosample_util"].requires = ["xmlwrapp", "xobjedit", "taxon3", "seqset", "macro", "valid"]
            if "xcleanup" in allexports:
                self.cpp_info.components["xcleanup"].libs = ["xcleanup"]
                self.cpp_info.components["xcleanup"].requires = ["xobjedit"]
            if "xomssa" in allexports:
                self.cpp_info.components["xomssa"].libs = ["xomssa"]
                self.cpp_info.components["xomssa"].requires = ["blast", "omssa", "pepXML", "seqdb", "xcompress", "xconnect", "xregexp"]
#12--------------------------------------------------------------------------
            if "blast_services" in allexports:
                self.cpp_info.components["blast_services"].libs = ["blast_services"]
                self.cpp_info.components["blast_services"].requires = ["xnetblastcli"]
            if "blast_sra_input" in allexports:
                self.cpp_info.components["blast_sra_input"].libs = ["blast_sra_input"]
                self.cpp_info.components["blast_sra_input"].requires = ["sraread", "blastdb", "VDB"]
            if "ncbi_xloader_cdd" in allexports:
                self.cpp_info.components["ncbi_xloader_cdd"].libs = ["ncbi_xloader_cdd"]
                self.cpp_info.components["ncbi_xloader_cdd"].requires = ["cdd_access", "xcompress", "seq", "xobjmgr"]
            if "ncbi_xloader_csra" in allexports:
                self.cpp_info.components["ncbi_xloader_csra"].libs = ["ncbi_xloader_csra"]
                self.cpp_info.components["ncbi_xloader_csra"].requires = ["sraread", "seqset", "VDB"]
            if "ncbi_xloader_lds2" in allexports:
                self.cpp_info.components["ncbi_xloader_lds2"].libs = ["ncbi_xloader_lds2"]
                self.cpp_info.components["ncbi_xloader_lds2"].requires = ["lds2", "xobjmgr", "seq"]
            if "ncbi_xloader_snp" in allexports:
                self.cpp_info.components["ncbi_xloader_snp"].libs = ["ncbi_xloader_snp"]
                self.cpp_info.components["ncbi_xloader_snp"].requires = ["sraread", "seqset", "seq", "dbsnp_ptis", "grpc_integration", "VDB", "GRPC"]
            if "ncbi_xloader_sra" in allexports:
                self.cpp_info.components["ncbi_xloader_sra"].libs = ["ncbi_xloader_sra"]
                self.cpp_info.components["ncbi_xloader_sra"].requires = ["sraread", "seqset", "VDB"]
            if "ncbi_xloader_vdbgraph" in allexports:
                self.cpp_info.components["ncbi_xloader_vdbgraph"].libs = ["ncbi_xloader_vdbgraph"]
                self.cpp_info.components["ncbi_xloader_vdbgraph"].requires = ["sraread", "seqset", "VDB"]
            if "ncbi_xloader_wgs" in allexports:
                self.cpp_info.components["ncbi_xloader_wgs"].libs = ["ncbi_xloader_wgs"]
                self.cpp_info.components["ncbi_xloader_wgs"].requires = ["sraread", "seqset", "VDB"]
            if "ncbi_xreader_cache" in allexports:
                self.cpp_info.components["ncbi_xreader_cache"].libs = ["ncbi_xreader_cache"]
                self.cpp_info.components["ncbi_xreader_cache"].requires = ["ncbi_xreader"]
            if "ncbi_xreader_gicache" in allexports:
                self.cpp_info.components["ncbi_xreader_gicache"].libs = ["ncbi_xreader_gicache"]
                self.cpp_info.components["ncbi_xreader_gicache"].requires = ["ncbi_xreader", "LMDB"]
            if "ncbi_xreader_id1" in allexports:
                self.cpp_info.components["ncbi_xreader_id1"].libs = ["ncbi_xreader_id1"]
                self.cpp_info.components["ncbi_xreader_id1"].requires = ["ncbi_xreader"]
            if "ncbi_xreader_id2" in allexports:
                self.cpp_info.components["ncbi_xreader_id2"].libs = ["ncbi_xreader_id2"]
                self.cpp_info.components["ncbi_xreader_id2"].requires = ["ncbi_xreader"]
            if "ncbi_xreader_pubseqos" in allexports:
                self.cpp_info.components["ncbi_xreader_pubseqos"].libs = ["ncbi_xreader_pubseqos"]
                self.cpp_info.components["ncbi_xreader_pubseqos"].requires = ["dbapi_driver", "ncbi_xreader"]
            if "ncbi_xreader_pubseqos2" in allexports:
                self.cpp_info.components["ncbi_xreader_pubseqos2"].libs = ["ncbi_xreader_pubseqos2"]
                self.cpp_info.components["ncbi_xreader_pubseqos2"].requires = ["dbapi_driver", "ncbi_xreader", "eMyNCBI_result"]
            if "seqalign_util" in allexports:
                self.cpp_info.components["seqalign_util"].libs = ["seqalign_util"]
                self.cpp_info.components["seqalign_util"].requires = ["blastdb", "seq", "test_boost", "Boost"]
            if "seqdb" in allexports:
                self.cpp_info.components["seqdb"].libs = ["seqdb"]
                self.cpp_info.components["seqdb"].requires = ["blastdb", "xobjmgr", "LMDB"]
            if "variation_utils" in allexports:
                self.cpp_info.components["variation_utils"].libs = ["variation_utils"]
                self.cpp_info.components["variation_utils"].requires = ["variation", "xobjutil", "blastdb", "genome_collection"]
            if "xalnmgr" in allexports:
                self.cpp_info.components["xalnmgr"].libs = ["xalnmgr"]
                self.cpp_info.components["xalnmgr"].requires = ["tables", "xobjutil", "seqset"]
            if "xcddalignview" in allexports:
                self.cpp_info.components["xcddalignview"].libs = ["xcddalignview"]
                self.cpp_info.components["xcddalignview"].requires = ["seq", "ncbimime"]
            if "xobjedit" in allexports:
                self.cpp_info.components["xobjedit"].libs = ["xobjedit"]
                self.cpp_info.components["xobjedit"].requires = ["eutils", "esearch", "esummary", "mlacli", "taxon3", "valid", "xobjread", "xobjutil", "xlogging"]
            if "xobjimport" in allexports:
                self.cpp_info.components["xobjimport"].libs = ["xobjimport"]
                self.cpp_info.components["xobjimport"].requires = ["xobjutil"]
            if "xobjreadex" in allexports:
                self.cpp_info.components["xobjreadex"].libs = ["xobjreadex"]
                self.cpp_info.components["xobjreadex"].requires = ["xobjread", "xobjutil", "seqset"]
            if "xunittestutil" in allexports:
                self.cpp_info.components["xunittestutil"].libs = ["xunittestutil"]
                self.cpp_info.components["xunittestutil"].requires = ["xobjutil"]
#11--------------------------------------------------------------------------
            if "blastdb" in allexports:
                self.cpp_info.components["blastdb"].libs = ["blastdb"]
                self.cpp_info.components["blastdb"].requires = ["xnetblast"]
            if "cdd_access" in allexports:
                self.cpp_info.components["cdd_access"].libs = ["cdd_access"]
                self.cpp_info.components["cdd_access"].requires = ["id2", "xconnect"]
            if "eMyNCBI_result" in allexports:
                self.cpp_info.components["eMyNCBI_result"].libs = ["eMyNCBI_result"]
                self.cpp_info.components["eMyNCBI_result"].requires = ["seqset", "id2"]
            if "id2_split" in allexports:
                self.cpp_info.components["id2_split"].libs = ["id2_split"]
                self.cpp_info.components["id2_split"].requires = ["xcompress", "xobjmgr"]
            if "id2cli" in allexports:
                self.cpp_info.components["id2cli"].libs = ["id2cli"]
                self.cpp_info.components["id2cli"].requires = ["id2", "xconnect"]
            if "lds2" in allexports:
                self.cpp_info.components["lds2"].libs = ["lds2"]
                self.cpp_info.components["lds2"].requires = ["xcompress", "xobjread", "sqlitewrapp", "SQLITE3"]
            if "ncbi_xloader_asn_cache" in allexports:
                self.cpp_info.components["ncbi_xloader_asn_cache"].libs = ["ncbi_xloader_asn_cache"]
                self.cpp_info.components["ncbi_xloader_asn_cache"].requires = ["libgeneral", "asn_cache", "xobjmgr"]
            if "ncbi_xloader_patcher" in allexports:
                self.cpp_info.components["ncbi_xloader_patcher"].libs = ["ncbi_xloader_patcher"]
                self.cpp_info.components["ncbi_xloader_patcher"].requires = ["xobjmgr"]
            if "ncbi_xreader" in allexports:
                self.cpp_info.components["ncbi_xreader"].libs = ["ncbi_xreader"]
                self.cpp_info.components["ncbi_xreader"].requires = ["id1", "id2", "xcompress", "xconnect", "xobjmgr"]
            if "ncbimime" in allexports:
                self.cpp_info.components["ncbimime"].libs = ["ncbimime"]
                self.cpp_info.components["ncbimime"].requires = ["cdd"]
            if "psg_client" in allexports:
                self.cpp_info.components["psg_client"].libs = ["psg_client"]
                self.cpp_info.components["psg_client"].requires = ["id2", "seqsplit", "xconnserv", "xxconnect2", "UV", "NGHTTP2"]
            if "snputil" in allexports:
                self.cpp_info.components["snputil"].libs = ["snputil"]
                self.cpp_info.components["snputil"].requires = ["variation", "xobjmgr", "seqset"]
            if "sraread" in allexports:
                self.cpp_info.components["sraread"].libs = ["sraread"]
                self.cpp_info.components["sraread"].requires = ["xobjmgr", "VDB"]
            if "uudutil" in allexports:
                self.cpp_info.components["uudutil"].libs = ["uudutil"]
                self.cpp_info.components["uudutil"].requires = ["gbproj", "xcompress", "xconnserv"]
            if "xalgoalignnw" in allexports:
                self.cpp_info.components["xalgoalignnw"].libs = ["xalgoalignnw"]
                self.cpp_info.components["xalgoalignnw"].requires = ["tables", "xobjmgr", "seq"]
            if "xalgoblastdbindex_search" in allexports:
                self.cpp_info.components["xalgoblastdbindex_search"].libs = ["xalgoblastdbindex_search"]
                self.cpp_info.components["xalgoblastdbindex_search"].requires = ["seqset", "xobjmgr"]
            if "xalgodustmask" in allexports:
                self.cpp_info.components["xalgodustmask"].libs = ["xalgodustmask"]
                self.cpp_info.components["xalgodustmask"].requires = ["seqset", "xobjmgr"]
            if "xalgosegmask" in allexports:
                self.cpp_info.components["xalgosegmask"].libs = ["xalgosegmask"]
                self.cpp_info.components["xalgosegmask"].requires = ["blast", "xobjmgr", "seqset"]
            if "xid_mapper" in allexports:
                self.cpp_info.components["xid_mapper"].libs = ["xid_mapper"]
                self.cpp_info.components["xid_mapper"].requires = ["xobjmgr", "seqset", "sqlitewrapp"]
            if "xmergetree" in allexports:
                self.cpp_info.components["xmergetree"].libs = ["xmergetree"]
                self.cpp_info.components["xmergetree"].requires = ["xobjmgr", "seqset"]
            if "xnetblastcli" in allexports:
                self.cpp_info.components["xnetblastcli"].libs = ["xnetblastcli"]
                self.cpp_info.components["xnetblastcli"].requires = ["xconnect", "xnetblast"]
            if "xobjutil" in allexports:
                self.cpp_info.components["xobjutil"].libs = ["xobjutil"]
                self.cpp_info.components["xobjutil"].requires = ["submit", "xobjmgr"]
#10--------------------------------------------------------------------------
            if "cdd" in allexports:
                self.cpp_info.components["cdd"].libs = ["cdd"]
                self.cpp_info.components["cdd"].requires = ["cn3d", "scoremat"]
            if "gbproj" in allexports:
                self.cpp_info.components["gbproj"].libs = ["gbproj"]
                self.cpp_info.components["gbproj"].requires = ["submit", "xconnect"]
            if "id1cli" in allexports:
                self.cpp_info.components["id1cli"].libs = ["id1cli"]
                self.cpp_info.components["id1cli"].requires = ["id1", "xconnect"]
            if "id2" in allexports:
                self.cpp_info.components["id2"].libs = ["id2"]
                self.cpp_info.components["id2"].requires = ["seqsplit"]
            if "xnetblast" in allexports:
                self.cpp_info.components["xnetblast"].libs = ["xnetblast"]
                self.cpp_info.components["xnetblast"].requires = ["scoremat"]
            if "xobjmgr" in allexports:
                self.cpp_info.components["xobjmgr"].libs = ["xobjmgr"]
                self.cpp_info.components["xobjmgr"].requires = ["genome_collection", "seqedit", "seqsplit", "submit"]
            if "xobjread" in allexports:
                self.cpp_info.components["xobjread"].libs = ["xobjread"]
                self.cpp_info.components["xobjread"].requires = ["submit", "xlogging"]
#9--------------------------------------------------------------------------
            if "asn_cache" in allexports:
                self.cpp_info.components["asn_cache"].libs = ["asn_cache"]
                self.cpp_info.components["asn_cache"].requires = ["bdb", "seqset", "xcompress"]
            if "bamread" in allexports:
                self.cpp_info.components["bamread"].libs = ["bamread"]
                self.cpp_info.components["bamread"].requires = ["seqset", "xcompress", "VDB"]
            if "cn3d" in allexports:
                self.cpp_info.components["cn3d"].libs = ["cn3d"]
                self.cpp_info.components["cn3d"].requires = ["mmdb"]
            if "dbsnp_tooltip_service" in allexports:
                self.cpp_info.components["dbsnp_tooltip_service"].libs = ["dbsnp_tooltip_service"]
                self.cpp_info.components["dbsnp_tooltip_service"].requires = ["trackmgr"]
            if "gencoll_client" in allexports:
                self.cpp_info.components["gencoll_client"].libs = ["gencoll_client"]
                self.cpp_info.components["gencoll_client"].requires = ["genome_collection", "sqlitewrapp", "xcompress", "xconnect", "SQLITE3"]
            if "id1" in allexports:
                self.cpp_info.components["id1"].libs = ["id1"]
                self.cpp_info.components["id1"].requires = ["seqset"]
            if "local_taxon" in allexports:
                self.cpp_info.components["local_taxon"].libs = ["local_taxon"]
                self.cpp_info.components["local_taxon"].requires = ["taxon1", "sqlitewrapp", "SQLITE3"]
            if "proj" in allexports:
                self.cpp_info.components["proj"].libs = ["proj"]
                self.cpp_info.components["proj"].requires = ["pubmed", "seqset"]
            if "remapcli" in allexports:
                self.cpp_info.components["remapcli"].libs = ["remapcli"]
                self.cpp_info.components["remapcli"].requires = ["remap", "xconnect"]
            if "scoremat" in allexports:
                self.cpp_info.components["scoremat"].libs = ["scoremat"]
                self.cpp_info.components["scoremat"].requires = ["seqset"]
            if "searchbyrsid" in allexports:
                self.cpp_info.components["searchbyrsid"].libs = ["searchbyrsid"]
                self.cpp_info.components["searchbyrsid"].requires = ["trackmgr"]
            if "seqedit" in allexports:
                self.cpp_info.components["seqedit"].libs = ["seqedit"]
                self.cpp_info.components["seqedit"].requires = ["seqset"]
            if "seqsplit" in allexports:
                self.cpp_info.components["seqsplit"].libs = ["seqsplit"]
                self.cpp_info.components["seqsplit"].requires = ["seqset"]
            if "submit" in allexports:
                self.cpp_info.components["submit"].libs = ["submit"]
                self.cpp_info.components["submit"].requires = ["seqset"]
            if "trackmgrcli" in allexports:
                self.cpp_info.components["trackmgrcli"].libs = ["trackmgrcli"]
                self.cpp_info.components["trackmgrcli"].requires = ["trackmgr", "xconnect"]
            if "trackmgrgridcli" in allexports:
                self.cpp_info.components["trackmgrgridcli"].libs = ["trackmgrgridcli"]
                self.cpp_info.components["trackmgrgridcli"].requires = ["trackmgr", "xcompress", "xconnserv", "LZO"]
            if "valerr" in allexports:
                self.cpp_info.components["valerr"].libs = ["valerr"]
                self.cpp_info.components["valerr"].requires = ["xser", "seqset"]
#8--------------------------------------------------------------------------
            if "dbsnp_ptis" in allexports:
                self.cpp_info.components["dbsnp_ptis"].libs = ["dbsnp_ptis"]
                self.cpp_info.components["dbsnp_ptis"].requires = ["seq", "grpc_integration", "PROTOBUF", "GRPC", "Z"]
            if "entrezgene" in allexports:
                self.cpp_info.components["entrezgene"].libs = ["entrezgene"]
                self.cpp_info.components["entrezgene"].requires = ["seq"]
            if "eutils_client" in allexports:
                self.cpp_info.components["eutils_client"].libs = ["eutils_client"]
                self.cpp_info.components["eutils_client"].requires = ["seq", "xmlwrapp"]
            if "genome_collection" in allexports:
                self.cpp_info.components["genome_collection"].libs = ["genome_collection"]
                self.cpp_info.components["genome_collection"].requires = ["seq"]
            if "homologene" in allexports:
                self.cpp_info.components["homologene"].libs = ["homologene"]
                self.cpp_info.components["homologene"].requires = ["seq"]
            if "macro" in allexports:
                self.cpp_info.components["macro"].libs = ["macro"]
                self.cpp_info.components["macro"].requires = ["seq"]
            if "mlacli" in allexports:
                self.cpp_info.components["mlacli"].libs = ["mlacli"]
                self.cpp_info.components["mlacli"].requires = ["mla", "xconnect"]
            if "mmdb" in allexports:
                self.cpp_info.components["mmdb"].libs = ["mmdb"]
                self.cpp_info.components["mmdb"].requires = ["seq"]
            if "omssa" in allexports:
                self.cpp_info.components["omssa"].libs = ["omssa"]
                self.cpp_info.components["omssa"].requires = ["seq"]
            if "pcassay" in allexports:
                self.cpp_info.components["pcassay"].libs = ["pcassay"]
                self.cpp_info.components["pcassay"].requires = ["seq", "pcsubstance"]
            if "pcassay2" in allexports:
                self.cpp_info.components["pcassay2"].libs = ["pcassay2"]
                self.cpp_info.components["pcassay2"].requires = ["seq", "pcsubstance"]
            if "remap" in allexports:
                self.cpp_info.components["remap"].libs = ["remap"]
                self.cpp_info.components["remap"].requires = ["seq"]
            if "seqset" in allexports:
                self.cpp_info.components["seqset"].libs = ["seqset"]
                self.cpp_info.components["seqset"].requires = ["seq"]
            if "seqtest" in allexports:
                self.cpp_info.components["seqtest"].libs = ["seqtest"]
                self.cpp_info.components["seqtest"].requires = ["seq"]
            if "taxon1" in allexports:
                self.cpp_info.components["taxon1"].libs = ["taxon1"]
                self.cpp_info.components["taxon1"].requires = ["seq", "xconnect"]
            if "taxon3" in allexports:
                self.cpp_info.components["taxon3"].libs = ["taxon3"]
                self.cpp_info.components["taxon3"].requires = ["seq", "xconnect"]
            if "trackmgr" in allexports:
                self.cpp_info.components["trackmgr"].libs = ["trackmgr"]
                self.cpp_info.components["trackmgr"].requires = ["seq"]
            if "variation" in allexports:
                self.cpp_info.components["variation"].libs = ["variation"]
                self.cpp_info.components["variation"].requires = ["seq"]
#7--------------------------------------------------------------------------
            if "mla" in allexports:
                self.cpp_info.components["mla"].libs = ["mla"]
                self.cpp_info.components["mla"].requires = ["medlars", "pubmed", "pub"]
            if "pcsubstance" in allexports:
                self.cpp_info.components["pcsubstance"].libs = ["pcsubstance"]
                self.cpp_info.components["pcsubstance"].requires = ["pub"]
            if "seq" in allexports:
                self.cpp_info.components["seq"].libs = ["seq"]
                self.cpp_info.components["seq"].requires = ["pub", "seqcode", "sequtil"]
#6--------------------------------------------------------------------------
            if "pub" in allexports:
                self.cpp_info.components["pub"].libs = ["pub"]
                self.cpp_info.components["pub"].requires = ["medline"]
            if "pubmed" in allexports:
                self.cpp_info.components["pubmed"].libs = ["pubmed"]
                self.cpp_info.components["pubmed"].requires = ["medline"]
#5--------------------------------------------------------------------------
            if "medlars" in allexports:
                self.cpp_info.components["medlars"].libs = ["medlars"]
                self.cpp_info.components["medlars"].requires = ["biblio"]
            if "medline" in allexports:
                self.cpp_info.components["medline"].libs = ["medline"]
                self.cpp_info.components["medline"].requires = ["biblio"]
            if "netstorage" in allexports:
                self.cpp_info.components["netstorage"].libs = ["netstorage"]
                self.cpp_info.components["netstorage"].requires = ["ncbi_xcache_netcache"]
#4--------------------------------------------------------------------------
            if "biblio" in allexports:
                self.cpp_info.components["biblio"].libs = ["biblio"]
                self.cpp_info.components["biblio"].requires = ["libgeneral"]
            if "biotree" in allexports:
                self.cpp_info.components["biotree"].libs = ["biotree"]
                self.cpp_info.components["biotree"].requires = ["libgeneral"]
            if "entrez2cli" in allexports:
                self.cpp_info.components["entrez2cli"].libs = ["entrez2cli"]
                self.cpp_info.components["entrez2cli"].requires = ["entrez2", "xconnect"]
            if "eutils" in allexports:
                self.cpp_info.components["eutils"].libs = ["eutils"]
                self.cpp_info.components["eutils"].requires = ["einfo", "esearch", "egquery", "epost", "elink", "esummary", "espell", "ehistory", "uilist", "xconnect"]
            if "ncbi_xblobstorage_netcache" in allexports:
                self.cpp_info.components["ncbi_xblobstorage_netcache"].libs = ["ncbi_xblobstorage_netcache"]
                self.cpp_info.components["ncbi_xblobstorage_netcache"].requires = ["xconnserv"]
            if "ncbi_xcache_netcache" in allexports:
                self.cpp_info.components["ncbi_xcache_netcache"].libs = ["ncbi_xcache_netcache"]
                self.cpp_info.components["ncbi_xcache_netcache"].requires = ["xconnserv"]
            if "sample_asn" in allexports:
                self.cpp_info.components["sample_asn"].libs = ["sample_asn"]
                self.cpp_info.components["sample_asn"].requires = ["libgeneral"]
            if "sdbapi" in allexports:
                self.cpp_info.components["sdbapi"].libs = ["sdbapi"]
                self.cpp_info.components["sdbapi"].requires = ["dbapi", "dbapi_util_blobstore", "ncbi_xdbapi_ftds", "ncbi_xdbapi_ftds100", "xutil", "xconnect"]
            if "valid" in allexports:
                self.cpp_info.components["valid"].libs = ["valid"]
                self.cpp_info.components["valid"].requires = ["libgeneral", "xregexp"]
            if "xgridcgi" in allexports:
                self.cpp_info.components["xgridcgi"].libs = ["xgridcgi"]
                self.cpp_info.components["xgridcgi"].requires = ["xcgi", "xconnserv", "xhtml"]
            if "xobjmanip" in allexports:
                self.cpp_info.components["xobjmanip"].libs = ["xobjmanip"]
                self.cpp_info.components["xobjmanip"].requires = ["libgeneral"]
            if "xsoap_server" in allexports:
                self.cpp_info.components["xsoap_server"].libs = ["xsoap_server"]
                self.cpp_info.components["xsoap_server"].requires = ["xcgi", "xsoap"]
#3--------------------------------------------------------------------------
            if "access" in allexports:
                self.cpp_info.components["access"].libs = ["access"]
                self.cpp_info.components["access"].requires = ["xser"]
            if "asn_sample_lib" in allexports:
                self.cpp_info.components["asn_sample_lib"].libs = ["asn_sample_lib"]
                self.cpp_info.components["asn_sample_lib"].requires = ["xser"]
            if "blastxml" in allexports:
                self.cpp_info.components["blastxml"].libs = ["blastxml"]
                self.cpp_info.components["blastxml"].requires = ["xser"]
            if "blastxml2" in allexports:
                self.cpp_info.components["blastxml2"].libs = ["blastxml2"]
                self.cpp_info.components["blastxml2"].requires = ["xser"]
            if "ctransition_nlmzip" in allexports:
                self.cpp_info.components["ctransition_nlmzip"].libs = ["ctransition_nlmzip"]
                self.cpp_info.components["ctransition_nlmzip"].requires = ["ctransition", "xcompress"]
            if "dbapi_sample_base" in allexports:
                self.cpp_info.components["dbapi_sample_base"].libs = ["dbapi_sample_base"]
#                self.cpp_info.components["dbapi_sample_base"].requires = ["ncbi_xdbapi_ftds", "ncbi_xdbapi_ftds100", "dbapi_driver", "xutil", "ncbi_xdbapi_ctlib", "Sybase", "ODBC"]
                self.cpp_info.components["dbapi_sample_base"].requires = ["ncbi_xdbapi_ftds", "ncbi_xdbapi_ftds100", "dbapi_driver", "xutil"]
            if "dbapi_util_blobstore" in allexports:
                self.cpp_info.components["dbapi_util_blobstore"].libs = ["dbapi_util_blobstore"]
                self.cpp_info.components["dbapi_util_blobstore"].requires = ["dbapi_driver", "xcompress"]
            if "docsum" in allexports:
                self.cpp_info.components["docsum"].libs = ["docsum"]
                self.cpp_info.components["docsum"].requires = ["xser"]
            if "dtd_sample_lib" in allexports:
                self.cpp_info.components["dtd_sample_lib"].libs = ["dtd_sample_lib"]
                self.cpp_info.components["dtd_sample_lib"].requires = ["xser"]
            if "egquery" in allexports:
                self.cpp_info.components["egquery"].libs = ["egquery"]
                self.cpp_info.components["egquery"].requires = ["xser"]
            if "ehistory" in allexports:
                self.cpp_info.components["ehistory"].libs = ["ehistory"]
                self.cpp_info.components["ehistory"].requires = ["xser"]
            if "einfo" in allexports:
                self.cpp_info.components["einfo"].libs = ["einfo"]
                self.cpp_info.components["einfo"].requires = ["xser"]
            if "elink" in allexports:
                self.cpp_info.components["elink"].libs = ["elink"]
                self.cpp_info.components["elink"].requires = ["xser"]
            if "entrez2" in allexports:
                self.cpp_info.components["entrez2"].libs = ["entrez2"]
                self.cpp_info.components["entrez2"].requires = ["xser"]
            if "epost" in allexports:
                self.cpp_info.components["epost"].libs = ["epost"]
                self.cpp_info.components["epost"].requires = ["xser"]
            if "esearch" in allexports:
                self.cpp_info.components["esearch"].libs = ["esearch"]
                self.cpp_info.components["esearch"].requires = ["xser"]
            if "espell" in allexports:
                self.cpp_info.components["espell"].libs = ["espell"]
                self.cpp_info.components["espell"].requires = ["xser"]
            if "esummary" in allexports:
                self.cpp_info.components["esummary"].libs = ["esummary"]
                self.cpp_info.components["esummary"].requires = ["xser"]
            if "featdef" in allexports:
                self.cpp_info.components["featdef"].libs = ["featdef"]
                self.cpp_info.components["featdef"].requires = ["xser"]
            if "gbseq" in allexports:
                self.cpp_info.components["gbseq"].libs = ["gbseq"]
                self.cpp_info.components["gbseq"].requires = ["xser"]
            if "general" in allexports:
                self.cpp_info.components["libgeneral"].libs = ["$<1:general>"]
                self.cpp_info.components["libgeneral"].requires = ["xser"]
            if "generalasn" in allexports:
                self.cpp_info.components["libgeneral"].libs = ["generalasn"]
                self.cpp_info.components["libgeneral"].requires = ["xser"]
            if "genesbyloc" in allexports:
                self.cpp_info.components["genesbyloc"].libs = ["genesbyloc"]
                self.cpp_info.components["genesbyloc"].requires = ["xser"]
            if "hydra_client" in allexports:
                self.cpp_info.components["hydra_client"].libs = ["hydra_client"]
                self.cpp_info.components["hydra_client"].requires = ["xmlwrapp"]
            if "insdseq" in allexports:
                self.cpp_info.components["insdseq"].libs = ["insdseq"]
                self.cpp_info.components["insdseq"].requires = ["xser"]
            if "jsd_sample_lib" in allexports:
                self.cpp_info.components["jsd_sample_lib"].libs = ["jsd_sample_lib"]
                self.cpp_info.components["jsd_sample_lib"].requires = ["xser"]
            if "linkout" in allexports:
                self.cpp_info.components["linkout"].libs = ["linkout"]
                self.cpp_info.components["linkout"].requires = ["xser"]
            if "mim" in allexports:
                self.cpp_info.components["mim"].libs = ["mim"]
                self.cpp_info.components["mim"].requires = ["xser"]
            if "msbuild_dataobj" in allexports:
                self.cpp_info.components["msbuild_dataobj"].libs = ["msbuild_dataobj"]
                self.cpp_info.components["msbuild_dataobj"].requires = ["xser"]
            if "ncbi_xcache_bdb" in allexports:
                self.cpp_info.components["ncbi_xcache_bdb"].libs = ["ncbi_xcache_bdb"]
                self.cpp_info.components["ncbi_xcache_bdb"].requires = ["bdb", "BerkeleyDB"]
            if "objcoords" in allexports:
                self.cpp_info.components["objcoords"].libs = ["objcoords"]
                self.cpp_info.components["objcoords"].requires = ["xser"]
            if "objprt" in allexports:
                self.cpp_info.components["objprt"].libs = ["objprt"]
                self.cpp_info.components["objprt"].requires = ["xser"]
            if "pepXML" in allexports:
                self.cpp_info.components["pepXML"].libs = ["pepXML"]
                self.cpp_info.components["pepXML"].requires = ["xser"]
            if "pmcidconv_client" in allexports:
                self.cpp_info.components["pmcidconv_client"].libs = ["pmcidconv_client"]
                self.cpp_info.components["pmcidconv_client"].requires = ["xmlwrapp"]
            if "python_ncbi_dbapi" in allexports:
                self.cpp_info.components["python_ncbi_dbapi"].libs = ["python_ncbi_dbapi"]
                self.cpp_info.components["python_ncbi_dbapi"].requires = ["dbapi", "xutil", "PYTHON"]
            if "seqcode" in allexports:
                self.cpp_info.components["seqcode"].libs = ["seqcode"]
                self.cpp_info.components["seqcode"].requires = ["xser"]
            if "soap_dataobj" in allexports:
                self.cpp_info.components["soap_dataobj"].libs = ["soap_dataobj"]
                self.cpp_info.components["soap_dataobj"].requires = ["xser"]
            if "tinyseq" in allexports:
                self.cpp_info.components["tinyseq"].libs = ["tinyseq"]
                self.cpp_info.components["tinyseq"].requires = ["xser"]
            if "uilist" in allexports:
                self.cpp_info.components["uilist"].libs = ["uilist"]
                self.cpp_info.components["uilist"].requires = ["xser"]
            if "varrep" in allexports:
                self.cpp_info.components["varrep"].libs = ["varrep"]
                self.cpp_info.components["varrep"].requires = ["xser"]
            if "xalgotext" in allexports:
                self.cpp_info.components["xalgotext"].libs = ["xalgotext"]
                self.cpp_info.components["xalgotext"].requires = ["xcompress"]
            if "xcgi_redirect" in allexports:
                self.cpp_info.components["xcgi_redirect"].libs = ["xcgi_redirect"]
                self.cpp_info.components["xcgi_redirect"].requires = ["xcgi", "xhtml"]
            if "xconnserv" in allexports:
                self.cpp_info.components["xconnserv"].libs = ["xconnserv"]
                self.cpp_info.components["xconnserv"].requires = ["xthrserv"]
            if "xcser" in allexports:
                self.cpp_info.components["xcser"].libs = ["xcser"]
                self.cpp_info.components["xcser"].requires = ["xser"]
            if "xfcgi_mt" in allexports:
                self.cpp_info.components["xfcgi_mt"].libs = ["xfcgi_mt"]
                self.cpp_info.components["xfcgi_mt"].requires = ["xcgi", "FASTCGIPP"]
            if "xmlreaders" in allexports:
                self.cpp_info.components["xmlreaders"].libs = ["xmlreaders"]
                self.cpp_info.components["xmlreaders"].requires = ["xmlwrapp"]
            if "xsd_sample_lib" in allexports:
                self.cpp_info.components["xsd_sample_lib"].libs = ["xsd_sample_lib"]
                self.cpp_info.components["xsd_sample_lib"].requires = ["xser"]
            if "xsoap" in allexports:
                self.cpp_info.components["xsoap"].libs = ["xsoap"]
                self.cpp_info.components["xsoap"].requires = ["xconnect", "xser"]
#2--------------------------------------------------------------------------
            if "bdb" in allexports:
                self.cpp_info.components["bdb"].libs = ["bdb"]
                self.cpp_info.components["bdb"].requires = ["xutil", "BerkeleyDB"]
            if "dbapi" in allexports:
                self.cpp_info.components["dbapi"].libs = ["dbapi"]
                self.cpp_info.components["dbapi"].requires = ["dbapi_driver"]
            if "grpc_integration" in allexports:
                self.cpp_info.components["grpc_integration"].libs = ["grpc_integration"]
                self.cpp_info.components["grpc_integration"].requires = ["xutil", "GRPC", "Z"]
            if "gumbelparams" in allexports:
                self.cpp_info.components["gumbelparams"].libs = ["gumbelparams"]
                self.cpp_info.components["gumbelparams"].requires = ["tables", "xutil"]
            if "ncbi_xdbapi_ctlib" in allexports:
                self.cpp_info.components["ncbi_xdbapi_ctlib"].libs = ["ncbi_xdbapi_ctlib"]
                self.cpp_info.components["ncbi_xdbapi_ctlib"].requires = ["dbapi_driver", "Sybase"]
            if "ncbi_xdbapi_ftds" in allexports:
                self.cpp_info.components["ncbi_xdbapi_ftds"].libs = ["ncbi_xdbapi_ftds"]
                self.cpp_info.components["ncbi_xdbapi_ftds"].requires = ["dbapi_driver", "ct_ftds100"]
            if "ncbi_xdbapi_ftds100" in allexports:
                self.cpp_info.components["ncbi_xdbapi_ftds100"].libs = ["ncbi_xdbapi_ftds100"]
                self.cpp_info.components["ncbi_xdbapi_ftds100"].requires = ["ct_ftds100", "dbapi_driver"]
            if "ncbi_xdbapi_mysql" in allexports:
                self.cpp_info.components["ncbi_xdbapi_mysql"].libs = ["ncbi_xdbapi_mysql"]
                self.cpp_info.components["ncbi_xdbapi_mysql"].requires = ["dbapi_driver", "MySQL"]
            if "ncbi_xdbapi_odbc" in allexports:
                self.cpp_info.components["ncbi_xdbapi_odbc"].libs = ["ncbi_xdbapi_odbc"]
                self.cpp_info.components["ncbi_xdbapi_odbc"].requires = ["dbapi_driver", "ODBC"]
            if "psg_cache" in allexports:
                self.cpp_info.components["psg_cache"].libs = ["psg_cache"]
                self.cpp_info.components["psg_cache"].requires = ["xncbi", "psg_protobuf", "psg_cassandra", "LMDB", "PROTOBUF", "CASSANDRA"]
            if "wx_tools" in allexports:
                self.cpp_info.components["wx_tools"].libs = ["wx_tools"]
                self.cpp_info.components["wx_tools"].requires = ["xutil", "wxWidgets"]
            if "xasn" in allexports:
                self.cpp_info.components["xasn"].libs = ["xasn"]
                self.cpp_info.components["xasn"].requires = ["xhtml", "NCBI_C"]
            if "xcgi" in allexports:
                self.cpp_info.components["xcgi"].libs = ["xcgi"]
                self.cpp_info.components["xcgi"].requires = ["xutil"]
            if "xcompress" in allexports:
                self.cpp_info.components["xcompress"].libs = ["xcompress"]
                self.cpp_info.components["xcompress"].requires = ["xutil", "Z", "BZ2", "LZO"]
            if "xfcgi" in allexports:
                self.cpp_info.components["xfcgi"].libs = ["xfcgi"]
                self.cpp_info.components["xfcgi"].requires = ["xutil", "FASTCGI"]
            if "xmlwrapp" in allexports:
                self.cpp_info.components["xmlwrapp"].libs = ["xmlwrapp"]
                self.cpp_info.components["xmlwrapp"].requires = ["xconnect", "XML", "XSLT"]
            if "xregexp_template_tester" in allexports:
                self.cpp_info.components["xregexp_template_tester"].libs = ["xregexp_template_tester"]
                self.cpp_info.components["xregexp_template_tester"].requires = ["xregexp", "PCRE"]
            if "xser" in allexports:
                self.cpp_info.components["xser"].libs = ["xser"]
                self.cpp_info.components["xser"].requires = ["xutil"]
            if "xstruct_thread" in allexports:
                self.cpp_info.components["xstruct_thread"].libs = ["xstruct_thread"]
                self.cpp_info.components["xstruct_thread"].requires = ["xutil"]
            if "xthrserv" in allexports:
                self.cpp_info.components["xthrserv"].libs = ["xthrserv"]
                self.cpp_info.components["xthrserv"].requires = ["xconnect", "xutil"]
            if "xxconnect2" in allexports:
                self.cpp_info.components["xxconnect2"].libs = ["xxconnect2"]
                self.cpp_info.components["xxconnect2"].requires = ["xconnect", "UV", "NGHTTP2"]
#1--------------------------------------------------------------------------
            if "basic_sample_lib" in allexports:
                self.cpp_info.components["basic_sample_lib"].libs = ["basic_sample_lib"]
                self.cpp_info.components["basic_sample_lib"].requires = ["xncbi"]
            if "blast" in allexports:
                self.cpp_info.components["blast"].libs = ["blast"]
                self.cpp_info.components["blast"].requires = ["composition_adjustment", "connect", "tables"]
            if "connssl" in allexports:
                self.cpp_info.components["connssl"].libs = ["connssl"]
                self.cpp_info.components["connssl"].requires = ["connect"]
            if "ct_ftds100" in allexports:
                self.cpp_info.components["ct_ftds100"].libs = ["ct_ftds100"]
                self.cpp_info.components["ct_ftds100"].requires = ["tds_ftds100"]
            if "ctransition" in allexports:
                self.cpp_info.components["ctransition"].libs = ["ctransition"]
                self.cpp_info.components["ctransition"].requires = ["xncbi"]
            if "dbapi_driver" in allexports:
                self.cpp_info.components["dbapi_driver"].libs = ["dbapi_driver"]
                self.cpp_info.components["dbapi_driver"].requires = ["xncbi"]
            if "gene_info" in allexports:
                self.cpp_info.components["gene_info"].libs = ["gene_info"]
                self.cpp_info.components["gene_info"].requires = ["xncbi"]
            if "jaeger_tracer" in allexports:
                self.cpp_info.components["jaeger_tracer"].libs = ["jaeger_tracer"]
                self.cpp_info.components["jaeger_tracer"].requires = ["xncbi", "JAEGER"]
            if "odbc_ftds100" in allexports:
                self.cpp_info.components["odbc_ftds100"].libs = ["odbc_ftds100"]
                self.cpp_info.components["odbc_ftds100"].requires = ["tds_ftds100"]
            if "psg_cassandra" in allexports:
                self.cpp_info.components["psg_cassandra"].libs = ["psg_cassandra"]
                self.cpp_info.components["psg_cassandra"].requires = ["connect", "xncbi", "CASSANDRA"]
            if "psg_diag" in allexports:
                self.cpp_info.components["psg_diag"].libs = ["psg_diag"]
                self.cpp_info.components["psg_diag"].requires = ["xncbi"]
            if "sequtil" in allexports:
                self.cpp_info.components["sequtil"].libs = ["sequtil"]
                self.cpp_info.components["sequtil"].requires = ["xncbi"]
            if "sqlitewrapp" in allexports:
                self.cpp_info.components["sqlitewrapp"].libs = ["sqlitewrapp"]
                self.cpp_info.components["sqlitewrapp"].requires = ["xncbi", "SQLITE3"]
            if "sybdb_ftds100" in allexports:
                self.cpp_info.components["sybdb_ftds100"].libs = ["sybdb_ftds100"]
                self.cpp_info.components["sybdb_ftds100"].requires = ["tds_ftds100"]
            if "test_boost" in allexports:
                self.cpp_info.components["test_boost"].libs = ["test_boost"]
                self.cpp_info.components["test_boost"].requires = ["xncbi", "Boost"]
            if "test_mt" in allexports:
                self.cpp_info.components["test_mt"].libs = ["test_mt"]
                self.cpp_info.components["test_mt"].requires = ["xncbi"]
            if "utrtprof" in allexports:
                self.cpp_info.components["utrtprof"].libs = ["utrtprof"]
                self.cpp_info.components["utrtprof"].requires = ["xncbi"]
            if "xalgovmerge" in allexports:
                self.cpp_info.components["xalgovmerge"].libs = ["xalgovmerge"]
                self.cpp_info.components["xalgovmerge"].requires = ["xncbi"]
            if "xconnect" in allexports:
                self.cpp_info.components["xconnect"].libs = ["xconnect"]
                self.cpp_info.components["xconnect"].requires = ["xncbi"]
            if "xctools" in allexports:
                self.cpp_info.components["xctools"].libs = ["xctools"]
                self.cpp_info.components["xctools"].requires = ["connect", "xncbi", "NCBI_C"]
            if "xdiff" in allexports:
                self.cpp_info.components["xdiff"].libs = ["xdiff"]
                self.cpp_info.components["xdiff"].requires = ["xncbi"]
            if "xhtml" in allexports:
                self.cpp_info.components["xhtml"].libs = ["xhtml"]
                self.cpp_info.components["xhtml"].requires = ["xncbi"]
            if "ximage" in allexports:
                self.cpp_info.components["ximage"].libs = ["ximage"]
                self.cpp_info.components["ximage"].requires = ["xncbi", "Z", "JPEG", "PNG", "GIF", "TIFF"]
            if "xlogging" in allexports:
                self.cpp_info.components["xlogging"].libs = ["xlogging"]
                self.cpp_info.components["xlogging"].requires = ["xncbi"]
            if "xpbacktest" in allexports:
                self.cpp_info.components["xpbacktest"].libs = ["xpbacktest"]
                self.cpp_info.components["xpbacktest"].requires = ["xncbi"]
            if "xqueryparse" in allexports:
                self.cpp_info.components["xqueryparse"].libs = ["xqueryparse"]
                self.cpp_info.components["xqueryparse"].requires = ["xncbi"]
            if "xregexp" in allexports:
                self.cpp_info.components["xregexp"].libs = ["xregexp"]
                self.cpp_info.components["xregexp"].requires = ["xncbi", "PCRE"]
            if "xstruct_dp" in allexports:
                self.cpp_info.components["xstruct_dp"].libs = ["xstruct_dp"]
                self.cpp_info.components["xstruct_dp"].requires = ["xncbi"]
            if "xutil" in allexports:
                self.cpp_info.components["xutil"].libs = ["xutil"]
                self.cpp_info.components["xutil"].requires = ["xncbi"]
            if "xxconnect" in allexports:
                self.cpp_info.components["xxconnect"].libs = ["xxconnect"]
                self.cpp_info.components["xxconnect"].requires = ["xncbi", "NCBI_C"]
#0--------------------------------------------------------------------------
            if "clog" in allexports:
                self.cpp_info.components["clog"].libs = ["clog"]
                self.cpp_info.components["clog"].requires = ["ORIGLIBS"]
            if "composition_adjustment" in allexports:
                self.cpp_info.components["composition_adjustment"].libs = ["composition_adjustment"]
                self.cpp_info.components["composition_adjustment"].requires = ["ORIGLIBS"]
            if "connect" in allexports:
                self.cpp_info.components["connect"].libs = ["connect"]
                self.cpp_info.components["connect"].requires = ["NETWORKLIBS", "ORIGLIBS"]
            if "edit_imgt_file" in allexports:
                self.cpp_info.components["edit_imgt_file"].libs = ["edit_imgt_file"]
                self.cpp_info.components["edit_imgt_file"].requires = ["ORIGLIBS"]
            if "fastme" in allexports:
                self.cpp_info.components["fastme"].libs = ["fastme"]
                self.cpp_info.components["fastme"].requires = ["ORIGLIBS"]
            if "lapackwrapp" in allexports:
                self.cpp_info.components["lapackwrapp"].libs = ["lapackwrapp"]
                self.cpp_info.components["lapackwrapp"].requires = ["LAPACK", "ORIGLIBS"]
            if "psg_protobuf" in allexports:
                self.cpp_info.components["psg_protobuf"].libs = ["psg_protobuf"]
                self.cpp_info.components["psg_protobuf"].requires = ["PROTOBUF", "ORIGLIBS"]
            if "tables" in allexports:
                self.cpp_info.components["tables"].libs = ["tables"]
                self.cpp_info.components["tables"].requires = ["ORIGLIBS"]
            if "task_server" in allexports:
                self.cpp_info.components["task_server"].libs = ["task_server"]
                self.cpp_info.components["task_server"].requires = ["Boost", "ORIGLIBS"]
            if "tds_ftds100" in allexports:
                self.cpp_info.components["tds_ftds100"].libs = ["tds_ftds100"]
                self.cpp_info.components["tds_ftds100"].requires = ["ORIGLIBS"]
            if "test_dll" in allexports:
                self.cpp_info.components["test_dll"].libs = ["test_dll"]
                self.cpp_info.components["test_dll"].requires = ["ORIGLIBS"]
            if "xncbi" in allexports:
                self.cpp_info.components["xncbi"].libs = ["xncbi"]
                self.cpp_info.components["xncbi"].requires = ["ORIGLIBS"]
#----------------------------------------------------------------------------
        if self.settings.os == "Windows":
            self.cpp_info.components["ORIGLIBS"].defines.append("_UNICODE")
            self.cpp_info.components["ORIGLIBS"].defines.append("_CRT_SECURE_NO_WARNINGS=1")
        else:
            self.cpp_info.components["ORIGLIBS"].defines.append("_MT")
            self.cpp_info.components["ORIGLIBS"].defines.append("_REENTRANT")
            self.cpp_info.components["ORIGLIBS"].defines.append("_THREAD_SAFE")
            self.cpp_info.components["ORIGLIBS"].defines.append("_LARGEFILE_SOURCE")
            self.cpp_info.components["ORIGLIBS"].defines.append("_LARGEFILE64_SOURCE")
            self.cpp_info.components["ORIGLIBS"].defines.append("_FILE_OFFSET_BITS=64")
        if self.options.shared:
            self.cpp_info.components["ORIGLIBS"].defines.append("NCBI_DLL_BUILD")
        if self.settings.build_type == "Debug":
            self.cpp_info.components["ORIGLIBS"].defines.append("_DEBUG")
        else:
            self.cpp_info.components["ORIGLIBS"].defines.append("NDEBUG")
        self.cpp_info.components["ORIGLIBS"].builddirs.append("res")
        self.cpp_info.components["ORIGLIBS"].build_modules = ["res/build-system/cmake/CMake.NCBIpkg.conan.cmake"]

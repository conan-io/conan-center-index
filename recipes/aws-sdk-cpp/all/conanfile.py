from conans import ConanFile, CMake, tools
import os, shutil

def merge_dicts_for_sdk(a, b):
    res = a.copy()
    res.update(b)
    return res

class AwsSdkCppConan(ConanFile):
    name = "aws-sdk-cpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/aws-sdk-cpp"
    description = "AWS SDK for C++"
    topics = ("aws", "cpp", "crossplateform", "amazon", "cloud")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    sdks = ("access_management",
            "acm",
            "alexaforbusiness"
            "amplify"
            "apigateway",
            "application_autoscaling",
            "appstream",
            "appsync",
            "athena",
            "autoscaling",
            "batch",
            "budgets",
            "chime",
            "cloud9",
            "clouddirectory",
            "cloudformation",
            "cloudfront",
            "cloudhsmv2",
            "cloudsearch",
            "cloudtrail",
            "codebuild",
            "codecommit",
            "codedeploy",
            "codepipeline",
            "codestar",
            "cognito_identity",
            "cognito_idp",
            "cognito_sync",
            "comprehend",
            "config",
            "cur",
            "datapipeline",
            "dax",
            "devicefarm",
            "directconnect",
            "discovery",
            "dlm",
            "dms",
            "docdb",
            "ds",
            "dynamodb",
            "dynamodbstreams",
            "ec2",
            "ecr",
            "ecs",
            "eks",
            "elasticache",
            "elasticbeanstalk",
            "elasticfilesystem",
            "elasticloadbalancing",
            "elasticloadbalancingv2",
            "elasticmapreduce",
            "elastictranscoder",
            "email",
            "es",
            "events",
            "firehose",
            "fms",
            "fsx",
            "gamelift",
            "glacier",
            "globalaccelerator",
            "glue",
            "greengrass",
            "guardduty",
            "health",
            "iam",
            "identity_management",
            "importexport",
            "inspector",
            "iot_data",
            "iot_jobs_data",
            "iot",
            "kafka",
            "kinesis",
            "kinesisanalytics",
            "kinesisvideo",
            "kms",
            "lambda",
            "lex",
            "lightsail",
            "logs",
            "machinelearnings",
            "macie",
            "marketplace_entitlement",
            "marketplacecommerceanalytics",
            "mediaconvert",
            "medialive",
            "mediapackage",
            "mediastore",
            "mediatailor",
            "meteringmarketplace",
            "mobileanalytics",
            "monitoring",
            "mq",
            "mturk_requester",
            "neptune",
            "opsworks",
            "opsworkscm",
            "organizations",
            "pinpoint",
            "polly",
            "pricing",
            "queues",
            "quicksight",
            "ram",
            "rds",
            "redshift",
            "recognition",
            "resource_groups",
            "robomaker"
            "route53",
            "route53domains",
            "s3",
            "sagemaker",
            "sdb",
            "serverlessrepo"
            "servicecatalog",
            "servicediscovery",
            "shield",
            "signer",
            "sms",
            "snowball",
            "sns",
            "sqs",
            "ssm",
            "states",
            "storagegateway",
            "sts",
            "support",
            "swf",
            "text_to_speech",
            "texttract",
            "transcribe",
            "transfer",
            "translate",
            "waf",
            "workdocs",
            "worklink",
            "workmail",
            "workspaces",
            "xray"
           )
    options = merge_dicts_for_sdk({ x: [True, False] for x in sdks}, {
            "shared": [True, False],
            "fPIC": [True, False],
            "min_size": [True, False]
        })
    default_options = merge_dicts_for_sdk({ x: False for x in sdks}, {
            "shared": False,
            "fPIC": True,
            "min_size": False
        })

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("aws-c-common/0.4.25")
        self.requires("aws-c-event-stream/0.1.5")
        self.requires("zlib/1.2.11")
        if self.settings.os != "Windows":
            self.requires("libcurl/7.71.1")
        if not self.settings.os in ["Windows", "Macos"]:
            self.requires("openssl/1.1.1i")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)
        shutil.rmtree(self._source_subfolder + "/code-generation")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        build_only = list([])
        for sdk in self.sdks:
            if getattr(self.options, sdk):
                build_only.append(sdk)
        self._cmake.definitions["BUILD_ONLY"] = ";".join(build_only)

        self._cmake.definitions["BUILD_DEPS"] = False
        self._cmake.definitions["ENABLE_UNITY_BUILD"] = True
        self._cmake.definitions["ENABLE_TESTING"] = False
        self._cmake.definitions["AUTORUN_UNIT_TESTS"] = False

        self._cmake.definitions["MINIMIZE_SIZE"] = self.options.min_size
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                "find_package(Git)", "# find_package(Git")
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "sdks.cmake"),
                "sort_links(EXPORTS)", "# sort_links(EXPORTS)")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        libs = list([])

        for sdk in self.sdks:
            if getattr(self.options, sdk):
                self.cpp_info.libs.append("aws-cpp-sdk-" + sdk)
        self.cpp_info.libs.extend(["aws-cpp-sdk-core", "aws-c-event-stream", "aws-c-common", "aws-checksums"])

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["winhttp", "wininet", "bcrypt", "userenv", "version", "ws2_32"])

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("atomic")

        lib_stdcpp = tools.stdcpp_library(self)
        if lib_stdcpp:
            self.cpp_info.system_libs.append(lib_stdcpp)

from conans import ConanFile, CMake, tools
import os

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
    generators = "cmake"
    requires = "zlib/1.2.11"
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
    options = merge_dicts_for_sdk({"build_" + x: [True, False] for x in sdks}, {
            "shared": [True, False],
            "fPIC": [True, False],
            "min_size": [True, False]
        })
    default_options = merge_dicts_for_sdk({"build_" + x: False for x in sdks}, {
            "shared": False,
            "fPIC": True,
            "min_size": False
        })

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.settings.os != "Windows":
            if self.settings.os != "Macos":
                self.requires("openssl/1.1.1d")
            self.requires("libcurl/7.66.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        build_only = list([])
        for sdk in self.sdks:
            if getattr(self.options, "build_" + sdk):
                build_only.append(sdk)

        cmake.definitions["BUILD_ONLY"] = ";".join(build_only)
        cmake.definitions["ENABLE_UNITY_BUILD"] = "ON"
        cmake.definitions["ENABLE_TESTING"] = "OFF"
        cmake.definitions["AUTORUN_UNIT_TESTS"] = "OFF"

        cmake.definitions["MINIMIZE_SIZE"] = "ON" if self.options.min_size else "OFF"
        cmake.definitions["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        cmake.definitions["FORCE_SHARED_CRT"] = "ON" if self.options.shared else "OFF"

        cmake.configure(source_folder=self._source_subfolder, build_folder=self.build_folder)
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.install(build_dir=self.build_folder)

    def package_info(self):
        libs = list([])

        for sdk in self.sdks:
            if getattr(self.options, "build_" + sdk):
                libs.append("aws-cpp-sdk-" + sdk)
        libs.extend(["aws-cpp-sdk-core", "aws-c-event-stream", "aws-c-common", "aws-checksums"])

        if self.settings.os == "Windows":
            libs.append("winhttp")
            libs.append("wininet")
            libs.append("bcrypt")
            libs.append("userenv")
            libs.append("version")
            libs.append("ws2_32")

        if self.settings.os == "Linux":
            libs.append("atomic")
            if self.settings.compiler == "clang":
                libs.append("-stdlib=libstdc++")

        self.cpp_info.libs = libs
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]

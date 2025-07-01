import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=2"


class AwsSdkCppConan(ConanFile):
    name = "aws-sdk-cpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/aws-sdk-cpp"
    description = "AWS SDK for C++"
    topics = ("aws", "cpp", "cross-platform", "amazon", "cloud")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    # This list comes from tools/code-generation/api-description, which then generates the sdk sources
    # To generate for a new one, run the build once and check src/generated/src inside your build_folder, remove the common aws-sdk-cpp prefix
    # and that's the list of sdks. Then join it to this one
    _sdks = (
        ('AWSMigrationHub', ['1.11.352', '1.11.599']),
        ('access-management', ['1.9.234', '1.11.352']),
        ('accessanalyzer', ['1.9.234', '1.11.352', '1.11.599']),
        ('account', ['1.11.352', '1.11.599']),
        ('acm', ['1.9.234', '1.11.352', '1.11.599']),
        ('acm-pca', ['1.9.234', '1.11.352', '1.11.599']),
        ('aiops', ['1.11.599']),
        ('alexaforbusiness', ['1.9.234']),
        ('amp', ['1.9.234', '1.11.352', '1.11.599']),
        ('amplify', ['1.9.234', '1.11.352', '1.11.599']),
        ('amplifybackend', ['1.9.234', '1.11.352', '1.11.599']),
        ('amplifyuibuilder', ['1.11.352', '1.11.599']),
        ('apigateway', ['1.9.234', '1.11.352', '1.11.599']),
        ('apigatewaymanagementapi', ['1.9.234', '1.11.352', '1.11.599']),
        ('apigatewayv2', ['1.9.234', '1.11.352', '1.11.599']),
        ('appconfig', ['1.9.234', '1.11.352', '1.11.599']),
        ('appconfigdata', ['1.11.352', '1.11.599']),
        ('appfabric', ['1.11.352', '1.11.599']),
        ('appflow', ['1.9.234', '1.11.352', '1.11.599']),
        ('appintegrations', ['1.9.234', '1.11.352', '1.11.599']),
        ('application-autoscaling', ['1.9.234', '1.11.352', '1.11.599']),
        ('application-insights', ['1.9.234', '1.11.352', '1.11.599']),
        ('application-signals', ['1.11.352', '1.11.599']),
        ('applicationcostprofiler', ['1.11.352', '1.11.599']),
        ('appmesh', ['1.9.234', '1.11.352', '1.11.599']),
        ('apprunner', ['1.11.352', '1.11.599']),
        ('appstream', ['1.9.234', '1.11.352', '1.11.599']),
        ('appsync', ['1.9.234', '1.11.352', '1.11.599']),
        ('apptest', ['1.11.352', '1.11.599']),
        ('arc-zonal-shift', ['1.11.352', '1.11.599']),
        ('artifact', ['1.11.352', '1.11.599']),
        ('athena', ['1.9.234', '1.11.352', '1.11.599']),
        ('auditmanager', ['1.9.234', '1.11.352', '1.11.599']),
        ('autoscaling', ['1.9.234', '1.11.352', '1.11.599']),
        ('autoscaling-plans', ['1.9.234', '1.11.352', '1.11.599']),
        ('awstransfer', ['1.9.234', '1.11.352', '1.11.599']),
        ('b2bi', ['1.11.352', '1.11.599']),
        ('backup', ['1.9.234', '1.11.352', '1.11.599']),
        ('backup-gateway', ['1.11.352', '1.11.599']),
        ('backupsearch', ['1.11.599']),
        ('batch', ['1.9.234', '1.11.352', '1.11.599']),
        ('bcm-data-exports', ['1.11.352', '1.11.599']),
        ('bcm-pricing-calculator', ['1.11.599']),
        ('bedrock', ['1.11.352', '1.11.599']),
        ('bedrock-agent', ['1.11.352', '1.11.599']),
        ('bedrock-agent-runtime', ['1.11.352', '1.11.599']),
        ('bedrock-data-automation', ['1.11.599']),
        ('bedrock-data-automation-runtime', ['1.11.599']),
        ('bedrock-runtime', ['1.11.352', '1.11.599']),
        ('billing', ['1.11.599']),
        ('billingconductor', ['1.11.352', '1.11.599']),
        ('braket', ['1.9.234', '1.11.352', '1.11.599']),
        ('budgets', ['1.9.234', '1.11.352', '1.11.599']),
        ('ce', ['1.9.234', '1.11.352', '1.11.599']),
        ('chatbot', ['1.11.352', '1.11.599']),
        ('chime', ['1.9.234', '1.11.352', '1.11.599']),
        ('chime-sdk-identity', ['1.11.352', '1.11.599']),
        ('chime-sdk-media-pipelines', ['1.11.352', '1.11.599']),
        ('chime-sdk-meetings', ['1.11.352', '1.11.599']),
        ('chime-sdk-messaging', ['1.11.352', '1.11.599']),
        ('chime-sdk-voice', ['1.11.352', '1.11.599']),
        ('cleanrooms', ['1.11.352', '1.11.599']),
        ('cleanroomsml', ['1.11.352', '1.11.599']),
        ('cloud9', ['1.9.234', '1.11.352', '1.11.599']),
        ('cloudcontrol', ['1.11.352', '1.11.599']),
        ('clouddirectory', ['1.9.234', '1.11.352', '1.11.599']),
        ('cloudformation', ['1.9.234', '1.11.352', '1.11.599']),
        ('cloudfront', ['1.9.234', '1.11.352', '1.11.599']),
        ('cloudfront-keyvaluestore', ['1.11.352', '1.11.599']),
        ('cloudhsm', ['1.9.234', '1.11.352', '1.11.599']),
        ('cloudhsmv2', ['1.9.234', '1.11.352', '1.11.599']),
        ('cloudsearch', ['1.9.234', '1.11.352', '1.11.599']),
        ('cloudsearchdomain', ['1.9.234', '1.11.352', '1.11.599']),
        ('cloudtrail', ['1.9.234', '1.11.352', '1.11.599']),
        ('cloudtrail-data', ['1.11.352', '1.11.599']),
        ('codeartifact', ['1.9.234', '1.11.352', '1.11.599']),
        ('codebuild', ['1.9.234', '1.11.352', '1.11.599']),
        ('codecatalyst', ['1.11.352', '1.11.599']),
        ('codecommit', ['1.9.234', '1.11.352', '1.11.599']),
        ('codeconnections', ['1.11.352', '1.11.599']),
        ('codedeploy', ['1.9.234', '1.11.352', '1.11.599']),
        ('codeguru-reviewer', ['1.9.234', '1.11.352', '1.11.599']),
        ('codeguru-security', ['1.11.352', '1.11.599']),
        ('codeguruprofiler', ['1.9.234', '1.11.352', '1.11.599']),
        ('codepipeline', ['1.9.234', '1.11.352', '1.11.599']),
        ('codestar', ['1.9.234', '1.11.352']),
        ('codestar-connections', ['1.9.234', '1.11.352', '1.11.599']),
        ('codestar-notifications', ['1.9.234', '1.11.352', '1.11.599']),
        ('cognito-identity', ['1.9.234', '1.11.352', '1.11.599']),
        ('cognito-idp', ['1.9.234', '1.11.352', '1.11.599']),
        ('cognito-sync', ['1.9.234', '1.11.352', '1.11.599']),
        ('comprehend', ['1.9.234', '1.11.352', '1.11.599']),
        ('comprehendmedical', ['1.9.234', '1.11.352', '1.11.599']),
        ('compute-optimizer', ['1.9.234', '1.11.352', '1.11.599']),
        ('config', ['1.9.234', '1.11.352', '1.11.599']),
        ('connect', ['1.9.234', '1.11.352', '1.11.599']),
        ('connect-contact-lens', ['1.9.234', '1.11.352', '1.11.599']),
        ('connectcampaigns', ['1.11.352', '1.11.599']),
        ('connectcampaignsv2', ['1.11.599']),
        ('connectcases', ['1.11.352', '1.11.599']),
        ('connectparticipant', ['1.9.234', '1.11.352', '1.11.599']),
        ('controlcatalog', ['1.11.352', '1.11.599']),
        ('controltower', ['1.11.352', '1.11.599']),
        ('cost-optimization-hub', ['1.11.352', '1.11.599']),
        ('cur', ['1.9.234', '1.11.352', '1.11.599']),
        ('customer-profiles', ['1.9.234', '1.11.352', '1.11.599']),
        ('databrew', ['1.9.234', '1.11.352', '1.11.599']),
        ('dataexchange', ['1.9.234', '1.11.352', '1.11.599']),
        ('datapipeline', ['1.9.234', '1.11.352', '1.11.599']),
        ('datasync', ['1.9.234', '1.11.352', '1.11.599']),
        ('datazone', ['1.11.352', '1.11.599']),
        ('dax', ['1.9.234', '1.11.352', '1.11.599']),
        ('deadline', ['1.11.352', '1.11.599']),
        ('detective', ['1.9.234', '1.11.352', '1.11.599']),
        ('devicefarm', ['1.9.234', '1.11.352', '1.11.599']),
        ('devops-guru', ['1.9.234', '1.11.352', '1.11.599']),
        ('directconnect', ['1.9.234', '1.11.352', '1.11.599']),
        ('directory-service-data', ['1.11.599']),
        ('discovery', ['1.9.234', '1.11.352', '1.11.599']),
        ('dlm', ['1.9.234', '1.11.352', '1.11.599']),
        ('dms', ['1.9.234', '1.11.352', '1.11.599']),
        ('docdb', ['1.9.234', '1.11.352', '1.11.599']),
        ('docdb-elastic', ['1.11.352', '1.11.599']),
        ('drs', ['1.11.352', '1.11.599']),
        ('ds', ['1.9.234', '1.11.352', '1.11.599']),
        ('dsql', ['1.11.599']),
        ('dynamodb', ['1.9.234', '1.11.352', '1.11.599']),
        ('dynamodbstreams', ['1.9.234', '1.11.352', '1.11.599']),
        ('ebs', ['1.9.234', '1.11.352', '1.11.599']),
        ('ec2', ['1.9.234', '1.11.352', '1.11.599']),
        ('ec2-instance-connect', ['1.9.234', '1.11.352', '1.11.599']),
        ('ecr', ['1.9.234', '1.11.352', '1.11.599']),
        ('ecr-public', ['1.9.234', '1.11.352', '1.11.599']),
        ('ecs', ['1.9.234', '1.11.352', '1.11.599']),
        ('eks', ['1.9.234', '1.11.352', '1.11.599']),
        ('eks-auth', ['1.11.352', '1.11.599']),
        ('elastic-inference', ['1.9.234', '1.11.352']),
        ('elasticache', ['1.9.234', '1.11.352', '1.11.599']),
        ('elasticbeanstalk', ['1.9.234', '1.11.352', '1.11.599']),
        ('elasticfilesystem', ['1.9.234', '1.11.352', '1.11.599']),
        ('elasticloadbalancing', ['1.9.234', '1.11.352', '1.11.599']),
        ('elasticloadbalancingv2', ['1.9.234', '1.11.352', '1.11.599']),
        ('elasticmapreduce', ['1.9.234', '1.11.352', '1.11.599']),
        ('elastictranscoder', ['1.9.234', '1.11.352', '1.11.599']),
        ('email', ['1.9.234', '1.11.352', '1.11.599']),
        ('emr-containers', ['1.9.234', '1.11.352', '1.11.599']),
        ('emr-serverless', ['1.11.352', '1.11.599']),
        ('entityresolution', ['1.11.352', '1.11.599']),
        ('es', ['1.9.234', '1.11.352', '1.11.599']),
        ('eventbridge', ['1.9.234', '1.11.352', '1.11.599']),
        ('events', ['1.9.234', '1.11.352', '1.11.599']),
        ('evidently', ['1.11.352', '1.11.599']),
        ('evs', ['1.11.599']),
        ('finspace', ['1.11.352', '1.11.599']),
        ('finspace-data', ['1.11.352', '1.11.599']),
        ('firehose', ['1.9.234', '1.11.352', '1.11.599']),
        ('fis', ['1.11.352', '1.11.599']),
        ('fms', ['1.9.234', '1.11.352', '1.11.599']),
        ('forecast', ['1.9.234', '1.11.352', '1.11.599']),
        ('forecastquery', ['1.9.234', '1.11.352', '1.11.599']),
        ('frauddetector', ['1.9.234', '1.11.352', '1.11.599']),
        ('freetier', ['1.11.352', '1.11.599']),
        ('fsx', ['1.9.234', '1.11.352', '1.11.599']),
        ('gamelift', ['1.9.234', '1.11.352', '1.11.599']),
        ('gameliftstreams', ['1.11.599']),
        ('geo-maps', ['1.11.599']),
        ('geo-places', ['1.11.599']),
        ('geo-routes', ['1.11.599']),
        ('glacier', ['1.9.234', '1.11.352', '1.11.599']),
        ('globalaccelerator', ['1.9.234', '1.11.352', '1.11.599']),
        ('glue', ['1.9.234', '1.11.352', '1.11.599']),
        ('grafana', ['1.11.352', '1.11.599']),
        ('greengrass', ['1.9.234', '1.11.352', '1.11.599']),
        ('greengrassv2', ['1.9.234', '1.11.352', '1.11.599']),
        ('groundstation', ['1.9.234', '1.11.352', '1.11.599']),
        ('guardduty', ['1.9.234', '1.11.352', '1.11.599']),
        ('health', ['1.9.234', '1.11.352', '1.11.599']),
        ('healthlake', ['1.9.234', '1.11.352', '1.11.599']),
        ('honeycode', ['1.9.234']),
        ('iam', ['1.9.234', '1.11.352', '1.11.599']),
        ('identity-management', ['1.9.234', '1.11.352']),
        ('identitystore', ['1.9.234', '1.11.352', '1.11.599']),
        ('imagebuilder', ['1.9.234', '1.11.352', '1.11.599']),
        ('importexport', ['1.9.234', '1.11.352', '1.11.599']),
        ('inspector', ['1.9.234', '1.11.352', '1.11.599']),
        ('inspector-scan', ['1.11.352', '1.11.599']),
        ('inspector2', ['1.11.352', '1.11.599']),
        ('internetmonitor', ['1.11.352', '1.11.599']),
        ('invoicing', ['1.11.599']),
        ('iot', ['1.9.234', '1.11.352', '1.11.599']),
        ('iot-data', ['1.9.234', '1.11.352', '1.11.599']),
        ('iot-jobs-data', ['1.9.234', '1.11.352', '1.11.599']),
        ('iot-managed-integrations', ['1.11.599']),
        ('iot1click-devices', ['1.9.234', '1.11.352', '1.11.599']),
        ('iot1click-projects', ['1.9.234', '1.11.352', '1.11.599']),
        ('iotanalytics', ['1.9.234', '1.11.352', '1.11.599']),
        ('iotdeviceadvisor', ['1.9.234', '1.11.352', '1.11.599']),
        ('iotevents', ['1.9.234', '1.11.352', '1.11.599']),
        ('iotevents-data', ['1.9.234', '1.11.352', '1.11.599']),
        ('iotfleethub', ['1.9.234', '1.11.352', '1.11.599']),
        ('iotfleetwise', ['1.11.352', '1.11.599']),
        ('iotsecuretunneling', ['1.9.234', '1.11.352', '1.11.599']),
        ('iotsitewise', ['1.9.234', '1.11.352', '1.11.599']),
        ('iotthingsgraph', ['1.9.234', '1.11.352', '1.11.599']),
        ('iottwinmaker', ['1.11.352', '1.11.599']),
        ('iotwireless', ['1.9.234', '1.11.352', '1.11.599']),
        ('ivs', ['1.9.234', '1.11.352', '1.11.599']),
        ('ivs-realtime', ['1.11.352', '1.11.599']),
        ('ivschat', ['1.11.352', '1.11.599']),
        ('kafka', ['1.9.234', '1.11.352', '1.11.599']),
        ('kafkaconnect', ['1.11.352', '1.11.599']),
        ('kendra', ['1.9.234', '1.11.352', '1.11.599']),
        ('kendra-ranking', ['1.11.352', '1.11.599']),
        ('keyspaces', ['1.11.352', '1.11.599']),
        ('keyspacesstreams', ['1.11.599']),
        ('kinesis', ['1.9.234', '1.11.352', '1.11.599']),
        ('kinesis-video-archived-media', ['1.9.234', '1.11.352', '1.11.599']),
        ('kinesis-video-media', ['1.9.234', '1.11.352', '1.11.599']),
        ('kinesis-video-signaling', ['1.9.234', '1.11.352', '1.11.599']),
        ('kinesis-video-webrtc-storage', ['1.11.352', '1.11.599']),
        ('kinesisanalytics', ['1.9.234', '1.11.352', '1.11.599']),
        ('kinesisanalyticsv2', ['1.9.234', '1.11.352', '1.11.599']),
        ('kinesisvideo', ['1.9.234', '1.11.352', '1.11.599']),
        ('kms', ['1.9.234', '1.11.352', '1.11.599']),
        ('lakeformation', ['1.9.234', '1.11.352', '1.11.599']),
        ('lambda', ['1.9.234', '1.11.352', '1.11.599']),
        ('launch-wizard', ['1.11.352', '1.11.599']),
        ('lex', ['1.9.234', '1.11.352', '1.11.599']),
        ('lex-models', ['1.9.234', '1.11.352', '1.11.599']),
        ('lexv2-models', ['1.9.234', '1.11.352', '1.11.599']),
        ('lexv2-runtime', ['1.9.234', '1.11.352', '1.11.599']),
        ('license-manager', ['1.9.234', '1.11.352', '1.11.599']),
        ('license-manager-linux-subscriptions', ['1.11.352', '1.11.599']),
        ('license-manager-user-subscriptions', ['1.11.352', '1.11.599']),
        ('lightsail', ['1.9.234', '1.11.352', '1.11.599']),
        ('location', ['1.9.234', '1.11.352', '1.11.599']),
        ('logs', ['1.9.234', '1.11.352', '1.11.599']),
        ('lookoutequipment', ['1.11.352', '1.11.599']),
        ('lookoutmetrics', ['1.11.352', '1.11.599']),
        ('lookoutvision', ['1.9.234', '1.11.352', '1.11.599']),
        ('m2', ['1.11.352', '1.11.599']),
        ('machinelearning', ['1.9.234', '1.11.352', '1.11.599']),
        ('macie', ['1.9.234']),
        ('macie2', ['1.9.234', '1.11.352', '1.11.599']),
        ('mailmanager', ['1.11.352', '1.11.599']),
        ('managedblockchain', ['1.9.234', '1.11.352', '1.11.599']),
        ('managedblockchain-query', ['1.11.352', '1.11.599']),
        ('marketplace-agreement', ['1.11.352', '1.11.599']),
        ('marketplace-catalog', ['1.9.234', '1.11.352', '1.11.599']),
        ('marketplace-deployment', ['1.11.352', '1.11.599']),
        ('marketplace-entitlement', ['1.9.234', '1.11.352', '1.11.599']),
        ('marketplace-reporting', ['1.11.599']),
        ('marketplacecommerceanalytics', ['1.9.234', '1.11.352', '1.11.599']),
        ('mediaconnect', ['1.9.234', '1.11.352', '1.11.599']),
        ('mediaconvert', ['1.9.234', '1.11.352', '1.11.599']),
        ('medialive', ['1.9.234', '1.11.352', '1.11.599']),
        ('mediapackage', ['1.9.234', '1.11.352', '1.11.599']),
        ('mediapackage-vod', ['1.9.234', '1.11.352', '1.11.599']),
        ('mediapackagev2', ['1.11.352', '1.11.599']),
        ('mediastore', ['1.9.234', '1.11.352', '1.11.599']),
        ('mediastore-data', ['1.9.234', '1.11.352', '1.11.599']),
        ('mediatailor', ['1.9.234', '1.11.352', '1.11.599']),
        ('medical-imaging', ['1.11.352', '1.11.599']),
        ('memorydb', ['1.11.352', '1.11.599']),
        ('meteringmarketplace', ['1.9.234', '1.11.352', '1.11.599']),
        ('mgn', ['1.11.352', '1.11.599']),
        ('migration-hub-refactor-spaces', ['1.11.352', '1.11.599']),
        ('migrationhub-config', ['1.9.234', '1.11.352', '1.11.599']),
        ('migrationhuborchestrator', ['1.11.352', '1.11.599']),
        ('migrationhubstrategy', ['1.11.352', '1.11.599']),
        ('mobile', ['1.9.234', '1.11.352']),
        ('mobileanalytics', ['1.9.234']),
        ('monitoring', ['1.9.234', '1.11.352', '1.11.599']),
        ('mpa', ['1.11.599']),
        ('mq', ['1.9.234', '1.11.352', '1.11.599']),
        ('mturk-requester', ['1.9.234', '1.11.352', '1.11.599']),
        ('mwaa', ['1.9.234', '1.11.352', '1.11.599']),
        ('neptune', ['1.9.234', '1.11.352', '1.11.599']),
        ('neptune-graph', ['1.11.352', '1.11.599']),
        ('neptunedata', ['1.11.352', '1.11.599']),
        ('network-firewall', ['1.9.234', '1.11.352', '1.11.599']),
        ('networkflowmonitor', ['1.11.599']),
        ('networkmanager', ['1.9.234', '1.11.352', '1.11.599']),
        ('networkmonitor', ['1.11.352', '1.11.599']),
        ('nimble', ['1.11.352']),
        ('notifications', ['1.11.599']),
        ('notificationscontacts', ['1.11.599']),
        ('oam', ['1.11.352', '1.11.599']),
        ('observabilityadmin', ['1.11.599']),
        ('omics', ['1.11.352', '1.11.599']),
        ('opensearch', ['1.11.352', '1.11.599']),
        ('opensearchserverless', ['1.11.352', '1.11.599']),
        ('opsworks', ['1.9.234', '1.11.352', '1.11.599']),
        ('opsworkscm', ['1.9.234', '1.11.352', '1.11.599']),
        ('organizations', ['1.9.234', '1.11.352', '1.11.599']),
        ('osis', ['1.11.352', '1.11.599']),
        ('outposts', ['1.9.234', '1.11.352', '1.11.599']),
        ('panorama', ['1.11.352', '1.11.599']),
        ('partnercentral-selling', ['1.11.599']),
        ('payment-cryptography', ['1.11.352', '1.11.599']),
        ('payment-cryptography-data', ['1.11.352', '1.11.599']),
        ('pca-connector-ad', ['1.11.352', '1.11.599']),
        ('pca-connector-scep', ['1.11.352', '1.11.599']),
        ('pcs', ['1.11.599']),
        ('personalize', ['1.9.234', '1.11.352', '1.11.599']),
        ('personalize-events', ['1.9.234', '1.11.352', '1.11.599']),
        ('personalize-runtime', ['1.9.234', '1.11.352', '1.11.599']),
        ('pi', ['1.9.234', '1.11.352', '1.11.599']),
        ('pinpoint', ['1.9.234', '1.11.352', '1.11.599']),
        ('pinpoint-email', ['1.9.234', '1.11.352', '1.11.599']),
        ('pinpoint-sms-voice-v2', ['1.11.352', '1.11.599']),
        ('pipes', ['1.11.352', '1.11.599']),
        ('polly', ['1.9.234', '1.11.352', '1.11.599']),
        ('pricing', ['1.9.234', '1.11.352', '1.11.599']),
        ('privatenetworks', ['1.11.352']),
        ('proton', ['1.11.352', '1.11.599']),
        ('qapps', ['1.11.599']),
        ('qbusiness', ['1.11.352', '1.11.599']),
        ('qconnect', ['1.11.352', '1.11.599']),
        ('qldb', ['1.9.234', '1.11.352', '1.11.599']),
        ('qldb-session', ['1.9.234', '1.11.352', '1.11.599']),
        ('queues', ['1.9.234', '1.11.352']),
        ('quicksight', ['1.9.234', '1.11.352', '1.11.599']),
        ('ram', ['1.9.234', '1.11.352', '1.11.599']),
        ('rbin', ['1.11.352', '1.11.599']),
        ('rds', ['1.9.234', '1.11.352', '1.11.599']),
        ('rds-data', ['1.9.234', '1.11.352', '1.11.599']),
        ('redshift', ['1.9.234', '1.11.352', '1.11.599']),
        ('redshift-data', ['1.9.234', '1.11.352', '1.11.599']),
        ('redshift-serverless', ['1.11.352', '1.11.599']),
        ('rekognition', ['1.9.234', '1.11.352', '1.11.599']),
        ('repostspace', ['1.11.352', '1.11.599']),
        ('resiliencehub', ['1.11.352', '1.11.599']),
        ('resource-explorer-2', ['1.11.352', '1.11.599']),
        ('resource-groups', ['1.9.234', '1.11.352', '1.11.599']),
        ('resourcegroupstaggingapi', ['1.9.234', '1.11.352', '1.11.599']),
        ('robomaker', ['1.9.234', '1.11.352', '1.11.599']),
        ('rolesanywhere', ['1.11.352', '1.11.599']),
        ('route53', ['1.9.234', '1.11.352', '1.11.599']),
        ('route53-recovery-cluster', ['1.11.352', '1.11.599']),
        ('route53-recovery-control-config', ['1.11.352', '1.11.599']),
        ('route53-recovery-readiness', ['1.11.352', '1.11.599']),
        ('route53domains', ['1.9.234', '1.11.352', '1.11.599']),
        ('route53profiles', ['1.11.352', '1.11.599']),
        ('route53resolver', ['1.9.234', '1.11.352', '1.11.599']),
        ('rum', ['1.11.352', '1.11.599']),
        ('s3', ['1.9.234', '1.11.352', '1.11.599']),
        ('s3-crt', ['1.9.234', '1.11.352', '1.11.599']),
        ('s3-encryption', ['1.9.234', '1.11.352']),
        ('s3control', ['1.9.234', '1.11.352', '1.11.599']),
        ('s3outposts', ['1.9.234', '1.11.352', '1.11.599']),
        ('s3tables', ['1.11.599']),
        ('sagemaker', ['1.9.234', '1.11.352', '1.11.599']),
        ('sagemaker-a2i-runtime', ['1.9.234', '1.11.352', '1.11.599']),
        ('sagemaker-edge', ['1.9.234', '1.11.352', '1.11.599']),
        ('sagemaker-featurestore-runtime', ['1.9.234', '1.11.352', '1.11.599']),
        ('sagemaker-geospatial', ['1.11.352', '1.11.599']),
        ('sagemaker-metrics', ['1.11.352', '1.11.599']),
        ('sagemaker-runtime', ['1.9.234', '1.11.352', '1.11.599']),
        ('savingsplans', ['1.9.234', '1.11.352', '1.11.599']),
        ('scheduler', ['1.11.352', '1.11.599']),
        ('schemas', ['1.9.234', '1.11.352', '1.11.599']),
        ('sdb', ['1.9.234', '1.11.352', '1.11.599']),
        ('secretsmanager', ['1.9.234', '1.11.352', '1.11.599']),
        ('security-ir', ['1.11.599']),
        ('securityhub', ['1.9.234', '1.11.352', '1.11.599']),
        ('securitylake', ['1.11.352', '1.11.599']),
        ('serverlessrepo', ['1.9.234', '1.11.352', '1.11.599']),
        ('service-quotas', ['1.9.234', '1.11.352', '1.11.599']),
        ('servicecatalog', ['1.9.234', '1.11.352', '1.11.599']),
        ('servicecatalog-appregistry', ['1.9.234', '1.11.352', '1.11.599']),
        ('servicediscovery', ['1.9.234', '1.11.352', '1.11.599']),
        ('sesv2', ['1.9.234', '1.11.352', '1.11.599']),
        ('shield', ['1.9.234', '1.11.352', '1.11.599']),
        ('signer', ['1.9.234', '1.11.352', '1.11.599']),
        ('simspaceweaver', ['1.11.352', '1.11.599']),
        ('sms', ['1.9.234', '1.11.352', '1.11.599']),
        ('sms-voice', ['1.9.234', '1.11.352', '1.11.599']),
        ('snow-device-management', ['1.11.352', '1.11.599']),
        ('snowball', ['1.9.234', '1.11.352', '1.11.599']),
        ('sns', ['1.9.234', '1.11.352', '1.11.599']),
        ('socialmessaging', ['1.11.599']),
        ('sqs', ['1.9.234', '1.11.352', '1.11.599']),
        ('ssm', ['1.9.234', '1.11.352', '1.11.599']),
        ('ssm-contacts', ['1.11.352', '1.11.599']),
        ('ssm-guiconnect', ['1.11.599']),
        ('ssm-incidents', ['1.11.352', '1.11.599']),
        ('ssm-quicksetup', ['1.11.599']),
        ('ssm-sap', ['1.11.352', '1.11.599']),
        ('sso', ['1.9.234', '1.11.352', '1.11.599']),
        ('sso-admin', ['1.9.234', '1.11.352', '1.11.599']),
        ('sso-oidc', ['1.9.234', '1.11.352', '1.11.599']),
        ('states', ['1.9.234', '1.11.352', '1.11.599']),
        ('storagegateway', ['1.9.234', '1.11.352', '1.11.599']),
        ('sts', ['1.9.234', '1.11.352', '1.11.599']),
        ('supplychain', ['1.11.352', '1.11.599']),
        ('support', ['1.9.234', '1.11.352', '1.11.599']),
        ('support-app', ['1.11.352', '1.11.599']),
        ('swf', ['1.9.234', '1.11.352', '1.11.599']),
        ('synthetics', ['1.9.234', '1.11.352', '1.11.599']),
        ('taxsettings', ['1.11.352', '1.11.599']),
        ('text-to-speech', ['1.9.234', '1.11.352']),
        ('textract', ['1.9.234', '1.11.352', '1.11.599']),
        ('timestream-influxdb', ['1.11.352', '1.11.599']),
        ('timestream-query', ['1.9.234', '1.11.352', '1.11.599']),
        ('timestream-write', ['1.9.234', '1.11.352', '1.11.599']),
        ('tnb', ['1.11.352', '1.11.599']),
        ('transcribe', ['1.9.234', '1.11.352', '1.11.599']),
        ('transcribestreaming', ['1.9.234', '1.11.352', '1.11.599']),
        ('transfer', ['1.9.234', '1.11.352']),
        ('translate', ['1.9.234', '1.11.352', '1.11.599']),
        ('trustedadvisor', ['1.11.352', '1.11.599']),
        ('verifiedpermissions', ['1.11.352', '1.11.599']),
        ('voice-id', ['1.11.352', '1.11.599']),
        ('vpc-lattice', ['1.11.352', '1.11.599']),
        ('waf', ['1.9.234', '1.11.352', '1.11.599']),
        ('waf-regional', ['1.9.234', '1.11.352', '1.11.599']),
        ('wafv2', ['1.9.234', '1.11.352', '1.11.599']),
        ('wellarchitected', ['1.9.234', '1.11.352', '1.11.599']),
        ('wisdom', ['1.11.352', '1.11.599']),
        ('workdocs', ['1.9.234', '1.11.352', '1.11.599']),
        ('worklink', ['1.9.234', '1.11.352', '1.11.599']),
        ('workmail', ['1.9.234', '1.11.352', '1.11.599']),
        ('workmailmessageflow', ['1.9.234', '1.11.352', '1.11.599']),
        ('workspaces', ['1.9.234', '1.11.352', '1.11.599']),
        ('workspaces-instances', ['1.11.599']),
        ('workspaces-thin-client', ['1.11.352', '1.11.599']),
        ('workspaces-web', ['1.11.352', '1.11.599']),
        ('xray', ['1.9.234', '1.11.352', '1.11.599']),
    )
    options = {
        **{
            "shared": [True, False],
            "fPIC": [True, False],
            "min_size": [True, False],
        },
        **{sdk_name: [None, True, False] for sdk_name, _ in _sdks},
    }
    default_options = {
        **{
            "shared": False,
            "fPIC": True,
            "min_size": False
        },
        **{sdk_name: None for sdk_name, _ in _sdks},
        # Overrides
        "s3": True,  # TODO: testing
        "s3-crt": True,  # TODO: Testing too
        "monitoring": True  # TODO: Clarify why monitoring is True by default
    }

    short_paths = True

    @property
    def _internal_requirements(self):
        # These modules and dependencies come from https://github.com/aws/aws-sdk-cpp/blob/1.11.352/cmake/sdksCommon.cmake#L147 and below
        # Additionally Core is added to all modules automatically
        return {
            "access-management": ["iam", "cognito-identity"],
            "identity-management": ["cognito-identity", "sts"],
            "queues": ["sqs"],
            "s3-encryption": ["s3", "kms"],
            "text-to-speech": ["polly"],
            "transfer": ["s3"],
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        # Main modules are true by default, but the user can set them to false
        for module in self._internal_requirements:
            setattr(self.options, module, True)

        # Remove all sdk options not belonging to the current version
        for sdk_name, sdk_versions in self._sdks:
            if self.version not in sdk_versions:
                self.options.rm_safe(sdk_name)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        # If the user does not specify a value for a specific sdk:
        # - Set it to True if it's a dependency of a main module that is set to True
        for module, dependencies in self._internal_requirements.items():
            if self.options.get_safe(module):
                for dependency in dependencies:
                    # Don't listen to the linter, get_safe should be compared like this to None
                    # TODO: Remove str comparison when Conan 1 is disabled
                    if str(self.options.get_safe(dependency)) == "None":
                        setattr(self.options, dependency, True)

        # - Otherwise set it to False
        # This way there are no None options past this method, and we can control default values
        # of the dependencies of the main modules but still give the user control over them
        for sdk_name, sdk_versions in self._sdks:
            # == None is true for both "was deleted" and "was not set by the user",
            # ensure we only try to set the value to false for the latter
            if self.version in sdk_versions and self.options.get_safe(sdk_name) == None:
                setattr(self.options, sdk_name, False)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # These versions come from prefetch_crt_dependency.sh,
        # dont bump them independently, check the file
        # Create the new versions for the dependencies in the order shown
        # in that script, they are mostly topo sorted
        if self.version == "1.11.599":
            self.requires("aws-crt-cpp/0.32.8", transitive_headers=True)
            self.requires("aws-c-auth/0.9.0")
            self.requires("aws-c-cal/0.9.1")
            self.requires("aws-c-common/0.12.3")
            self.requires("aws-c-compression/0.3.1")
            self.requires("aws-c-event-stream/0.5.4")
            self.requires("aws-c-http/0.10.1")
            self.requires("aws-c-io/0.19.1")
            self.requires("aws-c-mqtt/0.13.1")
            if self.options.get_safe("s3-crt"):
                self.requires("aws-c-s3/0.8.0")
            self.requires("aws-c-sdkutils/0.2.4")  # No mention of this in the code
            self.requires("aws-checksums/0.2.6")
        elif self.version == "1.11.352":
            self.requires("aws-crt-cpp/0.26.9", transitive_headers=True)
            self.requires("aws-c-auth/0.7.16")
            self.requires("aws-c-cal/0.6.14")
            self.requires("aws-c-common/0.9.15")
            self.requires("aws-c-compression/0.2.18")  # No mention of this in the code
            self.requires("aws-c-event-stream/0.4.2")
            self.requires("aws-c-http/0.8.1")
            self.requires("aws-c-io/0.14.7")
            self.requires("aws-c-mqtt/0.10.3")
            if self.options.get_safe("s3-crt"):
                self.requires("aws-c-s3/0.5.5")
            self.requires("aws-c-sdkutils/0.1.15")  # No mention of this in the code
            self.requires("aws-checksums/0.1.18")
            # missing aws-lc, but only needed as openssl replacement if USE_OPENSSL is OFF
        elif self.version == "1.9.234":
            self.requires("aws-crt-cpp/0.17.1a", transitive_headers=True)
            self.requires("aws-c-auth/0.6.4")
            self.requires("aws-c-cal/0.5.12")
            self.requires("aws-c-common/0.6.11")
            self.requires("aws-c-compression/0.2.14")
            self.requires("aws-c-event-stream/0.2.7")
            self.requires("aws-c-http/0.6.7")
            self.requires("aws-c-io/0.10.9")
            self.requires("aws-c-mqtt/0.7.8")
            if self.options.get_safe("s3-crt"):
                self.requires("aws-c-s3/0.1.26")
            self.requires("aws-checksums/0.1.12")
        if self.settings.os != "Windows":
            # Used transitively in core/utils/crypto/openssl/CryptoImpl.h public header
            self.requires("openssl/[>=1.1 <4]", transitive_headers=True)
            # Used transitively in core/http/curl/CurlHandleContainer.h public header
            self.requires("libcurl/[>=7.78.0 <9]", transitive_headers=True)
        if self.settings.os == "Linux":
            # Pulseaudio -> libcap, libalsa only support linux, don't use pulseaudio on other platforms
            if self.options.get_safe("text-to-speech"):
                # Used transitively in text-to-speech/PulseAudioPCMOutputDriver.h public header
                self.requires("pulseaudio/14.2", transitive_headers=True, transitive_libs=True)
        # zlib is used if ENABLE_ZLIB_REQUEST_COMPRESSION is enabled, set ot ON by default
        self.requires("zlib/[>=1.2.11 <2]")

    def validate_build(self):
        if self.settings_build.os == "Windows" and self.settings.os == "Android":
            raise ConanInvalidConfiguration("Cross-building from Windows to Android is not supported")

        if (self.options.shared
                and self.settings.compiler == "gcc"
                and Version(self.settings.compiler.version) < "6.0"):
            raise ConanInvalidConfiguration(
                "Doesn't support gcc5 / shared. "
                "See https://github.com/conan-io/conan-center-index/pull/4401#issuecomment-802631744"
            )

    def validate(self):
        if is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Static runtime is not working for more recent releases")
        if (is_msvc(self) and self.options.shared
                and not self.dependencies["aws-c-common"].options.shared):
            raise ConanInvalidConfiguration(f"{self.ref} with shared is not supported with aws-c-common static")

        # If the user has explicitly set a main module dependency to False,
        # error out if the main module itself is not also disabled
        for main_module, dependencies in self._internal_requirements.items():
            if self.options.get_safe(main_module):
                for internal_requirement in dependencies:
                    if not self.options.get_safe(internal_requirement):
                        raise ConanInvalidConfiguration(f"-o={self.ref}:{main_module}=True requires -o={self.ref}:{internal_requirement}=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def _enabled_sdks(self):
        for sdk in self._sdks:
            if self.options.get_safe(sdk[0]):
                yield sdk

    def generate(self):
        tc = CMakeToolchain(self)
        # All option() are defined before project() in upstream CMakeLists,
        # therefore we must use cache_variables

        build_only = ["core"]
        for sdk_name, _ in self._enabled_sdks():
            build_only.append(sdk_name)
        tc.cache_variables["BUILD_ONLY"] = ";".join(build_only)

        tc.cache_variables["ENABLE_UNITY_BUILD"] = True
        tc.cache_variables["ENABLE_TESTING"] = False
        tc.cache_variables["AUTORUN_UNIT_TESTS"] = False
        tc.cache_variables["BUILD_DEPS"] = False
        if self.settings.os != "Windows":
            tc.cache_variables["USE_OPENSSL"] = True
            tc.cache_variables["ENABLE_OPENSSL_ENCRYPTION"] = True

        tc.cache_variables["MINIMIZE_SIZE"] = self.options.min_size
        if is_msvc(self):
            tc.cache_variables["FORCE_SHARED_CRT"] = not is_msvc_static_runtime(self)

        if cross_building(self):
            tc.cache_variables["CURL_HAS_H2_EXITCODE"] = "0"
            tc.cache_variables["CURL_HAS_H2_EXITCODE__TRYRUN_OUTPUT"] = ""
            tc.cache_variables["CURL_HAS_TLS_PROXY_EXITCODE"] = "0"
            tc.cache_variables["CURL_HAS_TLS_PROXY_EXITCODE__TRYRUN_OUTPUT"] = ""
        if is_msvc(self):
            tc.preprocessor_definitions["_SILENCE_CXX17_OLD_ALLOCATOR_MEMBERS_DEPRECATION_WARNING"] = "1"
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Disable warnings as errors
        if self.version == "1.9.234":
            replace_in_file(
                self, os.path.join(self.source_folder, "cmake", "compiler_settings.cmake"),
                'list(APPEND AWS_COMPILER_WARNINGS "-Wall" "-Werror" "-pedantic" "-Wextra")', "",
            )

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _res_folder(self):
        return "res"

    def _create_project_cmake_module(self):
        # package files needed to build other components (e.g. aws-cdi-sdk) with this SDK
        dependant_files = [
            "cmake/compiler_settings.cmake",
            "cmake/initialize_project_version.cmake",
            "cmake/utilities.cmake",
            "cmake/sdk_plugin_conf.cmake",
            "toolchains/cmakeProjectConfig.cmake",
            "toolchains/pkg-config.pc.in"
        ]
        if Version(self.version) >= "1.11.352":
            dependant_files.append("src/aws-cpp-sdk-core/include/aws/core/VersionConfig.h")
        else:
            dependant_files.append("aws-cpp-sdk-core/include/aws/core/VersionConfig.h")
        for file in dependant_files:
            copy(self, file, src=self.source_folder, dst=os.path.join(self.package_folder, self._res_folder))
            replace_in_file(
                self, os.path.join(self.package_folder, self._res_folder, file),
                "CMAKE_CURRENT_SOURCE_DIR", "AWS_NATIVE_SDK_ROOT",
                strict=False,
            )

        # avoid getting error from hook
        rename(self, os.path.join(self.package_folder, self._res_folder, "toolchains", "cmakeProjectConfig.cmake"),
               os.path.join(self.package_folder, self._res_folder, "toolchains", "cmakeProjectConf.cmake"))
        replace_in_file(
            self, os.path.join(self.package_folder, self._res_folder, "cmake", "utilities.cmake"),
            "cmakeProjectConfig.cmake", "cmakeProjectConf.cmake",
        )

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if is_msvc(self):
            copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            rm(self, "*.lib", os.path.join(self.package_folder, "bin"))

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        self._create_project_cmake_module()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "AWSSDK")

        sdk_plugin_conf = os.path.join(self._res_folder, "cmake", "sdk_plugin_conf.cmake")
        self.cpp_info.set_property("cmake_build_modules", [sdk_plugin_conf])

        # core component
        self.cpp_info.components["core"].set_property("cmake_target_name", "AWS::aws-sdk-cpp-core")
        self.cpp_info.components["core"].set_property("pkg_config_name", "aws-sdk-cpp-core")
        self.cpp_info.components["core"].libs = ["aws-cpp-sdk-core"]
        self.cpp_info.components["core"].requires = [
            "aws-crt-cpp::aws-crt-cpp",
            "aws-c-auth::aws-c-auth",
            "aws-c-cal::aws-c-cal",
            "aws-c-common::aws-c-common",
            "aws-c-compression::aws-c-compression",
            "aws-c-event-stream::aws-c-event-stream",
            "aws-c-http::aws-c-http",
            "aws-c-io::aws-c-io",
            "aws-c-mqtt::aws-c-mqtt",
            "aws-checksums::aws-checksums",
            "zlib::zlib"
        ]

        if Version(self.version) >= "1.11.352":
            self.cpp_info.components["core"].requires.extend([
                "aws-c-sdkutils::aws-c-sdkutils",
            ])

        # TODO: We might want to set cmake_components if the targets dont match the component names
        for sdk, _ in self._enabled_sdks():
            self.cpp_info.components[sdk].set_property("cmake_target_name", f"AWS::aws-sdk-cpp-{sdk}")
            self.cpp_info.components[sdk].set_property("pkg_config_name", f"aws-sdk-cpp-{sdk}")
            self.cpp_info.components[sdk].requires = ["core"]
            if sdk in self._internal_requirements:
                self.cpp_info.components[sdk].requires.extend(self._internal_requirements[sdk])
            self.cpp_info.components[sdk].libs = ["aws-cpp-sdk-" + sdk]

            # TODO: Remove, Conan 1 legacy, but this component now exists, it's part of the api
            component_alias = f"aws-sdk-cpp-{sdk}_alias"  # to emulate COMPONENTS names for find_package()
            self.cpp_info.components[component_alias].requires = [sdk]

        # specific system_libs, frameworks and requires of components
        if self.settings.os == "Windows":
            self.cpp_info.components["core"].system_libs.extend([
                "winhttp", "wininet", "bcrypt", "userenv", "version", "ws2_32"
            ])
            if self.options.get_safe("text-to-speech"):
                self.cpp_info.components["text-to-speech"].system_libs.append("winmm")
        else:
            self.cpp_info.components["core"].requires.extend(["libcurl::curl", "openssl::openssl"])

        if self.settings.os == "Linux":
            if self.options.get_safe("text-to-speech"):
                self.cpp_info.components["text-to-speech"].requires.append("pulseaudio::pulseaudio")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["core"].system_libs.append("atomic")

        if self.options.get_safe("s3-crt"):
            self.cpp_info.components["s3-crt"].requires.append("aws-c-s3::aws-c-s3")

        if self.settings.os == "Macos":
            if self.options.get_safe("text-to-speech"):
                self.cpp_info.components["text-to-speech"].frameworks.extend(["CoreAudio", "AudioToolbox"])

        libcxx = stdcpp_library(self)
        if libcxx:
            self.cpp_info.components["core"].system_libs.append(libcxx)

        self.cpp_info.components["plugin_scripts"].requires = ["core"]
        self.cpp_info.components["plugin_scripts"].builddirs.extend([
            os.path.join(self._res_folder, "cmake"),
            os.path.join(self._res_folder, "toolchains")])

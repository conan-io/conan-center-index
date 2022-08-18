cmake_minimum_required(VERSION 3.7)
# google-cloud-cpp consume some protos generated with the grpc_cpp_plugin,
# these protos (as header + library) are not available in googleapis package,
# so we need to generate them here.
#
# Approach here is to generate required grpc-protos, build them into some
# targets, transitively link googleapis libraries and use those targets
# in the google-cloud-cpp project (with the same names they had when vendored).
#
# Depending on the 'googleapis' versions, some protos might be moved from vXbetaY
# folders to vX stable ones... or some protos might be available or not in
# libraries provided by 'googleapis'. Those that are not available are also included
# in the targets generated here

set(_gRPC_PROTO_GENS_DIR ${CMAKE_BINARY_DIR}/proto_grpc)
file(MAKE_DIRECTORY ${_gRPC_PROTO_GENS_DIR})
set(GOOGLEAPIS_GRPC_PROTOS_TARGETS "")

include(googleapis-helpers.cmake)

googleapis_grpc_proto_library(iam_protos 
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/iam/admin"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/iam/credentials"
    )
googleapis_grpc_proto_library(iam_v1_policy_protos 
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/iam/v1/iam_policy.proto"
    )
googleapis_grpc_proto_library(longrunning_operations_protos 
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/longrunning"
    )
googleapis_grpc_proto_library(rpc_error_details_protos 
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/rpc/error_details.proto"
    )
googleapis_grpc_proto_library(rpc_status_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/rpc/status.proto"
    )
googleapis_grpc_proto_library(bigtable_protos 
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/bigtable"
    )
googleapis_grpc_proto_library(cloud_bigquery_protos
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery" 
    PROTOS 
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/connection/v1beta1/connection.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/migration/v2alpha/assessment_task.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/migration/v2alpha/migration_entities.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/migration/v2alpha/migration_error_details.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/migration/v2alpha/migration_metrics.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/migration/v2alpha/translation_task.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/migration/v2alpha/migration_service.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/migration/v2alpha/translation_service.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/reservation/v1beta1/reservation.proto"
        )
googleapis_grpc_proto_library(logging_protos
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/logging"
    )
googleapis_grpc_proto_library(pubsub_protos 
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/pubsub"
    PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/pubsub/v1beta2/pubsub.proto"
    )
googleapis_grpc_proto_library(spanner_protos 
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/spanner"
    )
googleapis_grpc_proto_library(api_client_protos 
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api" 
    PROTOS 
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/error_reason.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/serviceusage/v1beta1/resources.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/serviceusage/v1beta1/serviceusage.proto"
    )

install(
    TARGETS ${GOOGLEAPIS_GRPC_PROTOS_TARGETS}
    EXPORT googleapis-targets
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
            COMPONENT google_cloud_cpp_runtime
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
            COMPONENT google_cloud_cpp_runtime
            NAMELINK_SKIP
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
            COMPONENT google_cloud_cpp_development)

install(
    EXPORT googleapis-targets
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/google_cloud_cpp_googleapis"
    COMPONENT google_cloud_cpp_development)


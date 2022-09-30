cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(STANDARD_ASN1_FILES
 BIT_STRING.c
 INTEGER.c
 NativeEnumerated.c
 NativeInteger.c
 OBJECT_IDENTIFIER.c
 OCTET_STRING.c
 asn_SEQUENCE_OF.c
 asn_SET_OF.c
 asn_codecs_prim.c
 ber_decoder.c
 ber_tlv_length.c
 ber_tlv_tag.c
 constr_SEQUENCE.c
 constr_SEQUENCE_OF.c
 constr_SET_OF.c
 constr_TYPE.c
 constraints.c
 der_encoder.c
 per_decoder.c
 per_encoder.c
 per_opentype.c
 per_support.c
 xer_decoder.c
 xer_encoder.c
 xer_support.c
)

set(GENERATED_FILES
  MyTypes.c
  MyInt.c
)

add_custom_command(
  OUTPUT ${GENERATED_FILES} ${STANDARD_ASN1_FILES}
  COMMAND asn1c -S ${SUPPORT_PATH} MyModule.asn1
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  DEPENDS MyModule.asn1
)

add_executable(${PROJECT_NAME} test_package.c ${GENERATED_FILES} ${STANDARD_ASN1_FILES})
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_BINARY_DIR})

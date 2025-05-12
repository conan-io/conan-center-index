#ifdef ASIO_GRPC_V2
#include <agrpc/asio_grpc.hpp>
#else
#include <agrpc/asioGrpc.hpp>
#endif
#include <boost/asio/post.hpp>

#ifndef CROSSCOMPILING
#include <grpcpp/create_channel.h>
#include <test.grpc.pb.h>
#endif

int main() {
  agrpc::GrpcContext grpc_context{std::make_unique<grpc::CompletionQueue>()};

  boost::asio::post(grpc_context, [] {});

#ifndef CROSSCOMPILING
  boost::asio::post(grpc_context, []() {
    [[maybe_unused]] auto stub = test::Test::NewStub(grpc::CreateChannel(
        "localhost:50051", grpc::InsecureChannelCredentials()));
    [[maybe_unused]] test::TestRequest request;
  });
#endif
}

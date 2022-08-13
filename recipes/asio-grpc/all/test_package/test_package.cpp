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
  std::unique_ptr<test::Test::Stub> stub;
  grpc::ClientContext client_context;
  std::unique_ptr<grpc::ClientAsyncResponseReader<test::TestReply>> reader;
  test::TestRequest request;
  test::TestReply response;
  grpc::Status status;

  boost::asio::post(grpc_context, [&]() {
    stub = test::Test::NewStub(grpc::CreateChannel(
        "localhost:50051", grpc::InsecureChannelCredentials()));
    request.set_message("hello");
    reader = agrpc::request(&test::Test::Stub::AsyncUnary, *stub,
                            client_context, request, grpc_context);
    agrpc::finish(reader, response, status,
                  boost::asio::bind_executor(grpc_context, [](bool) {}));
  });
#endif
}

// Licensed to the Apache Software Foundation (ASF) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The ASF licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

/**
 * this is a simplified version of the echo_c++ example in brpc
 */

#include <butil/logging.h>
#include <brpc/server.h>
#include <butil/time.h>
#include <brpc/channel.h>
#include "echo.pb.h"

DEFINE_bool(echo_attachment, true, "Echo attachment as well");
DEFINE_int32(idle_timeout_s, -1, "Connection will be closed if there is no "
             "read/write operations during the last `idle_timeout_s'");
DEFINE_string(attachment, "", "Carry this along with requests");
DEFINE_string(protocol, "baidu_std", "Protocol type. Defined in src/brpc/options.proto");
DEFINE_string(connection_type, "", "Connection type. Available values: single, pooled, short");
DEFINE_string(load_balancer, "", "The algorithm for load balancing");
DEFINE_int32(timeout_ms, 100, "RPC timeout in milliseconds");
DEFINE_int32(max_retry, 3, "Max retries(not including the first RPC)"); 

namespace example {
class EchoServiceImpl : public EchoService {
public:
    EchoServiceImpl() {};
    virtual ~EchoServiceImpl() {};
    virtual void Echo(google::protobuf::RpcController* cntl_base,
                      const EchoRequest* request,
                      EchoResponse* response,
                      google::protobuf::Closure* done) {
        brpc::ClosureGuard done_guard(done);

        brpc::Controller* cntl =
            static_cast<brpc::Controller*>(cntl_base);

        LOG(INFO) << "Received request[log_id=" << cntl->log_id() 
                  << "] from " << cntl->remote_side() 
                  << " to " << cntl->local_side()
                  << ": " << request->message()
                  << " (attached=" << cntl->request_attachment() << ")";

        response->set_message(request->message());

        if (FLAGS_echo_attachment) {
            cntl->response_attachment().append(cntl->request_attachment());
        }
    }
};
}

int main(int argc, char* argv[]) {
    // Set up and start the server.
    brpc::Server server;
    example::EchoServiceImpl echo_service_impl;
    if (server.AddService(&echo_service_impl, 
                          brpc::SERVER_DOESNT_OWN_SERVICE) != 0) {
        LOG(ERROR) << "Fail to add service";
        return -1;
    }
    brpc::ServerOptions server_opts;
    server_opts.idle_timeout_sec = FLAGS_idle_timeout_s;
    if (server.Start(0 /* pick available port */, &server_opts) != 0) {
        LOG(ERROR) << "Fail to start EchoServer";
        return -1;
    }
    auto listen_port = server.listen_address().port;
    LOG(INFO) << "Server running at " << listen_port;

    // client just sends one request to server
    brpc::Channel channel;
    brpc::ChannelOptions client_channel_opts;
    client_channel_opts.protocol = FLAGS_protocol;
    client_channel_opts.connection_type = FLAGS_connection_type;
    client_channel_opts.timeout_ms = FLAGS_timeout_ms;
    client_channel_opts.max_retry = FLAGS_max_retry;

    auto server_connect = std::string("0.0.0.0:") + std::to_string(listen_port);
    if (channel.Init(server_connect.c_str(), FLAGS_load_balancer.c_str(), &client_channel_opts) != 0) {
        LOG(ERROR) << "Fail to initialize channel";
        return -1;
    }
    example::EchoService_Stub stub(&channel);

    example::EchoRequest request;
    example::EchoResponse response;
    brpc::Controller cntl;

    request.set_message("hello world");
    cntl.set_log_id(0);
    cntl.request_attachment().append(FLAGS_attachment);
    stub.Echo(&cntl, &request, &response, NULL /* block until response or error */);
    if (!cntl.Failed()) {
      LOG(INFO) << "Received response from " << cntl.remote_side()
        << " to " << cntl.local_side()
        << ": " << response.message() << " (attached="
        << cntl.response_attachment() << ")"
        << " latency=" << cntl.latency_us() << "us";
    } else {
      LOG(WARNING) << cntl.ErrorText();
    }

    // shutdown the server
    if (server.Stop(0) != 0) {
      LOG(ERROR) << "Server stop failed";
      return -1;
    } else {
      LOG(INFO) << "Server stopped";
    }

    return 0;
}

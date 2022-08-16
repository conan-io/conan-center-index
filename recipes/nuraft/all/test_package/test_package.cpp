/**
 *
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  The ASF licenses
 * this file to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <stdlib.h>

#include <cassert>
#include <iostream>
#include <libnuraft/in_memory_log_store.hxx>
#include <libnuraft/nuraft.hxx>

using namespace nuraft;

struct ex_logger : ::nuraft::logger {
  void debug(const std::string& log_line) override {
    std::cout << log_line << std::endl;
  }

  void info(const std::string& log_line) override {
    std::cout << log_line << std::endl;
  }

  void warn(const std::string& log_line) override {
    std::cout << log_line << std::endl;
  }

  void err(const std::string& log_line) override {
    std::cout << log_line << std::endl;
  }

  void set_level(int) override {}

  void put_details(int level, const char* source_file, const char* func_name,
                   size_t line_number, const std::string& log_line) override {
    std::cout << source_file << ":" << func_name << "#" << line_number << " : "
              << log_line << std::endl;
  }
};

class simple_state_mgr : public state_mgr {
 public:
  simple_state_mgr(int32 srv_id) : srv_id_(srv_id) {}

 public:
  virtual ptr<cluster_config> load_config() {
    ptr<cluster_config> conf = cs_new<cluster_config>();
    conf->get_servers().push_back(
        cs_new<srv_config>(1, "tcp://127.0.0.1:9001"));
    return conf;
  }

  virtual void save_config(const cluster_config& config) {}
  virtual void save_state(const srv_state& state) {}
  virtual ptr<srv_state> read_state() { return cs_new<srv_state>(); }

  virtual ptr<log_store> load_log_store() { return cs_new<inmem_log_store>(); }

  virtual int32 server_id() { return srv_id_; }

  virtual void system_exit(const int exit_code) {
    std::cout << "system exiting with code " << exit_code << std::endl;
  }

 private:
  int32 srv_id_;
};

class echo_state_machine : public state_machine {
 public:
  echo_state_machine() : lock_(), last_commit_idx_(0) {}

 public:
  virtual ptr<buffer> commit(const ulong log_idx, buffer& data) {
    auto_lock(lock_);
    std::cout << "commit message [" << log_idx << "]"
              << ": " << reinterpret_cast<const char*>(data.data())
              << std::endl;
    last_commit_idx_ = log_idx;
    return nullptr;
  }

  virtual ptr<buffer> pre_commit(const ulong log_idx, buffer& data) {
    auto_lock(lock_);
    std::cout << "pre-commit [" << log_idx << "]"
              << ": " << reinterpret_cast<const char*>(data.data())
              << std::endl;
    return nullptr;
  }

  virtual void rollback(const ulong log_idx, buffer& data) {
    auto_lock(lock_);
    std::cout << "rollback [" << log_idx << "]"
              << ": " << reinterpret_cast<const char*>(data.data())
              << std::endl;
  }

  virtual void save_snapshot_data(snapshot& s, const ulong offset,
                                  buffer& data) {}
  virtual bool apply_snapshot(snapshot& s) { return true; }

  virtual int read_snapshot_data(snapshot& s, const ulong offset,
                                 buffer& data) {
    return 0;
  }

  virtual ptr<snapshot> last_snapshot() { return ptr<snapshot>(); }

  virtual void create_snapshot(snapshot& s,
                               async_result<bool>::handler_type& when_done) {}

  virtual ulong last_commit_index() { return last_commit_idx_; }

 private:
  std::mutex lock_;
  ulong last_commit_idx_;
};

int main(int argc, char** argv) {
  // State manager (RAFT log store, config).
  ptr<state_mgr> smgr(cs_new<simple_state_mgr>(1));

  // State machine.
  ptr<state_machine> smachine(cs_new<echo_state_machine>());

  // Parameters.
  raft_params params;
  params.with_election_timeout_lower(200)
      .with_election_timeout_upper(400)
      .with_hb_interval(100)
      .with_max_append_size(100)
      .with_rpc_failure_backoff(50);

  // ASIO service.
  ptr<logger> l = cs_new<ex_logger>();
  ptr<asio_service> asio_svc_ = cs_new<asio_service>();
  ptr<rpc_listener> listener(asio_svc_->create_rpc_listener((ushort)(9001), l));
  ptr<delayed_task_scheduler> scheduler = asio_svc_;
  ptr<rpc_client_factory> rpc_cli_factory = asio_svc_;

  // Run server.
  context* ctx(new context(smgr, smachine, listener, l, rpc_cli_factory,
                           scheduler, params));
  ptr<raft_server> server(cs_new<raft_server>(ctx));
  server->shutdown();
  return 0;
}

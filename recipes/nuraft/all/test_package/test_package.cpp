#include <cassert>
#include <cstdlib>
#include <iostream>
#include <libnuraft/in_memory_log_store.hxx>
#include <libnuraft/nuraft.hxx>

using namespace nuraft;

struct ex_logger : ::nuraft::logger {
  void set_level(int) override {}
  void debug(const std::string&) override {}
  void info(const std::string&) override {}
  void warn(const std::string&) override {}
  void err(const std::string& log_line) override {
    std::cout << log_line << std::endl;
  }

  void put_details(int, const char*, const char*, size_t,
                   const std::string&) override {}
};

class simple_state_mgr : public state_mgr {
 public:
  simple_state_mgr(int32 srv_id) : srv_id_(srv_id) {}

 public:
  ptr<cluster_config> load_config() override {
    ptr<cluster_config> conf = cs_new<cluster_config>();
    conf->get_servers().push_back(
        cs_new<srv_config>(1, "tcp://127.0.0.1:9001"));
    return conf;
  }

  void save_config(const cluster_config&) override {}
  void save_state(const srv_state&) override {}
  ptr<srv_state> read_state() override { return cs_new<srv_state>(); }

  ptr<log_store> load_log_store() override { return cs_new<inmem_log_store>(); }

  int32 server_id() override { return srv_id_; }

  void system_exit(const int) override {}

 private:
  int32 srv_id_;
};

class echo_state_machine : public state_machine {
 public:
  echo_state_machine() : last_commit_idx_(0) {}

 public:
  ptr<buffer> commit(const ulong log_idx, buffer&) override {
    last_commit_idx_ = log_idx;
    return nullptr;
  }

  ptr<buffer> pre_commit(const ulong, buffer&) override { return nullptr; }

  void rollback(const ulong, buffer&) override {}

  void save_snapshot_data(snapshot&, const ulong, buffer&) override {}
  bool apply_snapshot(snapshot&) override { return true; }

  int read_snapshot_data(snapshot&, const ulong, buffer&) override { return 0; }

  ptr<snapshot> last_snapshot() override { return ptr<snapshot>(); }

  void create_snapshot(snapshot&, async_result<bool>::handler_type&) override {}

  ulong last_commit_index() override { return last_commit_idx_; }

 private:
  ulong last_commit_idx_;
};

int main(int argc, char** argv) {
  // State manager (RAFT log store, config).
  ptr<state_mgr> smgr(cs_new<simple_state_mgr>(1));

  // State machine.
  ptr<state_machine> smachine(cs_new<echo_state_machine>());

  // Parameters.
  raft_params params;

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

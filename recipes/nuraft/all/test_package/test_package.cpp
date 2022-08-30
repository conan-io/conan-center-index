#include <cassert>
#include <cstdlib>
#include <iostream>
#include <nuraft.hxx>

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
  // State machine.
  ptr<state_machine> smachine(cs_new<echo_state_machine>());

  // Parameters.
  raft_params params;

  // ASIO service.
  ptr<logger> l = cs_new<ex_logger>();
  ptr<asio_service> asio_svc_ = cs_new<asio_service>();
  ptr<rpc_listener> listener(asio_svc_->create_rpc_listener((ushort)(9001), l));
  return 0;
}

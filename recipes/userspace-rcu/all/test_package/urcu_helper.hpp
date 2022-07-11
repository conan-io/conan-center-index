/*********************************************************************************
 * Modifications Copyright 2017-2019 eBay Inc.
 *
 * Author/Developer(s): Harihara Kadayam, Aditya Marella
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *    https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 *distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 *WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 *License for the specific language governing permissions and limitations under
 *the License.
 *
 *********************************************************************************/
#pragma once

#if __cplusplus <= 201703L
#if defined __clang__ or defined __GNUC__
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpedantic"
#endif
#include <urcu.h>
#if defined __clang__ or defined __GNUC__
#pragma GCC diagnostic pop
#endif
#else
#include <urcu.h>
#endif
#include <urcu-call-rcu.h>
#include <urcu/static/urcu-qsbr.h>

#include <functional>
#include <memory>
#include <mutex>
#include <tuple>

namespace test_package {

class urcu_ctl {
 public:
  static thread_local bool _rcu_registered_already;

  static void register_rcu() { rcu_register_thread(); }

  static void declare_quiscent_state() { rcu_quiescent_state(); }

  static void unregister_rcu() { rcu_unregister_thread(); }

  static void sync_rcu() { synchronize_rcu(); }
};

/* TODO : Try an ensure the lifetime of this object does not exceed the
 * scoped_ptr that created it */
template <typename T>
class _urcu_access_ptr {
 public:
  T* m_p;

  _urcu_access_ptr(T* p) : m_p(p) {}
  ~_urcu_access_ptr() { rcu_read_unlock(); }
  _urcu_access_ptr(const _urcu_access_ptr& other) = delete;
  _urcu_access_ptr& operator=(const _urcu_access_ptr& other) = delete;
  _urcu_access_ptr(_urcu_access_ptr&& other) noexcept {
    std::swap(m_p, other.m_p);
  }

  const T* operator->() const { return m_p; }
  T* operator->() { return m_p; }
  T* get() const { return m_p; }
};

/* Simplified urcu pointer access */
template <typename T, typename... Args>
class urcu_scoped_ptr {
 public:
  template <class... Args1>
  urcu_scoped_ptr(Args1&&... args) : m_args(std::forward<Args1>(args)...) {
    m_cur_obj = new T(std::forward<Args1>(args)...);
  }

  urcu_scoped_ptr(urcu_scoped_ptr const&) = delete;
  urcu_scoped_ptr(urcu_scoped_ptr&&) = delete;
  urcu_scoped_ptr& operator=(urcu_scoped_ptr const&) = delete;
  urcu_scoped_ptr& operator=(urcu_scoped_ptr&&) = delete;

  ~urcu_scoped_ptr() {
    rcu_read_lock();  // Take read-fence prior to accessing m_cur_obj
    if (m_cur_obj) delete rcu_dereference(m_cur_obj);
    rcu_read_unlock();
  }

  _urcu_access_ptr<T> access() const {
    rcu_read_lock();  // Take read-fence prior to accessing m_cur_obj
    return _urcu_access_ptr<T>(rcu_dereference(
        m_cur_obj));  // This object will read_unlock when it's destroyed
  }

  void update(const std::function<void(T*)>& edit_cb) {
    T* old_obj{nullptr};
    {
      std::lock_guard<std::mutex> l(m_updater_mutex);
      auto new_obj =
          new T(*rcu_dereference(m_cur_obj));  // Create new obj from old obj
      edit_cb(new_obj);

      old_obj = rcu_xchg_pointer(&m_cur_obj, new_obj);
    }
    synchronize_rcu();
    if (old_obj) delete old_obj;
  }

  T* make_and_exchange(const bool sync_rcu_now = true) {
    return _make_and_exchange(sync_rcu_now, m_args,
                              std::index_sequence_for<Args...>());
  }

 private:
  template <std::size_t... Is>
  T* _make_and_exchange(const bool sync_rcu_now,
                        const std::tuple<Args...>& tuple,
                        std::index_sequence<Is...>) {
    auto new_obj = new T(std::get<Is>(
        tuple)...);  // Make new object with saved constructor params
    auto old_obj = rcu_xchg_pointer(&m_cur_obj, new_obj);
    if (sync_rcu_now) {
      synchronize_rcu();
    }
    return old_obj;
  }

 private:
  // Args to hold onto for new buf
  std::tuple<Args...> m_args;

  // RCU protected pointer
  T* m_cur_obj = nullptr;

  // Mutex to protect multiple copiers to run the copy step in parallel.
  std::mutex m_updater_mutex;
};

#define RCU_REGISTER_INIT \
  thread_local bool test_package::urcu_ctl::_rcu_registered_already = false;
}  // namespace test_package

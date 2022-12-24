// // Copyright Takatoshi Kondo 2017
// //
// // Distributed under the Boost Software License, Version 1.0.
// // (See accompanying file LICENSE_1_0.txt or copy at
// // http://www.boost.org/LICENSE_1_0.txt)

// #include <iostream>
// #include <iomanip>
// #include <set>

// #include <mqtt_server_cpp.hpp>

// #include <boost/lexical_cast.hpp>
// #include <boost/multi_index_container.hpp>
// #include <boost/multi_index/ordered_index.hpp>
// #include <boost/multi_index/member.hpp>
// #include <boost/multi_index/composite_key.hpp>

// namespace mi = boost::multi_index;

// using con_t = MQTT_NS::server_tls_ws<>::endpoint_t;
// using con_sp_t = std::shared_ptr<con_t>;

// struct sub_con
// {
//     sub_con(MQTT_NS::buffer topic, con_sp_t con, MQTT_NS::qos qos_value)
//         : topic(std::move(topic))
//         , con(std::move(con))
//         , qos_value(qos_value)
//     {
//     }
//     MQTT_NS::buffer topic;
//     con_sp_t con;
//     MQTT_NS::qos qos_value;
// };

// struct tag_topic
// {
// };
// struct tag_con
// {
// };
// struct tag_con_topic
// {
// };

// using mi_sub_con
//     = mi::multi_index_container<sub_con,
//         mi::indexed_by<mi::ordered_unique<mi::tag<tag_con_topic>,
//                            mi::composite_key<sub_con,
//                                               BOOST_MULTI_INDEX_MEMBER(sub_con, con_sp_t, con),
//                                               BOOST_MULTI_INDEX_MEMBER(
//                                                   sub_con, MQTT_NS::buffer, topic)> >,
//                                     mi::ordered_non_unique<mi::tag<tag_topic>,
//                                         BOOST_MULTI_INDEX_MEMBER(sub_con, MQTT_NS::buffer, topic)>,
//                                     mi::ordered_non_unique<mi::tag<tag_con>,
//                                         BOOST_MULTI_INDEX_MEMBER(sub_con, con_sp_t, con)> > >;


// inline void close_proc(std::set<con_sp_t>& cons, mi_sub_con& subs, con_sp_t const& con)
// {
//     cons.erase(con);

//     auto& idx = subs.get<tag_con>();
//     auto r = idx.equal_range(con);
//     idx.erase(r.first, r.second);
// }

// int main(int argc, char** argv)
// {

//     MQTT_NS::setup_log();

//     boost::asio::io_context ioc;

//     std::uint16_t port = 15432;
//     std::string cert = "server.crt.pem";
//     std::string key = "server.key.pem";

//     boost::asio::ssl::context ctx(boost::asio::ssl::context::tlsv12);
//     ctx.set_options(
//         boost::asio::ssl::context::default_workarounds | boost::asio::ssl::context::single_dh_use);
//     ctx.use_certificate_chain_file(cert);
//     ctx.use_private_key_file(key, boost::asio::ssl::context::pem);

//     auto s = MQTT_NS::server_tls_ws<>(
//         boost::asio::ip::tcp::endpoint(boost::asio::ip::tcp::v4(), port), std::move(ctx), ioc);

//     s.set_error_handler([](MQTT_NS::error_code ec)
//         {
//             std::cout << "error: " << ec.message() << std::endl;
//         });

//     std::set<con_sp_t> connections;
//     mi_sub_con subs;

//     s.set_accept_handler([&connections, &subs](con_sp_t spep)
//         {
//             auto& ep = *spep;
//             std::weak_ptr<con_t> wp(spep);

//             using packet_id_t = typename std::remove_reference_t<decltype(ep)>::packet_id_t;
//             std::cout << "accept" << std::endl;

//             // Pass spep to keep lifetime.
//             // It makes sure wp.lock() never return nullptr in the handlers below
//             // including close_handler and error_handler.
//             ep.start_session(std::move(spep));

//             // set connection (lower than MQTT) level handlers
//             ep.set_close_handler([&connections, &subs, wp]()
//                 {
//                     std::cout << "[server] closed." << std::endl;
//                     auto sp = wp.lock();
//                     BOOST_ASSERT(sp);
//                     close_proc(connections, subs, sp);
//                 });
//             ep.set_error_handler([&connections, &subs, wp](MQTT_NS::error_code ec)
//                 {
//                     std::cout << "[server] error: " << ec.message() << std::endl;
//                     auto sp = wp.lock();
//                     BOOST_ASSERT(sp);
//                     close_proc(connections, subs, sp);
//                 });

//             // set MQTT level handlers
//             ep.set_connect_handler([&connections, wp](MQTT_NS::buffer client_id,
//                 MQTT_NS::optional<MQTT_NS::buffer> username,
//                 MQTT_NS::optional<MQTT_NS::buffer> password, MQTT_NS::optional<MQTT_NS::will>,
//                 bool clean_session, std::uint16_t keep_alive)
//                 {
//                     using namespace MQTT_NS::literals;
//                     std::cout << "[server] client_id    : " << client_id << std::endl;
//                     std::cout << "[server] username     : "
//                               << (username ? username.value() : "none"_mb) << std::endl;
//                     std::cout << "[server] password     : "
//                               << (password ? password.value() : "none"_mb) << std::endl;
//                     std::cout << "[server] clean_session: " << std::boolalpha << clean_session
//                               << std::endl;
//                     std::cout << "[server] keep_alive   : " << keep_alive << std::endl;
//                     auto sp = wp.lock();
//                     BOOST_ASSERT(sp);
//                     connections.insert(sp);
//                     sp->connack(false, MQTT_NS::connect_return_code::accepted);
//                     return true;
//                 });
//             ep.set_disconnect_handler([&connections, &subs, wp]()
//                 {
//                     std::cout << "[server] disconnect received." << std::endl;
//                     auto sp = wp.lock();
//                     BOOST_ASSERT(sp);
//                     close_proc(connections, subs, sp);
//                 });
//             ep.set_puback_handler([](packet_id_t packet_id)
//                 {
//                     std::cout << "[server] puback received. packet_id: " << packet_id << std::endl;
//                     return true;
//                 });
//             ep.set_pubrec_handler([](packet_id_t packet_id)
//                 {
//                     std::cout << "[server] pubrec received. packet_id: " << packet_id << std::endl;
//                     return true;
//                 });
//             ep.set_pubrel_handler([](packet_id_t packet_id)
//                 {
//                     std::cout << "[server] pubrel received. packet_id: " << packet_id << std::endl;
//                     return true;
//                 });
//             ep.set_pubcomp_handler([](packet_id_t packet_id)
//                 {
//                     std::cout << "[server] pubcomp received. packet_id: " << packet_id << std::endl;
//                     return true;
//                 });
//             ep.set_publish_handler(
//                 [&subs](MQTT_NS::optional<packet_id_t> packet_id, MQTT_NS::publish_options pubopts,
//                     MQTT_NS::buffer topic_name, MQTT_NS::buffer contents)
//                 {
//                     std::cout << "[server] publish received."
//                               << " dup: " << pubopts.get_dup() << " qos: " << pubopts.get_qos()
//                               << " retain: " << pubopts.get_retain() << std::endl;
//                     if (packet_id)
//                         std::cout << "[server] packet_id: " << *packet_id << std::endl;
//                     std::cout << "[server] topic_name: " << topic_name << std::endl;
//                     std::cout << "[server] contents: " << contents << std::endl;
//                     auto const& idx = subs.get<tag_topic>();
//                     auto r = idx.equal_range(topic_name);
//                     for (; r.first != r.second; ++r.first)
//                     {
//                         r.first->con->publish(
//                             topic_name, contents, std::min(r.first->qos_value, pubopts.get_qos()));
//                     }
//                     return true;
//                 });
//             ep.set_subscribe_handler(
//                 [&subs, wp](packet_id_t packet_id, std::vector<MQTT_NS::subscribe_entry> entries)
//                 {
//                     std::cout << "[server] subscribe received. packet_id: " << packet_id
//                               << std::endl;
//                     std::vector<MQTT_NS::suback_return_code> res;
//                     res.reserve(entries.size());
//                     auto sp = wp.lock();
//                     BOOST_ASSERT(sp);
//                     for (auto const& e : entries)
//                     {
//                         std::cout << "[server] topic_filter: " << e.topic_filter
//                                   << " qos: " << e.subopts.get_qos() << std::endl;
//                         res.emplace_back(MQTT_NS::qos_to_suback_return_code(e.subopts.get_qos()));
//                         subs.emplace(std::move(e.topic_filter), sp, e.subopts.get_qos());
//                     }
//                     sp->suback(packet_id, res);
//                     return true;
//                 });
//             ep.set_unsubscribe_handler(
//                 [&subs, wp](packet_id_t packet_id, std::vector<MQTT_NS::unsubscribe_entry> entries)
//                 {
//                     std::cout << "[server] unsubscribe received. packet_id: " << packet_id
//                               << std::endl;
//                     auto sp = wp.lock();
//                     for (auto const& e : entries)
//                     {
//                         auto it = subs.find(std::make_tuple(sp, e.topic_filter));
//                         if (it != subs.end())
//                         {
//                             subs.erase(it);
//                         }
//                     }
//                     BOOST_ASSERT(sp);
//                     sp->unsuback(packet_id);
//                     return true;
//                 });
//         });
//     // commented for the purpose of the package test, in the self-check version please uncomment
//     // s.listen();
//     // ioc.run();
// }


#include <mqtt_client_cpp.hpp>

int main() {
    MQTT_NS::setup_log();

    boost::asio::io_context ioc;

    auto c = MQTT_NS::make_async_client(ioc, "localhost", "40000");

    c->set_client_id("test_package");
    c->set_clean_session(true);

    return 0;
}

//
// Created by Leonid  on 2019-03-25.
//

#include "FullAsyncTest.hpp"

#include "app/AsyncController.hpp"
#include "app/AsyncWebSocketListener.hpp"

#include "oatpp-websocket/Connector.hpp"
#include "oatpp-websocket/AsyncConnectionHandler.hpp"

#include "oatpp/web/server/AsyncHttpConnectionHandler.hpp"

#include "oatpp/network/server/SimpleTCPConnectionProvider.hpp"
#include "oatpp/network/client/SimpleTCPConnectionProvider.hpp"

#include "oatpp/network/virtual_/client/ConnectionProvider.hpp"
#include "oatpp/network/virtual_/server/ConnectionProvider.hpp"
#include "oatpp/network/virtual_/Interface.hpp"

#include "oatpp-test/web/ClientServerTestRunner.hpp"

#include "oatpp/core/macro/component.hpp"

namespace oatpp { namespace test { namespace websocket {

namespace {

//#define OATPP_TEST_USE_PORT 8000

class TestComponent {
public:

  OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::async::Executor>, httpServerExecutor)("http-server-exec", [] {
    return std::make_shared<oatpp::async::Executor>(4, 2);
  }());

  OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::async::Executor>, wsServerExecutor)("ws-server-exec", [] {
    return std::make_shared<oatpp::async::Executor>(4, 2);
  }());

  OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::async::Executor>, wsClientExecutor)("ws-client-exec", [] {
    return std::make_shared<oatpp::async::Executor>(4, 2);
  }());

  OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::network::virtual_::Interface>, virtualInterface)([] {
    return oatpp::network::virtual_::Interface::obtainShared("virtualhost");
  }());

  OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::network::ServerConnectionProvider>, serverConnectionProvider)([] {
#ifdef OATPP_TEST_USE_PORT
    return oatpp::network::server::SimpleTCPConnectionProvider::createShared(OATPP_TEST_USE_PORT);
#else
    OATPP_COMPONENT(std::shared_ptr<oatpp::network::virtual_::Interface>, interface);
    return oatpp::network::virtual_::server::ConnectionProvider::createShared(interface);
#endif
  }());

  /**
   *  Create Router component
   */
  OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::web::server::HttpRouter>, httpRouter)([] {
    return oatpp::web::server::HttpRouter::createShared();
  }());

  /**
   *  Create ConnectionHandler component which uses Router component to route requests
   */
  OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::network::server::ConnectionHandler>, serverConnectionHandler)([] {
    OATPP_COMPONENT(std::shared_ptr<oatpp::web::server::HttpRouter>, router); // get Router component
    OATPP_COMPONENT(std::shared_ptr<oatpp::async::Executor>, executor, "http-server-exec");
    return oatpp::web::server::AsyncHttpConnectionHandler::createShared(router, executor);
  }());

  /**
   *  Create ObjectMapper component to serialize/deserialize DTOs in Contoller's API
   */
  OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::data::mapping::ObjectMapper>, apiObjectMapper)([] {
    auto serializerConfig = oatpp::parser::json::mapping::Serializer::Config::createShared();
    auto deserializerConfig = oatpp::parser::json::mapping::Deserializer::Config::createShared();
    deserializerConfig->allowUnknownFields = false;
    auto objectMapper = oatpp::parser::json::mapping::ObjectMapper::createShared(serializerConfig, deserializerConfig);
    return objectMapper;
  }());

  /**
   *  Create websocket connection handler
   */
  OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::websocket::AsyncConnectionHandler>, websocketConnectionHandler)([] {
    OATPP_COMPONENT(std::shared_ptr<oatpp::async::Executor>, executor, "ws-server-exec");
    auto connectionHandler = oatpp::websocket::AsyncConnectionHandler::createShared(executor);
    connectionHandler->setSocketInstanceListener(std::make_shared<app::AsyncWebSocketInstanceListener>());
    return connectionHandler;
  }());

  OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::network::ClientConnectionProvider>, clientConnectionProvider)([this] {
#ifdef OATPP_TEST_USE_PORT
    return oatpp::network::client::SimpleTCPConnectionProvider::createShared("127.0.0.1", OATPP_TEST_USE_PORT);
#else
    OATPP_COMPONENT(std::shared_ptr<oatpp::network::virtual_::Interface>, interface);
    return oatpp::network::virtual_::client::ConnectionProvider::createShared(interface);
#endif
  }());

  OATPP_CREATE_COMPONENT(std::shared_ptr<oatpp::websocket::Connector>, connector)([] {
    OATPP_COMPONENT(std::shared_ptr<oatpp::network::ClientConnectionProvider>, clientConnectionProvider);
    return oatpp::websocket::Connector::createShared(clientConnectionProvider);
  }());

};

class ClientSocketListener : public oatpp::websocket::AsyncWebSocket::Listener{
private:
  v_int64 m_lastTick = 0;
  v_int32 m_messageCounter = 0;
  bool m_printLog;
  oatpp::data::stream::ChunkedBuffer m_messageBuffer;
public:

  ClientSocketListener(bool printLog)
    : m_printLog(printLog)
  {}

  CoroutineStarter onPing(const std::shared_ptr<AsyncWebSocket>& socket, const oatpp::String& message) override {
    return socket->sendPongAsync(message);
  }

  CoroutineStarter onPong(const std::shared_ptr<AsyncWebSocket>& socket, const oatpp::String& message) override {
    return nullptr;
  }

  CoroutineStarter onClose(const std::shared_ptr<AsyncWebSocket>& socket, v_uint16 code, const oatpp::String& message) override {
    return nullptr;
  }

  CoroutineStarter readMessage(const std::shared_ptr<AsyncWebSocket>& socket, v_uint8 opcode, p_char8 data, oatpp::v_io_size size) override {
    if(size == 0) {
      m_messageCounter ++;
      auto wholeMessage = m_messageBuffer.toString();
      m_messageBuffer.clear();
      if(m_printLog) {
        auto tick = oatpp::base::Environment::getMicroTickCount();
        OATPP_LOGD("client", "sid=%d, received %s, latency=%d, messageCount=%d", socket.get(), wholeMessage->c_str(), tick - m_lastTick, m_messageCounter);
        m_lastTick = tick;
      }
    } else if(size > 0) {
      m_messageBuffer.writeSimple(data, size);
    }
    return nullptr;
  }

};

class ClientSenderCoroutine : public oatpp::async::Coroutine<ClientSenderCoroutine> {
private:
  std::shared_ptr<oatpp::websocket::AsyncWebSocket> m_socket;
  v_int32 m_messagesPerClient;
  v_int32 m_messagesCount;
public:

  ClientSenderCoroutine(const std::shared_ptr<oatpp::websocket::AsyncWebSocket>& socket, v_int32 messagesPerClient)
    : m_socket(socket)
    , m_messagesPerClient(messagesPerClient)
    , m_messagesCount(0)
  {}

  Action act() override {
    if(m_messagesCount < m_messagesPerClient) {
      m_messagesCount ++;
      return m_socket->sendOneFrameTextAsync("hello!").next(yieldTo(&ClientSenderCoroutine::act));
    }
    return m_socket->sendCloseAsync().next(finish());
  }

};

class ClientCoroutine : public oatpp::async::Coroutine<ClientCoroutine> {
public:
  static std::atomic<v_int32> CONNECTIONS;
  static std::atomic<v_int32> FINISHED_COUNTER;
private:
  OATPP_COMPONENT(std::shared_ptr<oatpp::async::Executor>, executor, "ws-client-exec");
  OATPP_COMPONENT(std::shared_ptr<oatpp::websocket::Connector>, connector);
  std::shared_ptr<oatpp::websocket::AsyncWebSocket> socket;
  bool m_printLog;
  v_int32 m_messagesPerClient;
public:

  ClientCoroutine(bool printLog, v_int32 messagesPerClient)
    : m_printLog(printLog)
    , m_messagesPerClient(messagesPerClient)
  {}

  Action act() override {
    return connector->connectAsync("ws").callbackTo(&ClientCoroutine::onConnected);
  }

  Action onConnected(const std::shared_ptr<oatpp::data::stream::IOStream>& connection) {
    ++ CONNECTIONS;
    socket = oatpp::websocket::AsyncWebSocket::createShared(connection, true);
    socket->setListener(std::make_shared<ClientSocketListener>(m_printLog));
    executor->execute<ClientSenderCoroutine>(socket, m_messagesPerClient);
    return socket->listenAsync().next(yieldTo(&ClientCoroutine::onFinishListen));
  }

  Action onFinishListen() {
    ++ FINISHED_COUNTER;
    OATPP_LOGD("Client", "Finished count=%d", FINISHED_COUNTER.load());
    return finish();
  }

  Action handleError(Error* error) override {
    if(error) {
      OATPP_LOGD("Client", "Error. !!!---!!!---!!!---!!!---!!!---!!!---!!!---!!!---!!!---!!!---!!!---!!!---!!! %s", error->what());
    }
    return error;
  }

};

std::atomic<v_int32> ClientCoroutine::CONNECTIONS(0);
std::atomic<v_int32> ClientCoroutine::FINISHED_COUNTER(0);

}

void FullAsyncTest::onRun() {


  TestComponent component;

  OATPP_COMPONENT(std::shared_ptr<oatpp::async::Executor>, httpServerExecutor, "http-server-exec");
  OATPP_COMPONENT(std::shared_ptr<oatpp::async::Executor>, wsServerExecutor, "ws-server-exec");
  OATPP_COMPONENT(std::shared_ptr<oatpp::async::Executor>, wsClientExecutor, "ws-client-exec");

  oatpp::test::web::ClientServerTestRunner runner;

  runner.addController(app::AsyncController::createShared());

  runner.run([] {

    OATPP_COMPONENT(std::shared_ptr<oatpp::async::Executor>, executor, "ws-client-exec");

    /////////////////////////////////////////////////////////////////////////////////////
    // Create clients

    v_int32 clients = 1000;
    v_int32 messagesPerClient = 100;

    for(v_int32 i = 0; i < clients; i ++) {
      executor->execute<ClientCoroutine>(false, messagesPerClient);
    }

    clients ++;
    executor->execute<ClientCoroutine>(true, messagesPerClient);

    /////////////////////////////////////////////////////////////////////////////////////

    OATPP_LOGD("AAA", "waiting...");

    while(true) {
      std::this_thread::sleep_for(std::chrono::milliseconds(200));
      if(ClientCoroutine::FINISHED_COUNTER == clients) {
        break;
      }
    }

  }, std::chrono::minutes(10));

  httpServerExecutor->waitTasksFinished();
  wsServerExecutor->waitTasksFinished();
  wsClientExecutor->waitTasksFinished();

  httpServerExecutor->stop();
  wsServerExecutor->stop();
  wsClientExecutor->stop();

  httpServerExecutor->join();
  wsServerExecutor->join();
  wsClientExecutor->join();

}

}}}

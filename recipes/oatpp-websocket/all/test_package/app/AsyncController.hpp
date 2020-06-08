//
//  AsyncController.hpp
//  web-starter-project
//
//  Created by Leonid on 2/12/18.
//  Copyright © 2018 oatpp. All rights reserved.
//

#ifndef oatpp_test_websocket_app_websoAsyncController_hpp
#define oatpp_test_websocket_app_websoAsyncController_hpp

#include "oatpp-websocket/Handshaker.hpp"
#include "oatpp-websocket/AsyncConnectionHandler.hpp"

#include "oatpp/web/server/api/ApiController.hpp"
#include "oatpp/parser/json/mapping/ObjectMapper.hpp"
#include "oatpp/core/macro/codegen.hpp"
#include "oatpp/core/macro/component.hpp"

namespace oatpp { namespace test {namespace websocket { namespace app {

class AsyncController : public oatpp::web::server::api::ApiController {
private:
  typedef AsyncController __ControllerType;
private:
  OATPP_COMPONENT(std::shared_ptr<oatpp::websocket::AsyncConnectionHandler>, websocketConnectionHandler);
protected:
  AsyncController(const std::shared_ptr<ObjectMapper>& objectMapper)
    : oatpp::web::server::api::ApiController(objectMapper)
  {}
public:

  static std::shared_ptr<AsyncController> createShared(OATPP_COMPONENT(std::shared_ptr<ObjectMapper>, objectMapper)){
    return std::shared_ptr<AsyncController>(new AsyncController(objectMapper));
  }

  /**
   *  Begin ENDPOINTs generation ('ApiController' codegen)
   */
#include OATPP_CODEGEN_BEGIN(ApiController)

  ENDPOINT_ASYNC("GET", "ws", WS) {

    static std::atomic<v_int32>& getAtom() {
      static std::atomic<v_int32> atom(0);
      return atom;
    }

    ENDPOINT_ASYNC_INIT(WS)

    Action act() override {
      getAtom() ++;
      auto params = std::make_shared<oatpp::network::server::ConnectionHandler::ParameterMap>();
      (*params)["p1"] = "v1";
      auto response = oatpp::websocket::Handshaker::serversideHandshake(request->getHeaders(), controller->websocketConnectionHandler);
      response->setConnectionUpgradeParameters(params);
      return _return(response);
    }

  };

  ENDPOINT_ASYNC("GET", "*", ALL) {

  ENDPOINT_ASYNC_INIT(ALL)

    Action act() override {
      oatpp::String path = request->getPathTail();
      if(path) {
        OATPP_LOGD("Controller", "path='%s'", path->c_str());
      } else {
        OATPP_LOGD("Controller", "path='%s'", "nullptr");
      }
      return _return(controller->createResponse(Status::CODE_400, "wtf"));
    }

  };

  /**
   *  Finish ENDPOINTs generation ('ApiController' codegen)
   */
#include OATPP_CODEGEN_END(ApiController)

};

}}}}

#endif /* oatpp_test_websocket_app_websoAsyncController_hpp */

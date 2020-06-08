//
//  Controller.hpp
//  web-starter-project
//
//  Created by Leonid on 2/12/18.
//  Copyright © 2018 oatpp. All rights reserved.
//

#ifndef oatpp_test_websocket_app_Controller_hpp
#define oatpp_test_websocket_app_Controller_hpp


#include "oatpp-websocket/Handshaker.hpp"
#include "oatpp-websocket/ConnectionHandler.hpp"

#include "oatpp/web/server/api/ApiController.hpp"
#include "oatpp/parser/json/mapping/ObjectMapper.hpp"
#include "oatpp/core/macro/codegen.hpp"
#include "oatpp/core/macro/component.hpp"


namespace oatpp { namespace test { namespace websocket { namespace app {

class Controller : public oatpp::web::server::api::ApiController {
protected:
  Controller(const std::shared_ptr<ObjectMapper> &objectMapper)
    : oatpp::web::server::api::ApiController(objectMapper)
  {}

private:
  OATPP_COMPONENT(std::shared_ptr<oatpp::websocket::ConnectionHandler>, websocketConnectionHandler);
public:

  /**
   *  Inject @objectMapper component here as default parameter
   *  Do not return bare Controllable* object! use shared_ptr!
   */
  static std::shared_ptr<Controller> createShared(OATPP_COMPONENT(std::shared_ptr<ObjectMapper>, objectMapper)) {
    return std::shared_ptr<Controller>(new Controller(objectMapper));
  }

  /**
   *  Begin ENDPOINTs generation ('ApiController' codegen)
   */
#include OATPP_CODEGEN_BEGIN(ApiController)

  ENDPOINT("GET", "/ws", websocketConnect, REQUEST(std::shared_ptr<IncomingRequest>, request)) {
    return oatpp::websocket::Handshaker::serversideHandshake(request->getHeaders(), websocketConnectionHandler);
  }

  /**
   *  Finish ENDPOINTs generation ('ApiController' codegen)
   */
#include OATPP_CODEGEN_END(ApiController)

};

}}}}

#endif /* oatpp_test_websocket_app_Controller_hpp */

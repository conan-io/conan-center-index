#include "Application/QuickFAST.h"
#include "Codecs/MessageConsumer.h"
#include "Codecs/GenericMessageBuilder.h"

using namespace QuickFAST;

class MessageInterpreter : public Codecs::MessageConsumer
{
public:
  MessageInterpreter(std::ostream & out, bool silent = false){ };
  virtual ~MessageInterpreter(){ };
  void setLogLevel(Common::Logger::LogLevel level){ };
  virtual bool consumeMessage(Messages::Message & message){return true;}
  virtual bool wantLog(unsigned short level){return true;}
  virtual bool logMessage(unsigned short level, const std::string & logMessage){return true;}
  virtual bool reportDecodingError(const std::string & errorMessage){return true;}
  virtual bool reportCommunicationError(const std::string & errorMessage){return true;}
  virtual void decodingStarted(){ }
  virtual void decodingStopped(){ }
};

int main(int argc, char* argv[])
{
  Application::DecoderConfiguration configuration_;
  Application::DecoderConnection connection_;

  try
  {
    MessageInterpreter handler(std::cout);
    Codecs::GenericMessageBuilder builder(handler);
    connection_.configure(builder, configuration_);
    connection_.run();
  }
  catch (std::exception &)
  {
  }
}

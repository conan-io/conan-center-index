#include "behaviortree_cpp_v3/bt_factory.h"

using namespace BT;

struct Position2D { double x,y; };

namespace BT{
    template <> inline Position2D convertFromString(StringView str) {
        printf("Converting string: \"%s\"\n", str.data() );

        // real numbers separated by semicolons
        auto parts = splitString(str, ';');
        if (parts.size() != 2)
        {
            throw RuntimeError("invalid input)");
        }
        else{
            Position2D output;
            output.x     = convertFromString<double>(parts[0]);
            output.y     = convertFromString<double>(parts[1]);
            return output;
        }
    }
}

class CalculateGoal: public SyncActionNode{
public:
    CalculateGoal(const std::string& name, const NodeConfiguration& config):
        SyncActionNode(name,config) {}

    NodeStatus tick() override{
        Position2D mygoal = {1.1, 2.3};
        setOutput("goal", mygoal);
        return NodeStatus::SUCCESS;
    }
    static PortsList providedPorts(){
        return { OutputPort<Position2D>("goal") };
    }
};


class PrintTarget: public SyncActionNode {
public:
    PrintTarget(const std::string& name, const NodeConfiguration& config):
        SyncActionNode(name,config) {}

    NodeStatus tick() override {
        auto res = getInput<Position2D>("target");
        if( !res ){
            throw RuntimeError("error reading port [target]:", res.error() );
        }
        Position2D goal = res.value();
        printf("Target positions: [ %.1f, %.1f ]\n", goal.x, goal.y );
        return NodeStatus::SUCCESS;
    }

    static PortsList providedPorts() {
        // Optionally, a port can have a human readable description
        const char*  description = "Simply print the target on console...";
        return { InputPort<Position2D>("target", description) };
    }
};

static const char* xml_text = R"(
 <root main_tree_to_execute = "MainTree" >
     <BehaviorTree ID="MainTree">
        <Sequence name="root">
            <CalculateGoal   goal="{GoalPosition}" />
            <PrintTarget     target="{GoalPosition}" />
            <SetBlackboard   output_key="OtherGoal" value="-1;3" />
            <PrintTarget     target="{OtherGoal}" />
        </Sequence>
     </BehaviorTree>
 </root>
 )";


int main() {
    using namespace BT;

    BehaviorTreeFactory factory;
    factory.registerNodeType<CalculateGoal>("CalculateGoal");
    factory.registerNodeType<PrintTarget>("PrintTarget");

    auto tree = factory.createTreeFromText(xml_text);
    tree.tickRoot();
    return 0;
}

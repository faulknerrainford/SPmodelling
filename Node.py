from abc import ABC, abstractmethod
import specification


class Node(ABC):

    def __init__(self, name, capacity=None, duration=None, queue=None, nuid="name"):
        self.name = name
        self.capacity = capacity
        self.duration = duration
        self.queue = queue
        self.nuid = nuid

    @abstractmethod
    def agentsready(self, tx, intf, agentclass):
        agents = intf.getnodeagents(tx, self.name, "name")
        clock = intf.gettime(tx)
        if self.queue or self.queue == {}:
            queueagents = [key for time in self.queue.keys() for key in self.queue[time].keys()]
            newagents = [ag for ag in agents if ag["id"] not in queueagents]
            # run prediction on each unqueued agent
            for ag in newagents:
                self.agentprediction(tx, ag, intf)
        for ag in agents:
            if self.queue:
                if clock in self.queue.keys():
                    if ag["id"] in self.queue[clock].keys():
                        agper = self.agentperception(tx, ag, intf, self.queue[clock][ag["id"]][0],
                                                     self.queue[clock][ag["id"]])
                        specification.Agents.Agent(ag["id"]).move(tx, intf, agper)
            else:
                agper = self.agentperception(tx, ag, intf)
                specification.Agents.Agent(ag["id"]).move(tx, intf, agper)
        if self.queue and clock in self.queue.keys():
            del self.queue[clock]

    @abstractmethod
    def agentperception(self, tx, agent, intf, dest=None, waittime=None):
        if dest:
            view = dest
        else:
            view = intf.perception(tx, agent["id"])[1:]
        if type(view) == list:
            for edge in view:
                if "cap" in edge.end_node.keys():
                    if edge.end_node["cap"] <= edge.end_node["load"]:
                        view.remove(edge)
        return view

    @abstractmethod
    def agentprediction(self, tx, agent, intf):
        view = intf.perception(tx, agent["id"])
        return view

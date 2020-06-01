from abc import ABC, abstractmethod


class MotiveAgent(ABC):

    @abstractmethod
    def __init__(self, agentid, params=None, nuid="id"):
        self.id = agentid
        self.view = None
        self.params = params
        self.choice = None
        self.nuid = nuid

    @abstractmethod
    def generator(self, tx, intf, params):
        pass

    @abstractmethod
    def perception(self, tx, intf, perc):
        self.view = perc

    @abstractmethod
    def choose(self, tx, intf, perc):
        self.perception(tx, intf, perc)

    @abstractmethod
    def learn(self, tx, intf, choice):
        return [choice, tx, intf]
        # uses interface to update network based on choice

    @abstractmethod
    def payment(self, tx, intf):
        return None

    def move(self, tx, intf, perc):
        self.choice = self.choose(tx, intf, perc)
        if self.choice:
            # Move node based on choice using tx
            tx.run("MATCH (n:Agent)-[r:LOCATED]->() "
                   "WHERE n.id = {id} "
                   "DELETE r", id=self.id)
            new = self.choice.end_node[self.nuid]
            tx.run("MATCH (n:Agent), (a:Node) "
                   "WHERE n.id={id} AND a." + self.nuid + "={new} "
                                                          "CREATE (n)-[r:LOCATED]->(a)", id=self.id, new=new)
            self.payment(tx, intf)
            self.learn(tx, intf, self.choice)
            return new


class CommunicativeAgent(ABC):

    @abstractmethod
    def __init__(self, agentid, params=None, nuid="id"):
        # TODO: write social agent functionality and handler like flow
        self.id = agentid
        self.view = None
        self.params = params
        self.nuid = nuid

    def socialise(self, tx, intf):
        self.perception(tx, intf)
        self.update(tx, intf)
        self.talk(tx, intf)
        self.listen(tx, intf)
        self.react(tx, intf)

    @abstractmethod
    def perception(self, tx, intf):
        return None

    @abstractmethod
    def update(self, tx, intf):
        return None

    @abstractmethod
    def talk(self, tx, intf):
        return None

    @abstractmethod
    def listen(self, tx, intf):
        return None

    @abstractmethod
    def react(self, tx, intf):
        return None

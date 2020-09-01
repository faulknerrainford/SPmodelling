from abc import ABC, abstractmethod
import SPmodelling.Interface as intf


class MobileAgent(ABC):
    """
    Class for simulating agents which move between locations in a network
    """

    @abstractmethod
    def __init__(self, agentid, params=None, nuid="id"):
        self.id = agentid
        self.view = None
        self.params = params
        self.choice = None
        self.nuid = nuid

    @abstractmethod
    def generator(self, tx, params):
        """
        Subclass should implement code to generate a specialised agent using the interface to insert the new agent into
        the database, the base function does nothing.

        :param tx: write transaction for a neo4j database
        :param params: paramaters are given as a list to be used by the subclass.

        :return: None
        """
        pass

    @abstractmethod
    def perception(self, tx, perc):
        """
        Subclass must implement this class to perform the Agents filtering to remove options the agent considers not
        possible for it. The agent will then reset the agent view to the filtered version.

        :param tx: Read or write transaction for neo4j database
        :param perc: Perception passed to agent from local node

        :return: None
        """
        self.view = perc

    @abstractmethod
    def choose(self, tx, perc):
        """
        Subclass must implement this function to make a choice between all possible options after node and agent filtering
        This class calls the agent perception function so super call must be made at start of funciton.

        :param tx: read or write transaction for neo4j
        :param perc: passed by node to give agent current local options

        :return: None
        """
        self.perception(tx, perc)

    @abstractmethod
    def learn(self, tx, choice):
        """
        Subclass must implement this function to make changes to the agent and node after moving.

        :param tx: write transaction for neo4j
        :param choice: Relationship object passed from the interface which the agent moved along

        :return: [choice, tx] Relationship object and neo4j write transaction
        """
        return [choice, tx]
        # uses interface to update network based on choice

    @abstractmethod
    def payment(self, tx):
        """
        Subclass must implement this function to make changes to the agent, edges and nodes before/during movement.
        Including paying any cost of the movement.

        :param tx: write transaction for neo4j database

        :return: None
        """
        return None

    def move(self, tx, perc):
        """
        This function performs action of the agent. It calls the choice function and checks for a return and a payment
        has been made (if the payment fails the agent doesn't move). The agent is moved and then learns. There is no
        reason for subclasses to implement this function.

        :param tx: neo4j write transaction
        :param perc: perception of local surroundings passed to agent by it's local node

        :return: If agent moves return the new local node
        """
        self.choice = self.choose(tx, perc)
        if self.choice:
            if self.payment(tx):
                # Move node based on choice using tx
                tx.run("MATCH (n:Agent)-[r:LOCATED]->() "
                       "WHERE n.id = {id} "
                       "DELETE r", id=self.id)
                new = self.choice.end_node["name"]
                tx.run("MATCH (n:Agent), (a:Node) "
                       "WHERE n.id={id} AND a.name='" + new + "' CREATE (n)-[r:LOCATED]->(a)", id=self.id, new=new)
                self.learn(tx, self.choice)
                return new


class CommunicativeAgent(ABC):
    """
    Agent Class for agents in social networks. These agents act as nodes as well as agents.
    """

    @abstractmethod
    def __init__(self, agentid, params=None, nuid="id"):
        self.id = agentid
        self.view = None
        self.params = params
        self.nuid = nuid

    def socialise(self, tx):
        """
        This function does not need to be implemented in the subclass. It calls the five functions that an agent
        performs as an action. The agent will: look, update, talk, listen and then react.

        :param tx: neo4j write transaction

        :return: None
        """
        if not self.look(tx):
            self.update(tx)
            self.talk(tx)
            self.listen(tx)
            self.react(tx)

    @abstractmethod
    def look(self, tx):
        """
        The subclass should implement this function to allow the agent to detect other entities in its social network.
        Can also be used to detect agents colocated with it in a physical network.

        :param tx: read or write transaction for a neo4j database

        :return: None
        """
        return None

    @abstractmethod
    def update(self, tx):
        """
        The subclass should implement this function to allow the agent to update it's own values based on it's local
        social network and colocated agents in physical networks.

        :param tx: write transaction for a neo4j database

        :return: None
        """
        return None

    @abstractmethod
    def talk(self, tx):
        """
        The subclass should implement this function to allow agents to form new social connections possibly through
        existing connections or co-location.

        :param tx: write transaction for a neo4j database

        :return: None
        """
        return None

    @abstractmethod
    def listen(self, tx):
        """
        The subclass should implement this function to allow agents to change their values or form new connections based
        on the situation after talking.

        :param tx: write transaction for a neo4j database

        :return: None
        """
        return None

    @abstractmethod
    def react(self, tx):
        """
        The subclass should implement this function. The agent has a final opportunity to adjust its values and manage
        its social network. This includes managing the number of social links.

        :param tx: write transaction for neo4j database

        :return: None
        """
        return None

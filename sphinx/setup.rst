====================
Install Requirements
====================

To run a model using SPmodelling you need to have:

+ Python 3.7+
+ Neo4j Server or Desktop
+ Python packages:
    + neobolt
    + neo4j
    + numpy
    + matplotlib
    + json
    + system
    + pandas

================
Run Requirements
================
+ An implementation of subclasses of modules you wish to use in your model
+ A specification built to the template given below:

.. code-block:: python

    # Import objects for standard intervenors with correct name
    from model.Monitor import ModelMonitor as Monitor
    from model.Population import ModelPopulation as Population
    from model.Cluster import ModelCluster as Cluster
    from model.Services import ModelServices as Services
    from model.Reset import ModelReset as Reset
    # Import other objects needed including nodes, agents and other internevors
    import model.Agent as mA
    import model.Node as mN
    import model.ExtraIntervenor as mEI

    # Set name tag for this model specification, this will be attached to all outputs
    specname = <Specification Name>
    nodes = <List of initialised node objects in system>
    # Agent class keys should match the agents label in the database
    AgentClasses = <Dictionary of name object pairs for different classes of agents in system>
    # Node and Service class keys should match the node names assigned at initialisation above
    NodeClasses = <Dictionary of name object pairs for different classes of nodes in system>
    ServiceClasses = <Dictionary of name object pairs for different classes of services in system>

    database_uri = "bolt://localhost:7687" # or server address for non-local servers

    # Usernames and passwords to be used by intervenors to access database
    # Intervenors must have write access to database, can use one or multiple users for intervenors
    Flow_auth = Inter_auth = Balancer_auth = Population_auth = (<Intervenor Username>, <Intervenor Password>)
    Structure_auth = Reset_auth = (<Intervenor Username>, <Intervenor Password>)
    # Viewers only need read access to database
    Monitor_auth = (<Viewer Username>, <Viewer Password>)

========
Example
========
A full specification for an existing model, called FallModel.

.. code-block:: python
    # General specification
    from FallModel import Fall_nodes as Nodes
    from FallModel import Fall_Monitor as Monitor
    from FallModel import Fall_Balancer as Balancer
    from FallModel import Patient as Agent
    from FallModel import Fall_Population as Population
    from FallModel import Fall_reset as Reset
    import sys

    specname = "socialV1Test"
    nodes = [Nodes.CareNode(), Nodes.HosNode(), Nodes.SocialNode(), Nodes.GPNode(), Nodes.InterventionNode(),
             Nodes.InterventionNode("InterventionOpen"), Nodes.HomeNode()]

    AgentClasses = None
    NodeClasses = {"Care":Nodes.CareNode, "Hos":Nodes.HosNode, "Social":Nodes.SocialNode, "GP":Nodes.GPNode,
                   "Intervention":Nodes.InterventionNode, "Home":Nodes.HomeNode}
    ServiceClasses = None

    database_uri = "bolt://localhost:7687"

    Flow_auth = ("Flow", "Flow")
    Balancer_auth = ("Balancer", "bal")
    Population_auth = ("Population", "pop")
    Structure_auth = ("Structure", "struct")
    Reset_auth = ("dancer", "dancer")
    Monitor_auth = ("monitor", "monitor")
    # FallModel specification
    Carers = None
    Intervention_cap = 2
    Open_Intervention = True
    Open_Intervention_cap = 2
    Open_Intervention_Limits = ["Healthy", "At risk"]

    savedirectory = "testfile"

There are several sections to the specification the first calls in all the modules and classes from the FallModel
package that will be used by SPmodelling. We then declare the classes to be used and the database specifics. The last
section is the specification relating to the FallModel specifically. These are added while declaring the FallModel and
give a fixed list of parameters associated with a specname to track the parameters used in any run of the model. In this
case we also add the savedirectory to allow us to dictate the folder the data from this model will be saved to.
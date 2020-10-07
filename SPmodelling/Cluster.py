import SPmodelling.Intervenor
import SPmodelling.Interface as intf
from neo4j import GraphDatabase


class Cluster(SPmodelling.Intervenor.Intervenor):

    def __init__(self, tx):
        super(Cluster, self).__init__()
        self.newgroupings = None
        # Get clusters
        cluster_tuples = intf.louvain(tx, "Agent", "SOCIAL").values()
        # Set up cluster nodes
        clusters = [[ag[1]]+ag[2] for ag in cluster_tuples]
        clusters = set([cluster for ag in clusters for cluster in ag])
        for cluster in clusters:
            intf.addnode(tx, cluster, 'Cluster', uid='id')
        for ag in cluster_tuples:
            # Set seed cluster for each node (currently final cluster)
            intf.updatenode(tx, ag[0], 'seedCluster', ag[1], 'id', 'Agent')
            for clust in set([ag[1]]+ag[2]):
                # connect agents to cluster nodes for current and intermediate clusters
                intf.createedge(tx, [clust, "Cluster", 'id'], [ag[0], "Agent", 'id'], edge_label="GROUPED")

    def check(self, tx):
        super(Cluster, self).check(tx)
        self.newgroupings = []
        # look for changes in clusters and make a change list
        currentclusters = intf.louvain(tx, "Agent", "SOCIAL", "seedCluster").values()
        # for agent get cluster tuple [id, list of all clusters]
        for ag in currentclusters:
            # make list of any new changes to clusters
            historicclusters = intf.checkgroupings(tx, [ag[0], "Agent", "id"])
            for clust in set([ag[1]]+ag[2]):
                if clust not in historicclusters:
                    self.newgroupings.append([ag[0], clust])
        return self.newgroupings

    def apply_change(self, tx):
        super(Cluster, self).apply_change(tx)
        for update in self.newgroupings:
            # add link to new clusters
            intf.createedge(tx, [update[1], "Cluster", 'id'], [update[0], "Agent", 'id'], edge_label="GROUPED")


def update_cluster_strength(tx, agent, cluster, strength):
    # update cluster strength links
    intf.updateedge([agent, cluster], 'strength', strength)
    pass


def update_cluster_orientation(tx, attribute, threshold, ordering):
    # TODO: update seedCluster based on largest/smallest attribute value base on order ascending/descending

    # TODO: drop weak links below/above the threshold value based on order ascending/descending
    pass


def main(rl):
    """
    Implements clustering repeatedly until the clock in the database reaches the run length.

    :param rl: run length

    :return: None
    """
    import specification
    clock = 0
    while clock < rl:
        dri = GraphDatabase.driver(specification.database_uri, auth=specification.Balancer_auth,
                                   max_connection_lifetime=2000)
        with dri.session() as ses:
            clust = ses.write_transaction(Cluster)
            ses.write_transaction(clust.apply_change)
            tx = ses.begin_transaction()
            time = intf.gettime(tx)
            while clock == time:
                time = intf.gettime(tx)
            clock = time
        dri.close()
    print("Cluster closed")

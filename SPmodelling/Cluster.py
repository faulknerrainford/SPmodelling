import SPmodelling.Intervenor
import SPmodelling.Interface as intf
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, SessionExpired


class Cluster(SPmodelling.Intervenor.Intervenor):

    def __init__(self, dri, strength):
        super(Cluster, self).__init__("Cluster")
        self.new_groupings = None
        self.strength = strength
        self.current_clusters = None
        # Get clusters
        cluster_tuples = intf.louvain(dri, "Agent", "SOCIAL")
        # Set up cluster nodes
        clusters = [[ag[1]] + ag[2] for ag in cluster_tuples]
        clusters = set([cluster for ag in clusters for cluster in ag])
        for cluster in clusters:
            intf.add_node(dri, [cluster, 'Cluster', 'id'])
        for ag in cluster_tuples:
            # Set seed cluster for each node (currently final cluster)
            intf.update_node(dri, [ag[0], 'Agent', 'id'], 'seedCluster', ag[1])
            for clust in set([ag[1]] + ag[2]):
                # connect agents to cluster nodes for current and intermediate clusters
                intf.create_edge(dri, [clust, "Cluster", 'id'], [ag[0], "Agent", 'id'], edge_label="GROUPED",
                                 parameters=self.strength + ":0")

    def check(self, dri):
        super(Cluster, self).check(dri)
        self.new_groupings = []
        # look for changes in clusters and make a change list
        current_clusters = intf.louvain(dri, "Agent", "SOCIAL", "seedCluster")
        # for agent get cluster tuple [id, list of all clusters]
        for ag in current_clusters:
            # filter out agents which have been removed from system
            if ag[0] or ag[0] == 0:
                # make list of any new changes to clusters
                if intf.get_node(dri, [ag[0], "Agent", "id"]):
                    historic_clusters = intf.check_groupings(dri, [ag[0], "Agent", "id"])
                    if historic_clusters:
                        historic_clusters = [[cl, "Cluster", "id"] for cl in historic_clusters]
                    current_cl = [[cl, "Cluster", "id"] for cl in ag[2]]
                    for cluster in current_cl:
                        if not historic_clusters or cluster not in historic_clusters:
                            self.new_groupings.append([ag[0], cluster[0]])
        return self.new_groupings

    def apply_change(self, dri):
        super(Cluster, self).apply_change(dri)
        if self.new_groupings:
            self.current_clusters = intf.clusters_in_system(dri)
            for update in self.new_groupings:
                if update[1] not in self.current_clusters:
                    self.new_cluster(dri, update[1])
                    self.current_clusters.append(update[1])
                # add link to new clusters
                intf.create_edge(dri, [update[1], "Cluster", 'id'], [update[0], "Agent", 'id'], edge_label="GROUPED",
                                 parameters=self.strength + ":0")

    @staticmethod
    def new_cluster(dri, cluster_id):
        intf.add_node(dri, [cluster_id, 'Cluster', 'id'])


def update_cluster_strength(dri, agent, cluster, strength, attribute_name):
    # update cluster strength links
    intf.update_edge(dri, [agent, cluster], attribute_name, strength, "GROUPED")


def update_cluster_orientation(dri, ps, attribute, threshold, ordering):
    agents = [[i, "Agent", "id"] for i in range(ps)]
    for agent in agents:
        clusters = intf.check_groupings(dri, agent)
        if clusters:
            clusters = [[cluster[0], "Cluster", "id"] for cluster in clusters]
            clusters_attributes = [[cluster, intf.get_edge_value(dri, [agent, cluster], attribute, "GROUPED")] for cluster
                                   in clusters]
            for cluster in clusters_attributes:
                if cluster[1] < threshold and ordering == "ascending":
                    intf.delete_edge(dri, agent, [cluster[0], "Cluster", "id"], "GROUPED")
                elif cluster[1] > threshold and ordering == "descending":
                    intf.delete_edge(dri, agent, [cluster[0], "Cluster", "id"], "GROUPED")
        clusters = intf.check_groupings(dri, agent)
        if clusters:
            clusters = [[cluster[0], "Cluster", "id"] for cluster in clusters]
            clusters_attributes = [[cluster, intf.get_edge_value(dri, [agent, cluster], attribute, "GROUPED")] for
                                   cluster
                                   in clusters]
            c_a = [cluster[1] for cluster in clusters_attributes]
            seed_cluster = None
            if ordering == "ascending":
                seed_cluster = clusters_attributes[c_a.index(max(c_a))][0]
            elif ordering == "descending":
                seed_cluster = clusters_attributes[c_a.index(min(c_a))][0]
            if seed_cluster[0] > -1:
                intf.update_agent(dri, agent, "seedCluster", seed_cluster[0])
    pass


def main(rl):
    """
    Implements clustering repeatedly until the clock in the database reaches the run length.

    :param rl: run length

    :return: None
    """
    import specification
    clock = 0
    dri = GraphDatabase.driver(specification.database_uri, auth=specification.Flow_auth,
                               max_connection_lifetime=36000, encrypted=False)
    clust = specification.Cluster(dri)
    while clock < rl:
        clust.check(dri)
        clust.apply_change(dri)
        time = intf.get_time(dri)
        while time-clock < 4:
            time = intf.get_time(dri)
        clock = time
    dri.close()
    print("Cluster closed")

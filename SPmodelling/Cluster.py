import SPmodelling.Intervenor
import SPmodelling.Interface as intf
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, SessionExpired


class Cluster(SPmodelling.Intervenor.Intervenor):
    """
    Intervenor that forms and manages the clusters in the system. It uses the louvain algorithm and the structure of the
     social network for community detection and updates with seeded clusters for continuity.
    """

    def __init__(self, dri, strength):
        """
        When initialising clusters in the system we run an unseeded algorithm using the strength attribute given to work
         out the initial clustering on the social network

        :param dri: neo4j database driver
        :param strength: attribute of the social links in the social network to be used as the strength of the links for
                         clustering purposes.
        """
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

    def check(self, dri, params=None):
        """
        Check the clustering on the system and records any new cluster assignments

        :param dri: neo4j database driver
        :param params: Any additional parameters needed by cluster

        :return: List of new agent cluster pairings
        """
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

    def apply_change(self, dri, params=None):
        """
        Implement new clusters and new grouping links as identified in the check

        :param dri: neo4j database driver
        :param params: Any additional parameters needed by balancer

        :return: None
        """
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
        """
        Adds new cluster to system

        :param dri: neo4j database driver
        :param cluster_id: id for the new cluster to be created

        :return: None
        """
        intf.add_node(dri, [cluster_id, 'Cluster', 'id'])


def update_cluster_strength(dri, agent, cluster, strength, attribute_name):
    """
    Update cluster edge strength with the given strength on the attribute_name given

    :param dri: neo4j database driver
    :param agent: agent tuple of id, label, id type
    :param cluster: cluster tuple of id, label, id type
    :param strength: value of the strength of the new cluster link
    :param attribute_name: attribute name to assign cluster link strength to

    :return: None
    """
    # update cluster strength links
    intf.update_edge(dri, [agent, cluster], attribute_name, strength, "GROUPED")


def update_cluster_orientation(dri, attribute, threshold, ordering):
    """
    For each agent check for its strongest cluster link and assign that clusters as it's seed cluster for future
    clustering runs. Also check for cluster links whose strength does not reach threshold values and remove those
    cluster links.

    :param dri: neo4j database driver
    :param attribute: attribute name for strength of cluster links
    :param threshold: threshold values for cluster links to continue to exist
    :param ordering: whether threshold requires value to be over ("ascending") or under ("descending") the threshold
                     value as given
    :return: None
    """
    agents = [(i, "Agent", "id") for i in intf.get_agents(dri, "Agent")]
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

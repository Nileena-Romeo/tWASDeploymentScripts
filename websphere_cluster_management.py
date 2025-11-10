"""
WebSphere Cluster Management Script (Jython)
This script demonstrates how to manage WebSphere clusters using wsadmin
"""

# Import required modules
import sys
import os
import time

# Configuration parameters
cellName = "YourCellName"
nodeName1 = "Node01"
nodeName2 = "Node02"
clusterName = "WebCluster01"
serverPrefix = "AppServer"
numServers = 2
webServerName = "webserver1"
webServerHostName = "webserver.example.com"
webServerPort = "80"

def createCluster():
    """Create a new cluster and cluster members"""
    print "Creating cluster: %s" % clusterName
    
    # Check if cluster already exists
    existingClusters = AdminConfig.list("ServerCluster").splitlines()
    for cluster in existingClusters:
        if clusterName == AdminConfig.showAttribute(cluster, "name"):
            print "Cluster %s already exists" % clusterName
            return cluster
    
    # Create the cluster
    clusterID = AdminConfig.create("ServerCluster", AdminConfig.getid("/Cell:%s/" % cellName), [["name", clusterName]])
    AdminConfig.save()
    print "Cluster created successfully"
    
    # Create cluster members
    for i in range(1, numServers + 1):
        nodeName = nodeName1 if i % 2 == 1 else nodeName2
        serverName = "%s%d" % (serverPrefix, i)
        createClusterMember(clusterID, nodeName, serverName)
    
    return clusterID

def createClusterMember(clusterID, nodeName, serverName):
    """Create a cluster member on the specified node"""
    print "Creating cluster member: %s on node %s" % (serverName, nodeName)
    
    # Create the cluster member
    memberAttrs = [
        ["memberName", serverName],
        ["nodeName", nodeName],
        ["weight", "2"],
        ["replicatorEntry", "true"]
    ]
    
    memberID = AdminConfig.create("ClusterMember", clusterID, memberAttrs)
    AdminConfig.save()
    print "Cluster member %s created successfully" % serverName
    
    # Configure JVM parameters for the cluster member
    serverID = AdminConfig.getid("/Cell:%s/Node:%s/Server:%s/" % (cellName, nodeName, serverName))
    jvmID = AdminConfig.list("JavaVirtualMachine", serverID)
    
    jvmAttrs = [
        ["initialHeapSize", 512],
        ["maximumHeapSize", 1024],
        ["genericJvmArguments", "-Xgcpolicy:gencon -Xmn256m -Dcom.ibm.websphere.pmirm.timeout=180"]
    ]
    
    AdminConfig.modify(jvmID, jvmAttrs)
    AdminConfig.save()
    print "JVM parameters configured for %s" % serverName
    
    return memberID

def configureWebServer():
    """Configure web server for the cluster"""
    print "Configuring web server for cluster: %s" % clusterName
    
    # Check if web server exists
    webServers = AdminConfig.list("WebServer").splitlines()
    webServerExists = False
    
    for server in webServers:
        if webServerName == AdminConfig.showAttribute(server, "name"):
            webServerExists = True
            break
    
    if not webServerExists:
        # Create web server definition
        nodeID = AdminConfig.getid("/Cell:%s/Node:%s/" % (cellName, nodeName1))
        webServerAttrs = [
            ["name", webServerName],
            ["webserverHostname", webServerHostName],
            ["webserverPort", webServerPort],
            ["pluginInstallRoot", "${WAS_INSTALL_ROOT}/plugins"],
            ["configurationFile", "${WAS_INSTALL_ROOT}/plugins/config/%s/plugin-cfg.xml" % webServerName],
            ["serverIOTimeout", "60"]
        ]
        
        webServerID = AdminConfig.create("WebServer", nodeID, webServerAttrs)
        AdminConfig.save()
        print "Web server %s created successfully" % webServerName
    
    # Generate and propagate plugin
    print "Generating web server plugin for cluster"
    AdminTask.generatePluginCfg(["-clusterName", clusterName])
    
    print "Propagating plugin to web server"
    AdminTask.propagatePluginCfg(["-webServerName", webServerName, "-nodeName", nodeName1])
    
    AdminConfig.save()
    print "Web server configuration completed"

def startCluster():
    """Start the cluster and all its members"""
    print "Starting cluster: %s" % clusterName
    
    try:
        # Get cluster manager
        clusterMgr = AdminControl.completeObjectName("type=ClusterMgr,*")
        
        # Start the cluster
        AdminControl.invoke(clusterMgr, "startCluster", clusterName)
        
        # Wait for cluster to start
        print "Waiting for cluster to start..."
        time.sleep(30)
        
        # Check status
        state = AdminControl.getAttribute(clusterMgr, "state")
        print "Cluster state: %s" % state
        
        return True
    except:
        print "Error starting cluster: %s" % sys.exc_info()[0]
        return False

def stopCluster():
    """Stop the cluster and all its members"""
    print "Stopping cluster: %s" % clusterName
    
    try:
        # Get cluster manager
        clusterMgr = AdminControl.completeObjectName("type=ClusterMgr,*")
        
        # Stop the cluster
        AdminControl.invoke(clusterMgr, "stopCluster", clusterName)
        
        # Wait for cluster to stop
        print "Waiting for cluster to stop..."
        time.sleep(30)
        
        return True
    except:
        print "Error stopping cluster: %s" % sys.exc_info()[0]
        return False

def getClusterStatus():
    """Get the status of the cluster and its members"""
    print "Getting status for cluster: %s" % clusterName
    
    try:
        # Get cluster MBean
        clusterMBean = AdminControl.completeObjectName("type=Cluster,name=%s,*" % clusterName)
        
        if clusterMBean == "":
            print "Cluster %s is not running" % clusterName
            return False
        
        # Get cluster state
        state = AdminControl.getAttribute(clusterMBean, "state")
        print "Cluster state: %s" % state
        
        # Get status of individual members
        members = AdminControl.queryNames("type=ClusterMember,cluster=%s,*" % clusterName).splitlines()
        
        print "Cluster members status:"
        for member in members:
            memberName = AdminControl.getAttribute(member, "memberName")
            memberState = AdminControl.getAttribute(member, "state")
            print "  %s: %s" % (memberName, memberState)
        
        return True
    except:
        print "Error getting cluster status: %s" % sys.exc_info()[0]
        return False

# Main execution
if __name__ == "__main__":
    action = sys.argv[0] if len(sys.argv) > 0 else "status"
    
    if action == "create":
        createCluster()
        configureWebServer()
    elif action == "start":
        startCluster()
    elif action == "stop":
        stopCluster()
    elif action == "status":
        getClusterStatus()
    else:
        print "Usage: wsadmin -f %s [create|start|stop|status]" % __file__
        print "  create - Create a new cluster and configure web server"
        print "  start  - Start the cluster"
        print "  stop   - Stop the cluster"
        print "  status - Get cluster status"


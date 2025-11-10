"""
WebSphere Performance Tuning Script (Jython)
This script demonstrates how to configure performance-related settings in WebSphere
"""

# Import required modules
import sys
import os

# Configuration parameters
cellName = "YourCellName"
nodeName = "YourNodeName"
serverName = "YourServerName"

# Performance tuning parameters
jvmHeapMin = 1024
jvmHeapMax = 4096
threadPoolMin = 10
threadPoolMax = 100
connectionPoolMin = 10
connectionPoolMax = 100
connectionTimeout = 180
httpSessionTimeout = 30
httpKeepAlive = "true"
httpMaxKeepAliveConnections = 100
cacheDiskOffload = "true"
dynamicCacheSize = 2000
webContainerThreads = 50
asyncWorkManagerThreads = 30
pmiEnabled = "true"
pmiStatLevel = "high"

def configureJVMSettings():
    """Configure JVM settings for optimal performance"""
    print "Configuring JVM settings..."
    
    # Get server configuration
    serverID = AdminConfig.getid("/Cell:%s/Node:%s/Server:%s/" % (cellName, nodeName, serverName))
    
    # Get JVM configuration
    jvmID = AdminConfig.list("JavaVirtualMachine", serverID)
    
    # Configure JVM settings
    AdminConfig.modify(jvmID, [
        ["initialHeapSize", jvmHeapMin],
        ["maximumHeapSize", jvmHeapMax],
        ["genericJvmArguments", "-Xgcpolicy:gencon -Xmn512m -Xcompressedrefs -Xgc:preferredHeapBase=0x100000000 -Xdisableexplicitgc -XX:+UseParallelGC -XX:ParallelGCThreads=8 -Dcom.ibm.websphere.pmirm.timeout=180"]
    ])
    
    # Save configuration
    AdminConfig.save()
    print "JVM settings configured successfully"

def configureThreadPools():
    """Configure thread pools for optimal performance"""
    print "Configuring thread pools..."
    
    # Get server configuration
    serverID = AdminConfig.getid("/Cell:%s/Node:%s/Server:%s/" % (cellName, nodeName, serverName))
    
    # Configure WebContainer thread pool
    threadPoolID = AdminConfig.list("ThreadPool", serverID)
    for pool in threadPoolID.splitlines():
        name = AdminConfig.showAttribute(pool, "name")
        if name == "WebContainer":
            AdminConfig.modify(pool, [
                ["minimumSize", threadPoolMin],
                ["maximumSize", threadPoolMax],
                ["inactivityTimeout", "3500"],
                ["isGrowable", "true"]
            ])
            print "WebContainer thread pool configured"
    
    # Configure Default thread pool
    for pool in threadPoolID.splitlines():
        name = AdminConfig.showAttribute(pool, "name")
        if name == "Default":
            AdminConfig.modify(pool, [
                ["minimumSize", "5"],
                ["maximumSize", "20"],
                ["inactivityTimeout", "3500"],
                ["isGrowable", "true"]
            ])
            print "Default thread pool configured"
    
    # Configure ORB thread pool
    for pool in threadPoolID.splitlines():
        name = AdminConfig.showAttribute(pool, "name")
        if name == "ORB.thread.pool":
            AdminConfig.modify(pool, [
                ["minimumSize", "10"],
                ["maximumSize", "50"],
                ["inactivityTimeout", "3500"],
                ["isGrowable", "true"]
            ])
            print "ORB thread pool configured"
    
    # Save configuration
    AdminConfig.save()
    print "Thread pools configured successfully"

def configureConnectionPools():
    """Configure connection pools for optimal performance"""
    print "Configuring connection pools..."
    
    # Get all data sources
    dataSources = AdminConfig.list("DataSource").splitlines()
    
    for ds in dataSources:
        dsName = AdminConfig.showAttribute(ds, "name")
        print "Configuring connection pool for data source: %s" % dsName
        
        # Get connection pool
        connPool = AdminConfig.list("ConnectionPool", ds)
        
        if connPool:
            # Configure connection pool
            AdminConfig.modify(connPool, [
                ["minConnections", connectionPoolMin],
                ["maxConnections", connectionPoolMax],
                ["connectionTimeout", connectionTimeout],
                ["agedTimeout", "1800"],
                ["purgePolicy", "EntirePool"],
                ["reapTime", "180"],
                ["unusedTimeout", "1800"],
                ["stuckTime", "0"],
                ["stuckThreshold", "0"]
            ])
            print "Connection pool for %s configured" % dsName
    
    # Save configuration
    AdminConfig.save()
    print "Connection pools configured successfully"

def configureWebContainer():
    """Configure web container for optimal performance"""
    print "Configuring web container..."
    
    # Get server configuration
    serverID = AdminConfig.getid("/Cell:%s/Node:%s/Server:%s/" % (cellName, nodeName, serverName))
    
    # Get web container
    webContainerID = AdminConfig.list("WebContainer", serverID)
    
    # Configure web container
    if webContainerID:
        AdminConfig.modify(webContainerID, [
            ["enableServletCaching", "true"],
            ["disablePooling", "false"]
        ])
        
        # Configure session management
        sessionManagerID = AdminConfig.list("SessionManager", serverID)
        if sessionManagerID:
            AdminConfig.modify(sessionManagerID, [
                ["enableUrlRewriting", "false"],
                ["enableCookies", "true"],
                ["enableSSLTracking", "false"],
                ["enableProtocolSwitchRewriting", "false"],
                ["sessionPersistenceMode", "NONE"],
                ["tuningParams", [["allowOverflow", "false"], ["invalidationTimeout", str(httpSessionTimeout * 60)], ["maxInMemorySessionCount", "1000"]]]
            ])
            print "Session management configured"
    
    # Configure HTTP transport channel
    transports = AdminConfig.list("HTTPInboundChannel", serverID).splitlines()
    for transport in transports:
        AdminConfig.modify(transport, [
            ["keepAlive", httpKeepAlive],
            ["maximumPersistentRequests", httpMaxKeepAliveConnections],
            ["readTimeout", "60"],
            ["writeTimeout", "60"],
            ["persistentTimeout", "30"]
        ])
        print "HTTP transport channel configured"
    
    # Save configuration
    AdminConfig.save()
    print "Web container configured successfully"

def configureDynamicCache():
    """Configure dynamic cache for optimal performance"""
    print "Configuring dynamic cache..."
    
    # Get server configuration
    serverID = AdminConfig.getid("/Cell:%s/Node:%s/Server:%s/" % (cellName, nodeName, serverName))
    
    # Get dynamic cache service
    cacheID = AdminConfig.list("DynamicCache", serverID)
    
    # Configure dynamic cache
    if cacheID:
        AdminConfig.modify(cacheID, [
            ["enableCacheReplication", "false"],
            ["enableDiskOffload", cacheDiskOffload],
            ["flushToDisk", "false"],
            ["memoryCacheSizeInMB", dynamicCacheSize],
            ["diskCacheSizeInMB", str(dynamicCacheSize * 2)],
            ["diskCacheSizeInEntries", "10000"],
            ["memoryCacheSizeInEntries", "10000"],
            ["cacheSize", dynamicCacheSize]
        ])
        print "Dynamic cache configured"
    
    # Save configuration
    AdminConfig.save()
    print "Dynamic cache configured successfully"

def configureAsyncWorkManager():
    """Configure async work manager for optimal performance"""
    print "Configuring async work manager..."
    
    # Get server configuration
    serverID = AdminConfig.getid("/Cell:%s/Node:%s/Server:%s/" % (cellName, nodeName, serverName))
    
    # Get async work managers
    asyncMgrs = AdminConfig.list("AsyncWorkManager", serverID).splitlines()
    
    for mgr in asyncMgrs:
        name = AdminConfig.showAttribute(mgr, "name")
        print "Configuring async work manager: %s" % name
        
        # Configure work manager
        AdminConfig.modify(mgr, [
            ["minThreads", "5"],
            ["maxThreads", asyncWorkManagerThreads],
            ["threadPriority", "5"],
            ["isGrowable", "true"]
        ])
    
    # Save configuration
    AdminConfig.save()
    print "Async work manager configured successfully"

def configurePMI():
    """Configure Performance Monitoring Infrastructure (PMI)"""
    print "Configuring PMI..."
    
    # Enable PMI
    AdminConfig.modify("PMIService", [["enable", pmiEnabled], ["statisticSet", pmiStatLevel]])
    
    # Configure specific PMI modules
    if pmiEnabled == "true":
        # Get server configuration
        serverID = AdminConfig.getid("/Cell:%s/Node:%s/Server:%s/" % (cellName, nodeName, serverName))
        
        # Enable specific PMI modules
        AdminControl.invoke("WebSphere:type=PMIService,process=%s,node=%s,*" % (serverName, nodeName), 
                           "enableStatsModule", 
                           "[threadPoolModule true]")
        
        AdminControl.invoke("WebSphere:type=PMIService,process=%s,node=%s,*" % (serverName, nodeName), 
                           "enableStatsModule", 
                           "[connectionPoolModule true]")
        
        AdminControl.invoke("WebSphere:type=PMIService,process=%s,node=%s,*" % (serverName, nodeName), 
                           "enableStatsModule", 
                           "[webAppModule true]")
        
        AdminControl.invoke("WebSphere:type=PMIService,process=%s,node=%s,*" % (serverName, nodeName), 
                           "enableStatsModule", 
                           "[systemModule true]")
        
        print "PMI modules enabled"
    
    # Save configuration
    AdminConfig.save()
    print "PMI configured successfully"

def configureORB():
    """Configure ORB (Object Request Broker) settings"""
    print "Configuring ORB settings..."
    
    # Get server configuration
    serverID = AdminConfig.getid("/Cell:%s/Node:%s/Server:%s/" % (cellName, nodeName, serverName))
    
    # Get ORB
    orbID = AdminConfig.list("ObjectRequestBroker", serverID)
    
    # Configure ORB
    if orbID:
        AdminConfig.modify(orbID, [
            ["requestTimeout", "180"],
            ["connectionCacheMinimum", "10"],
            ["connectionCacheMaximum", "50"],
            ["noLocalCopies", "false"],
            ["cacheTimeout", "180"]
        ])
        print "ORB configured"
    
    # Save configuration
    AdminConfig.save()
    print "ORB settings configured successfully"

def configureTransactionService():
    """Configure transaction service for optimal performance"""
    print "Configuring transaction service..."
    
    # Get server configuration
    serverID = AdminConfig.getid("/Cell:%s/Node:%s/Server:%s/" % (cellName, nodeName, serverName))
    
    # Get transaction service
    tsID = AdminConfig.list("TransactionService", serverID)
    
    # Configure transaction service
    if tsID:
        AdminConfig.modify(tsID, [
            ["totalTranLifetimeTimeout", "300"],
            ["clientInactivityTimeout", "60"],
            ["transactionLogDirectory", "${USER_INSTALL_ROOT}/tranlog"],
            ["heuristicRetryLimit", "0"],
            ["heuristicRetryWait", "0"]
        ])
        print "Transaction service configured"
    
    # Save configuration
    AdminConfig.save()
    print "Transaction service configured successfully"

def generatePerformanceReport():
    """Generate a performance report"""
    print "Generating performance report..."
    
    # Create a report of current settings
    report = []
    report.append("WebSphere Performance Configuration Report")
    report.append("=========================================")
    report.append("")
    
    # JVM settings
    serverID = AdminConfig.getid("/Cell:%s/Node:%s/Server:%s/" % (cellName, nodeName, serverName))
    jvmID = AdminConfig.list("JavaVirtualMachine", serverID)
    initialHeap = AdminConfig.showAttribute(jvmID, "initialHeapSize")
    maxHeap = AdminConfig.showAttribute(jvmID, "maximumHeapSize")
    jvmArgs = AdminConfig.showAttribute(jvmID, "genericJvmArguments")
    
    report.append("JVM Settings:")
    report.append("  Initial Heap: %s MB" % initialHeap)
    report.append("  Maximum Heap: %s MB" % maxHeap)
    report.append("  JVM Arguments: %s" % jvmArgs)
    report.append("")
    
    # Thread pools
    report.append("Thread Pool Settings:")
    threadPoolID = AdminConfig.list("ThreadPool", serverID)
    for pool in threadPoolID.splitlines():
        name = AdminConfig.showAttribute(pool, "name")
        minSize = AdminConfig.showAttribute(pool, "minimumSize")
        maxSize = AdminConfig.showAttribute(pool, "maximumSize")
        report.append("  %s: Min=%s, Max=%s" % (name, minSize, maxSize))
    report.append("")
    
    # Connection pools
    report.append("Connection Pool Settings:")
    dataSources = AdminConfig.list("DataSource").splitlines()
    for ds in dataSources:
        dsName = AdminConfig.showAttribute(ds, "name")
        connPool = AdminConfig.list("ConnectionPool", ds)
        if connPool:
            minConn = AdminConfig.showAttribute(connPool, "minConnections")
            maxConn = AdminConfig.showAttribute(connPool, "maxConnections")
            timeout = AdminConfig.showAttribute(connPool, "connectionTimeout")
            report.append("  %s: Min=%s, Max=%s, Timeout=%s" % (dsName, minConn, maxConn, timeout))
    report.append("")
    
    # Web container
    report.append("Web Container Settings:")
    webContainerID = AdminConfig.list("WebContainer", serverID)
    if webContainerID:
        servletCaching = AdminConfig.showAttribute(webContainerID, "enableServletCaching")
        report.append("  Servlet Caching: %s" % servletCaching)
    
    sessionManagerID = AdminConfig.list("SessionManager", serverID)
    if sessionManagerID:
        timeout = AdminConfig.showAttribute(sessionManagerID, "invalidationTimeout")
        report.append("  Session Timeout: %s minutes" % timeout)
    report.append("")
    
    # Dynamic cache
    report.append("Dynamic Cache Settings:")
    cacheID = AdminConfig.list("DynamicCache", serverID)
    if cacheID:
        cacheSize = AdminConfig.showAttribute(cacheID, "cacheSize")
        diskOffload = AdminConfig.showAttribute(cacheID, "enableDiskOffload")
        report.append("  Cache Size: %s MB" % cacheSize)
        report.append("  Disk Offload: %s" % diskOffload)
    report.append("")
    
    # PMI
    report.append("PMI Settings:")
    pmiEnabled = AdminConfig.showAttribute("PMIService", "enable")
    pmiLevel = AdminConfig.showAttribute("PMIService", "statisticSet")
    report.append("  Enabled: %s" % pmiEnabled)
    report.append("  Statistic Level: %s" % pmiLevel)
    report.append("")
    
    # Write report to file
    reportFile = open("/tmp/was_performance_report.txt", "w")
    for line in report:
        reportFile.write(line + "\n")
    reportFile.close()
    
    print "Performance report generated at /tmp/was_performance_report.txt"

# Main execution
if __name__ == "__main__":
    action = sys.argv[0] if len(sys.argv) > 0 else "all"
    
    if action == "jvm" or action == "all":
        configureJVMSettings()
    
    if action == "threads" or action == "all":
        configureThreadPools()
    
    if action == "connections" or action == "all":
        configureConnectionPools()
    
    if action == "web" or action == "all":
        configureWebContainer()
    
    if action == "cache" or action == "all":
        configureDynamicCache()
    
    if action == "async" or action == "all":
        configureAsyncWorkManager()
    
    if action == "pmi" or action == "all":
        configurePMI()
    
    if action == "orb" or action == "all":
        configureORB()
    
    if action == "transactions" or action == "all":
        configureTransactionService()
    
    if action == "report":
        generatePerformanceReport()
    
    if action not in ["jvm", "threads", "connections", "web", "cache", "async", "pmi", "orb", "transactions", "report", "all"]:
        print "Usage: wsadmin -f %s [jvm|threads|connections|web|cache|async|pmi|orb|transactions|report|all]" % __file__
        print "  jvm          - Configure JVM settings"
        print "  threads      - Configure thread pools"
        print "  connections  - Configure connection pools"
        print "  web          - Configure web container"
        print "  cache        - Configure dynamic cache"
        print "  async        - Configure async work manager"
        print "  pmi          - Configure PMI"
        print "  orb          - Configure ORB settings"
        print "  transactions - Configure transaction service"
        print "  report       - Generate performance report"
        print "  all          - Configure all performance settings (default)"

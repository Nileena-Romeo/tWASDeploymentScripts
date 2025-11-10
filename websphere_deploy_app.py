"""
WebSphere Application Deployment Script (Jython)
This script demonstrates how to deploy an application to WebSphere using wsadmin
"""

# Import required modules
import sys
import os
import java.lang.System

# Configuration parameters
nodeName = "YourNodeName"
serverName = "YourServerName"
cellName = "YourCellName"
clusterName = "YourClusterName"  # If deploying to a cluster
earFile = "/path/to/your/application.ear"
appName = "YourApplicationName"
contextRoot = "/yourContextRoot"  # For web modules

# Get AdminApp and AdminConfig objects
def deployApplication():
    print "Starting application deployment..."
    
    # Check if application already exists and remove if it does
    appList = AdminApp.list().splitlines()
    if appName in appList:
        print "Application %s already exists. Uninstalling..." % appName
        AdminApp.uninstall(appName)
        AdminConfig.save()
    
    # Set deployment options
    options = [
        '-appname', appName,
        '-node', nodeName,
        '-server', serverName,
        '-contextroot', contextRoot,
        '-MapWebModToVH', [['.*', '.*', 'default_host']],
        '-usedefaultbindings',
        '-defaultbinding.virtual.host', 'default_host',
        '-nouseMetaDataFromBinary'
    ]
    
    # For cluster deployment, use these options instead:
    # options = [
    #     '-appname', appName,
    #     '-cluster', clusterName,
    #     '-contextroot', contextRoot,
    #     '-MapWebModToVH', [['.*', '.*', 'default_host']],
    #     '-usedefaultbindings',
    #     '-defaultbinding.virtual.host', 'default_host',
    #     '-nouseMetaDataFromBinary'
    # ]
    
    # Install the application
    print "Installing application %s from %s" % (appName, earFile)
    AdminApp.install(earFile, options)
    
    # Save the configuration
    print "Saving configuration..."
    AdminConfig.save()
    
    # Start the application
    print "Starting application..."
    appManager = AdminControl.queryNames('type=ApplicationManager,node=%s,process=%s,*' % (nodeName, serverName))
    AdminControl.invoke(appManager, 'startApplication', appName)
    
    print "Application %s deployed successfully" % appName

# Main execution
if __name__ == "__main__":
    deployApplication()
    print "Deployment script completed"


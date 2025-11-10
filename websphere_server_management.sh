#!/bin/bash
# WebSphere Server Management Script
# This script provides functions to start, stop, and check status of WebSphere servers

# Configuration
WAS_HOME="/opt/IBM/WebSphere/AppServer"
PROFILE_NAME="AppSrv01"
NODE_NAME="Node01"
SERVER_NAME="server1"
ADMIN_USER="wasadmin"
ADMIN_PASSWORD="password"

# Source WebSphere environment
if [ -f "${WAS_HOME}/profiles/${PROFILE_NAME}/bin/setupCmdLine.sh" ]; then
    . "${WAS_HOME}/profiles/${PROFILE_NAME}/bin/setupCmdLine.sh"
else
    echo "ERROR: WebSphere profile not found at ${WAS_HOME}/profiles/${PROFILE_NAME}"
    exit 1
fi

# Function to check if server is running
check_server_status() {
    echo "Checking status of ${SERVER_NAME}..."
    "${WAS_HOME}/profiles/${PROFILE_NAME}/bin/serverStatus.sh" ${SERVER_NAME} -username ${ADMIN_USER} -password ${ADMIN_PASSWORD}
    return $?
}

# Function to start the server
start_server() {
    echo "Starting ${SERVER_NAME}..."
    "${WAS_HOME}/profiles/${PROFILE_NAME}/bin/startServer.sh" ${SERVER_NAME} -username ${ADMIN_USER} -password ${ADMIN_PASSWORD}
    
    # Wait for server to start
    echo "Waiting for server to start..."
    sleep 10
    
    # Check if server started successfully
    check_server_status
    if [ $? -eq 0 ]; then
        echo "Server ${SERVER_NAME} started successfully."
    else
        echo "ERROR: Failed to start server ${SERVER_NAME}."
        exit 1
    fi
}

# Function to stop the server
stop_server() {
    echo "Stopping ${SERVER_NAME}..."
    "${WAS_HOME}/profiles/${PROFILE_NAME}/bin/stopServer.sh" ${SERVER_NAME} -username ${ADMIN_USER} -password ${ADMIN_PASSWORD}
    
    # Wait for server to stop
    echo "Waiting for server to stop..."
    sleep 10
    
    # Check if server stopped successfully
    check_server_status
    if [ $? -ne 0 ]; then
        echo "Server ${SERVER_NAME} stopped successfully."
    else
        echo "WARNING: Server ${SERVER_NAME} may still be running."
        
        # Force stop if necessary
        read -p "Do you want to force stop the server? (y/n): " force_stop
        if [ "$force_stop" = "y" ]; then
            echo "Force stopping ${SERVER_NAME}..."
            "${WAS_HOME}/profiles/${PROFILE_NAME}/bin/stopServer.sh" ${SERVER_NAME} -username ${ADMIN_USER} -password ${ADMIN_PASSWORD} -force
        fi
    fi
}

# Function to restart the server
restart_server() {
    stop_server
    start_server
}

# Function to deploy an application using wsadmin
deploy_application() {
    if [ -z "$1" ]; then
        echo "ERROR: No EAR file specified for deployment."
        echo "Usage: $0 deploy /path/to/application.ear ApplicationName"
        exit 1
    fi
    
    EAR_FILE="$1"
    APP_NAME="${2:-$(basename ${EAR_FILE%.*})}"
    
    echo "Deploying application ${APP_NAME} from ${EAR_FILE}..."
    
    # Create a temporary Jython script for deployment
    TEMP_SCRIPT=$(mktemp)
    cat > ${TEMP_SCRIPT} << EOF
appName = "${APP_NAME}"
earFile = "${EAR_FILE}"
nodeName = "${NODE_NAME}"
serverName = "${SERVER_NAME}"

print "Checking if application already exists..."
appList = AdminApp.list().splitlines()
if appName in appList:
    print "Application %s already exists. Uninstalling..." % appName
    AdminApp.uninstall(appName)
    AdminConfig.save()

print "Installing application %s from %s" % (appName, earFile)
options = ['-appname', appName, 
           '-node', nodeName, 
           '-server', serverName, 
           '-usedefaultbindings']
AdminApp.install(earFile, options)
AdminConfig.save()

print "Starting application..."
appManager = AdminControl.queryNames('type=ApplicationManager,node=%s,process=%s,*' % (nodeName, serverName))
AdminControl.invoke(appManager, 'startApplication', appName)

print "Application %s deployed successfully" % appName
EOF
    
    # Run the deployment script
    "${WAS_HOME}/profiles/${PROFILE_NAME}/bin/wsadmin.sh" -lang jython -f ${TEMP_SCRIPT} -username ${ADMIN_USER} -password ${ADMIN_PASSWORD}
    
    # Clean up
    rm ${TEMP_SCRIPT}
}

# Function to show server logs
show_logs() {
    LOG_FILE="${WAS_HOME}/profiles/${PROFILE_NAME}/logs/${SERVER_NAME}/SystemOut.log"
    
    if [ -f "${LOG_FILE}" ]; then
        if command -v tail >/dev/null 2>&1; then
            echo "Showing last 50 lines of ${SERVER_NAME} logs..."
            tail -n 50 "${LOG_FILE}"
            
            read -p "Do you want to follow the logs? (y/n): " follow_logs
            if [ "$follow_logs" = "y" ]; then
                tail -f "${LOG_FILE}"
            fi
        else
            echo "Last 50 lines of ${SERVER_NAME} logs:"
            cat "${LOG_FILE}" | tail -n 50
        fi
    else
        echo "ERROR: Log file not found at ${LOG_FILE}"
    fi
}

# Main script execution
case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        check_server_status
        ;;
    deploy)
        deploy_application "$2" "$3"
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|deploy|logs}"
        echo "  start   - Start the WebSphere server"
        echo "  stop    - Stop the WebSphere server"
        echo "  restart - Restart the WebSphere server"
        echo "  status  - Check the status of the WebSphere server"
        echo "  deploy  - Deploy an application (requires EAR file path)"
        echo "  logs    - Show server logs"
        exit 1
        ;;
esac

exit 0

# Made with Bob

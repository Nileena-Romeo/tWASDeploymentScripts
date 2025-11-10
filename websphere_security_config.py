"""
WebSphere Security Configuration Script (Jython)
This script demonstrates how to configure security settings in WebSphere
"""

# Import required modules
import sys
import os

# Configuration parameters
cellName = "YourCellName"
nodeName = "YourNodeName"
serverName = "YourServerName"
ldapHost = "ldap.example.com"
ldapPort = "389"
ldapBindDN = "cn=wasadmin,dc=example,dc=com"
ldapBindPassword = "password"
ldapBaseDN = "dc=example,dc=com"
ldapUserFilter = "(&(uid=%v)(objectclass=inetOrgPerson))"
ldapGroupFilter = "(&(cn=%v)(objectclass=groupOfUniqueNames))"
sslKeystore = "/path/to/keystore.p12"
sslKeystorePassword = "keystorePassword"
sslTruststore = "/path/to/truststore.p12"
sslTruststorePassword = "truststorePassword"

def configureLDAPRegistry():
    """Configure LDAP user registry"""
    print "Configuring LDAP user registry..."
    
    # Get security configuration
    securityID = AdminConfig.getid("/Cell:%s/Security:/" % cellName)
    
    # Check if LDAP is already configured
    userRegistries = AdminTask.listUserRegistries(["-cell", cellName])
    if "LDAP" in userRegistries:
        print "LDAP registry already configured. Updating settings..."
        
        # Get LDAP registry ID
        ldapID = AdminConfig.getid("/Cell:%s/LDAPUserRegistry:/" % cellName)
        
        # Update LDAP settings
        AdminConfig.modify(ldapID, [
            ["host", ldapHost],
            ["port", ldapPort],
            ["baseDN", ldapBaseDN],
            ["bindDN", ldapBindDN],
            ["bindPassword", ldapBindPassword],
            ["userFilter", ldapUserFilter],
            ["groupFilter", ldapGroupFilter],
            ["searchTimeout", "120"],
            ["reuseConnection", "true"]
        ])
    else:
        print "Setting up new LDAP registry..."
        
        # Configure LDAP registry
        AdminTask.configureAdminLDAPUserRegistry([
            "-ldapHost", ldapHost,
            "-ldapPort", ldapPort,
            "-baseDN", ldapBaseDN,
            "-bindDN", ldapBindDN,
            "-bindPassword", ldapBindPassword,
            "-userFilter", ldapUserFilter,
            "-groupFilter", ldapGroupFilter,
            "-certificateMapMode", "exactdn",
            "-certificateFilter", "cn=%u,ou=users,dc=example,dc=com"
        ])
    
    # Set as active user registry
    AdminTask.setAdminActiveSecuritySettings(["-activeUserRegistry", "LDAP"])
    
    # Save configuration
    AdminConfig.save()
    print "LDAP user registry configured successfully"

def configureSSL():
    """Configure SSL settings"""
    print "Configuring SSL settings..."
    
    # Get security configuration
    securityID = AdminConfig.getid("/Cell:%s/Security:/" % cellName)
    
    # Configure SSL
    sslConfigID = AdminTask.createSSLConfig([
        "-cellDefaultSSLSettings", "true",
        "-keyStoreName", sslKeystore,
        "-keyStorePassword", sslKeystorePassword,
        "-keyStoreType", "PKCS12",
        "-trustStoreName", sslTruststore,
        "-trustStorePassword", sslTruststorePassword,
        "-trustStoreType", "PKCS12"
    ])
    
    # Save configuration
    AdminConfig.save()
    print "SSL configuration completed successfully"

def configureGlobalSecurity():
    """Configure global security settings"""
    print "Configuring global security settings..."
    
    # Get security configuration
    securityID = AdminConfig.getid("/Cell:%s/Security:/" % cellName)
    
    # Enable global security
    AdminTask.setGlobalSecurity([
        "-enabled", "true",
        "-enforceJava2Security", "false",
        "-appEnabled", "true",
        "-activeProtocol", "BOTH",
        "-activeAuthMechanism", "LTPA",
        "-cacheTimeout", "600",
        "-useDomainQualifiedUserNames", "false"
    ])
    
    # Configure LTPA
    AdminTask.configureLTPAToken([
        "-password", "ltpaPassword",
        "-timeout", "120"
    ])
    
    # Save configuration
    AdminConfig.save()
    print "Global security configured successfully"

def configureJAASAuthentication():
    """Configure JAAS authentication entries"""
    print "Configuring JAAS authentication entries..."
    
    # Create JAAS authentication entries for database access
    AdminTask.createAuthDataEntry([
        "-alias", "DBAuthAlias",
        "-user", "dbuser",
        "-password", "dbpassword",
        "-description", "Database authentication"
    ])
    
    # Create JAAS authentication entries for MQ access
    AdminTask.createAuthDataEntry([
        "-alias", "MQAuthAlias",
        "-user", "mquser",
        "-password", "mqpassword",
        "-description", "MQ authentication"
    ])
    
    # Save configuration
    AdminConfig.save()
    print "JAAS authentication entries configured successfully"

def configureApplicationSecurity():
    """Configure application security roles"""
    print "Configuring application security roles..."
    
    # Map application roles to LDAP groups
    # This is typically done per application, but here's a general example
    
    # Get application deployment ID
    appName = "YourApplication"
    appID = AdminConfig.getid("/Deployment:%s/" % appName)
    
    if appID:
        # Map roles
        AdminApp.edit(appName, [
            "-MapRolesToUsers", [
                ["Administrator", "No", "No", "Yes", "cn=admins,ou=groups,dc=example,dc=com"],
                ["Manager", "No", "No", "Yes", "cn=managers,ou=groups,dc=example,dc=com"],
                ["User", "No", "No", "Yes", "cn=users,ou=groups,dc=example,dc=com"]
            ]
        ])
        
        # Save configuration
        AdminConfig.save()
        print "Application security roles configured successfully"
    else:
        print "Application %s not found" % appName

def configureCSRF():
    """Configure Cross-Site Request Forgery (CSRF) protection"""
    print "Configuring CSRF protection..."
    
    # Get security configuration
    securityID = AdminConfig.getid("/Cell:%s/Security:/" % cellName)
    
    # Configure CSRF protection
    AdminTask.configureCSRFProtection([
        "-enabled", "true",
        "-csrfExpirationInMinutes", "30"
    ])
    
    # Save configuration
    AdminConfig.save()
    print "CSRF protection configured successfully"

def configureTrustedRealms():
    """Configure trusted realms for SSO"""
    print "Configuring trusted realms..."
    
    # Configure trusted realms
    AdminTask.configureTrustedRealms([
        "-realmName", "TrustedRealm",
        "-realmHostName", "*.example.com",
        "-realmType", "HOSTNAME"
    ])
    
    # Save configuration
    AdminConfig.save()
    print "Trusted realms configured successfully"

def configureAudit():
    """Configure security auditing"""
    print "Configuring security auditing..."
    
    # Get security configuration
    securityID = AdminConfig.getid("/Cell:%s/Security:/" % cellName)
    
    # Configure audit
    AdminTask.configureAudit([
        "-dataLocation", "${USER_INSTALL_ROOT}/logs/audit",
        "-enableAudit", "true",
        "-enableAuditForSecurity", "true",
        "-firewallType", "none",
        "-maxFileSize", "20",
        "-maxLogs", "10",
        "-writeInterval", "1"
    ])
    
    # Save configuration
    AdminConfig.save()
    print "Security auditing configured successfully"

# Main execution
if __name__ == "__main__":
    action = sys.argv[0] if len(sys.argv) > 0 else "all"
    
    if action == "ldap" or action == "all":
        configureLDAPRegistry()
    
    if action == "ssl" or action == "all":
        configureSSL()
    
    if action == "global" or action == "all":
        configureGlobalSecurity()
    
    if action == "jaas" or action == "all":
        configureJAASAuthentication()
    
    if action == "app" or action == "all":
        configureApplicationSecurity()
    
    if action == "csrf" or action == "all":
        configureCSRF()
    
    if action == "realms" or action == "all":
        configureTrustedRealms()
    
    if action == "audit" or action == "all":
        configureAudit()
    
    if action not in ["ldap", "ssl", "global", "jaas", "app", "csrf", "realms", "audit", "all"]:
        print "Usage: wsadmin -f %s [ldap|ssl|global|jaas|app|csrf|realms|audit|all]" % __file__
        print "  ldap   - Configure LDAP user registry"
        print "  ssl    - Configure SSL settings"
        print "  global - Configure global security settings"
        print "  jaas   - Configure JAAS authentication entries"
        print "  app    - Configure application security roles"
        print "  csrf   - Configure CSRF protection"
        print "  realms - Configure trusted realms"
        print "  audit  - Configure security auditing"
        print "  all    - Configure all security settings (default)"


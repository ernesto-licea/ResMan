from ldap3 import ObjectDef, AttrDef, Server, Connection, NTLM, ALL, Reader, Writer


class LdapUser:
    def __init__(self,server,user):
        self.server = server
        self.user = user

        self.person = ObjectDef(['top', 'organizationalPerson', 'user'])
        self.person += AttrDef('distinguishedName', key='dn')
        self.person += AttrDef('objectClass', key='object_class')
        self.person += AttrDef('cn', key='cn')
        self.person += AttrDef('sAMAccountName', key='username')
        self.person += AttrDef('givenName', key='first_name')
        self.person += AttrDef('sn', key='last_name')
        self.person += AttrDef('displayName', key='full_name')
        self.person += AttrDef('userPrincipalName', key='email')
        self.person += AttrDef('userAccountControl', key='control')

        self.person += AttrDef(server.email_domain, key='email_domain')
        self.person += AttrDef(server.email_buzon_size, key='email_buzon_size')
        self.person += AttrDef(server.email_message_size, key='email_message_size')

        self.person += AttrDef(server.internet_domain, key='internet_domain')
        self.person += AttrDef(server.internet_quota_type, key='internet_quota_type')
        self.person += AttrDef(server.internet_quota_size, key='internet_quota_size')
        self.person += AttrDef(server.internet_extra_quota_size, key='internet_extra_quota_size')

        self.person += AttrDef(server.ftp_home, key='ftp_folder')
        self.person += AttrDef(server.ftp_size, key='ftp_size')

    def add_user(self):
        ldap_server = Server(
            host = self.server.server_host,
            port = self.server.server_port,
            use_ssl = self.server.start_tls,
            get_info=ALL
        )

        connection = Connection(
            server = ldap_server,
            user = self.server.admin_username,
            password = self.server.admin_password,
            raise_exceptions = True,
            authentication = NTLM
        )
        connection.bind()

        cursor_reader = Reader(connection,self.person,self.server.search_base)
        cursor_reader.search()

        cursor_writer = Writer.from_cursor(cursor_reader)

        ldap_user = cursor_writer.new(
            dn="CN={},{}".format(
                self.user.username,
                self.server.search_base
            )
        )

        ldap_user.cn = self.user.username
        ldap_user.username = self.user.username
        ldap_user.first_name = self.user.first_name
        ldap_user.last_name = self.user.last_name
        ldap_user.full_name = self.user.get_full_name()

        if self.user.email:
            ldap_user.email = self.user.email

        if self.user.email_domain:
            ldap_user.email_domain = self.user.email_domain

        if self.user.email_buzon_size:
            ldap_user.email_buzon_size = self.user.email_buzon_size

        if self.user.email_message_size:
            ldap_user.email_message_size = self.user.email_message_size

        if self.user.internet_domain:
            ldap_user.internet_domain = self.user.internet_domain

        if self.user.internet_quota_type:
            ldap_user.internet_quota_type = self.user.internet_quota_type

        if self.user.internet_quota_size:
            ldap_user.internet_quota_size = self.user.internet_quota_size

        if self.user.internet_extra_quota_size:
            ldap_user.internet_extra_quota_size = self.user.internet_extra_quota_size

        if self.user.ftp_folder:
            ldap_user.ftp_folder = self.user.ftp_folder

        if self.user.ftp_size:
            ldap_user.ftp_size = self.user.ftp_size

        ldap_user.entry_commit_changes()

        connection.extend.microsoft.modify_password(
            user=ldap_user.entry_dn,
            new_password=self.user._password,
            old_password=None
        )

        ldap_user.control = 512
        ldap_user.entry_commit_changes()

        connection.unbind()

    def edit_user(self):
        pass

    def reset_password(self,new_password):
        pass

    def remove_user(self):
        pass

class LdapGroup:
    def __init__(self,server,group):
        self.server = server
        self.group = group

        self.obj = ObjectDef(['top', 'group'])
        self.obj += AttrDef('distinguishedName', key='dn')
        self.obj += AttrDef('objectClass', key='object_class')
        self.obj += AttrDef('cn', key='cn')
        self.obj += AttrDef('mail', key='email')
        self.obj += AttrDef('sAMAccountName', key='slug_name')
        self.obj += AttrDef('groupType', key='type')

    def save(self):
        ldap_server = Server(
            host = self.server.server_host,
            port = self.server.server_port,
            use_ssl = self.server.start_tls,
            get_info=ALL
        )

        connection = Connection(
            server = ldap_server,
            user = self.server.admin_username,
            password = self.server.admin_password,
            raise_exceptions = True,
            authentication = NTLM
        )
        connection.bind()

        query = 'cn: {}'.format(
                self.group.name,
            )

        cursor_reader = Reader(connection,self.obj,self.server.search_base,query=query)
        cursor_reader.search()
        cursor_writer = Writer.from_cursor(cursor_reader)
        if cursor_reader.entries:
            ldap_group = cursor_writer[0]

        else:

            ldap_group = cursor_writer.new(
                dn="CN={},{}".format(
                    self.group.name,
                    self.server.search_base
                )
            )

            ldap_group.cn = self.group.name
            ldap_group.slug_name = self.group.slugname

        if self.group.service_type == 'security':
            ldap_group.type = -2147483646
        else:
            ldap_group.type = 2
            ldap_group.email = self.group.email

        ldap_group.entry_commit_changes()

        connection.unbind()



from ldap3 import ObjectDef, AttrDef, Server, Connection, NTLM, ALL, Reader, Writer
import base64

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
        self.person += AttrDef('userPrincipalName', key='logon')
        self.person += AttrDef('mail', key='email')
        self.person += AttrDef('extensionName', key='email_canonical')
        self.person += AttrDef('userAccountControl', key='control')
        self.person += AttrDef('memberOf', key='groups')

        self.person += AttrDef(server.email_domain, key='email_domain')
        self.person += AttrDef(server.email_buzon_size, key='email_buzon_size')
        self.person += AttrDef(server.email_message_size, key='email_message_size')

        self.person += AttrDef(server.internet_domain, key='internet_domain')
        self.person += AttrDef(server.internet_quota_type, key='internet_quota_type')
        self.person += AttrDef(server.internet_quota_size, key='internet_quota_size')
        self.person += AttrDef(server.internet_extra_quota_size, key='internet_extra_quota_size')

        self.person += AttrDef(server.ftp_home, key='ftp_folder')
        self.person += AttrDef(server.ftp_size, key='ftp_size')

        self.query = 'username: {}'.format(
            self.user.username,
        )

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
            password = base64.b64decode(self.server.admin_password).decode('utf-8'),
            raise_exceptions = True,
            authentication = NTLM
        )
        connection.bind()

        cursor_reader = Reader(connection,self.person,self.server.search_base,query=self.query)
        cursor_reader.search()

        cursor_writer = Writer.from_cursor(cursor_reader)

        if cursor_reader.entries:

            ldap_user = cursor_writer[0]

        else:
            ldap_user = cursor_writer.new(
                dn="CN={},{}".format(
                    self.user.get_full_name(),
                    self.server.search_base
                )
            )

            ldap_user.cn = self.user.get_full_name()
            ldap_user.username = self.user.username[:20]
            ldap_user.logon = "{}@{}".format(self.user.username,self.server.domain)
            ldap_user.entry_commit_changes()
            self._reset_password(connection,ldap_user)

        if self.user.status == "active":
            self._activate_user(connection,ldap_user)
        else:
            self._deactivate_user(connection,ldap_user)

        ldap_user.first_name = self.user.first_name
        ldap_user.last_name = self.user.last_name
        ldap_user.full_name = self.user.get_full_name()

        if self.user.email:
            ldap_user.email = self.user.email
            ldap_user.email_canonical = self.user.email.strip().split("@")[0]

        if self.user.email_domain:
            ldap_user.email_domain = self.user.email_domain

        if str(self.user.email_buzon_size):
            ldap_user.email_buzon_size = self.user.email_buzon_size*1024*1024

        if str(self.user.email_message_size):
            ldap_user.email_message_size = self.user.email_message_size

        if self.user.internet_domain:
            ldap_user.internet_domain = self.user.internet_domain

        if self.user.internet_quota_type:
            ldap_user.internet_quota_type = self.user.internet_quota_type

        if str(self.user.internet_quota_size):
            ldap_user.internet_quota_size = self.user.internet_quota_size

        if str(self.user.internet_extra_quota_size):
            ldap_user.internet_extra_quota_size = self.user.internet_extra_quota_size

        if self.user.ftp_folder:
            ldap_user.ftp_folder = self.user.ftp_folder

        if str(self.user.ftp_size):
            ldap_user.ftp_size = self.user.ftp_size

        ldap_user.entry_commit_changes()

        groups = []
        for service in self.user.services.all():
            service.ldap_save()
            groups.append(
                "CN={},{}".format(
                    service.name,
                    self.server.search_base
                )
            )
        for distribution_list in self.user.distribution_list.all():
            distribution_list.ldap_save()
            groups.append(
                "CN={},{}".format(
                    distribution_list.name,
                    self.server.search_base
                )
            )
        if self.user.area:
            self.user.area.ldap_save()
            groups.append(
                "CN={},{}".format(
                    self.user.area.name,
                    self.server.search_base
                )
            )

        connection.extend.microsoft.remove_members_from_groups(ldap_user.entry_dn,ldap_user.groups.values)
        connection.extend.microsoft.add_members_to_groups(ldap_user.entry_dn,groups)


        connection.unbind()

    def _reset_password(self,connection,ldap_user):
        connection.extend.microsoft.modify_password(
            user=ldap_user.entry_dn,
            new_password=self.user._password,
            old_password=None
        )

    def _activate_user(self,connection,ldap_user):
        ldap_user.control = 512
        ldap_user.entry_commit_changes()

    def _deactivate_user(self,connection,ldap_user):
        ldap_user.control = 514
        ldap_user.entry_commit_changes()

    def delete(self):
        ldap_server = Server(
            host=self.server.server_host,
            port=self.server.server_port,
            use_ssl=self.server.start_tls,
            get_info=ALL
        )

        connection = Connection(
            server=ldap_server,
            user=self.server.admin_username,
            password=self.server.admin_password,
            raise_exceptions=True,
            authentication=NTLM
        )
        connection.bind()

        cursor_reader = Reader(connection, self.person, self.server.search_base, query=self.query)
        cursor_reader.search()
        cursor_writer = Writer.from_cursor(cursor_reader)
        if cursor_reader.entries:
            ldap_user = cursor_writer[0]
            ldap_user.entry_delete()
            ldap_user.entry_commit_changes()

        connection.unbind()

    def reset_password(self):
        ldap_server = Server(
            host=self.server.server_host,
            port=self.server.server_port,
            use_ssl=self.server.start_tls,
            get_info=ALL
        )

        connection = Connection(
            server=ldap_server,
            user=self.server.admin_username,
            password=self.server.admin_password,
            raise_exceptions=True,
            authentication=NTLM
        )
        connection.bind()

        cursor_reader = Reader(connection, self.person, self.server.search_base, query=self.query)
        cursor_reader.search()
        cursor_writer = Writer.from_cursor(cursor_reader)

        if cursor_reader.entries:
            ldap_user = cursor_writer[0]
            self._reset_password(connection,ldap_user)
            ldap_user.entry_commit_changes()

        connection.unbind()

    def authenticate(self):
        ldap_server = Server(
            host=self.server.server_host,
            port=self.server.server_port,
            use_ssl=self.server.start_tls,
            get_info=ALL
        )

        connection = Connection(
            server=ldap_server,
            user='{}\{}'.format(self.server.domain_name,self.user.username),
            password=self.user._password,
            raise_exceptions=True,
            authentication=NTLM
        )
        connection.bind()

        cursor_reader = Reader(connection, self.person, self.server.search_base, query=self.query)
        cursor_reader.search()
        connection.unbind()

class LdapGroup:
    def __init__(self,server,group):
        self.server = server
        self.group = group

        self.obj = ObjectDef(['top', 'group'])
        self.obj += AttrDef('distinguishedName', key='dn')
        self.obj += AttrDef('objectClass', key='object_class')
        self.obj += AttrDef('cn', key='cn')
        self.obj += AttrDef('mail', key='email')
        self.obj += AttrDef('extensionName', key='email_canonical')
        self.obj += AttrDef('sAMAccountName', key='slug_name')
        self.obj += AttrDef('groupType', key='type')
        self.obj += AttrDef('flags', key='flags')

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
            password = base64.b64decode(self.server.admin_password).decode('utf-8'),
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
            ldap_group.slug_name = self.group.name

        if self.group.service_type == 'security':
            ldap_group.type = -2147483646
        elif self.group.service_type == 'area':
            ldap_group.type = -2147483646
            ldap_group.flags = 25

        else:
            ldap_group.type = 2
            #ldap_group.email = self.group.email
            ldap_group.email_canonical = self.group.email.strip().split("@")[0]

        ldap_group.entry_commit_changes()

        connection.unbind()


    def delete(self):
        ldap_server = Server(
            host=self.server.server_host,
            port=self.server.server_port,
            use_ssl=self.server.start_tls,
            get_info=ALL
        )

        connection = Connection(
            server=ldap_server,
            user=self.server.admin_username,
            password=self.server.admin_password,
            raise_exceptions=True,
            authentication=NTLM
        )
        connection.bind()

        query = 'cn: {}'.format(
            self.group.name,
        )

        cursor_reader = Reader(connection, self.obj, self.server.search_base, query=query)
        cursor_reader.search()
        cursor_writer = Writer.from_cursor(cursor_reader)
        if cursor_reader.entries:
            ldap_group = cursor_writer[0]
            ldap_group.entry_delete()
            ldap_group.entry_commit_changes()

        connection.unbind()

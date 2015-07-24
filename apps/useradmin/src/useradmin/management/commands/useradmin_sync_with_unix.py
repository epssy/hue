#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from optparse import make_option

from useradmin.views import sync_unix_users_and_groups

from django.core.management.base import BaseCommand

from django.utils.translation import ugettext_lazy as _

class Command(BaseCommand):
  """
  Handler for syncing the Hue database with Unix users and groups
  """

  option_list = BaseCommand.option_list + (
      make_option("--min-uid", help=_("Minimum UID to import (Inclusive)."), default=500),
      make_option("--max-uid", help=_("Maximum UID to import (Exclusive)."), default=65334),
      make_option("--min-gid", help=_("Minimum GID to import (Inclusive)."), default=500),
      make_option("--max-gid", help=_("Maximum GID to import (Exclusive)."), default=65334),
      make_option("--check-shell", help=_("Whether or not to check that the user's shell is /bin/false."), default=True),
      make_option("--create-home", help=_("Whether or not to create user's HDFS home directory if missing."), default=False),
      make_option("--sync-password", help=_("Whether or not to import the user's hashed shadow password if unset."), default=False),
      make_option("--force-password", help=_("Import the user's hashed shadow password even if there's one set."), default=False),
      make_option("--clobber", help=_("Disable users in Hue that are not found in Unix users and groups."), default=False),
      make_option("--group", action="append", help=_("Specify groups by name (one per switch)."))
  )

  def handle(self, *args, **options):
    # Typically, system users are under 500 or 1000, depending on OS, and there
    # is usually a nobody user at the top of the ID space, so let's avoid those
    min_uid = options['min_uid']
    max_uid = options['max_uid']
    min_gid = options['min_gid']
    max_gid = options['max_gid']
    check_shell = options['check_shell']
    create_home = options['create_home']

    # As a result of no bounding on CryptPasswordHasher.verify() it is possible
    # to inject a standard Linux shadow password hash as the users password.
    # On the users first login Django will rehash the password to pbkdf2_sha256
    # or what ever is dictated by PASSWORD_HASHERS[0].

    # Linux only, requires read access to /etc/shadow, will only replace '!'.

    # WARNING: If the default hash is CryptPasswordHasher this import will lead
    # to strongly hashed passwords being re-encoded very weakly by Django.
    sync_password = options['sync_password']

    sync_password = options['force_password']
    sync_password = options['clobber']

    groups = options['group']

    sync_unix_users_and_groups(min_uid, max_uid, min_gid, max_gid, check_shell, create_home, sync_password, force_password, clobber, groups)

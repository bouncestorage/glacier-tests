import nose
from nose.tools import eq_
from nose.tools import ok_

from glaciertests.util import Util
from glaciertests.util import GlacierTestsConfig


def test_vault_list_all():
    conn = GlacierTestsConfig().connection()
    result = conn.list_vaults()
    ok_('RequestId' in result)
    ok_('VaultList' in result)
    ok_('Marker' in result)
    eq_(len(result['VaultList']), 0)
    eq_(result['Marker'], None)


def test_vault_create():
    conn = GlacierTestsConfig().connection()
    vault = Util.get_new_vault()
    ok_('Location' in vault)
    ok_('RequestId' in vault)
    vault_name = vault['Location'].split('/')[-1]
    _check_in_listing([vault_name])


def test_vault_delete():
    conn = GlacierTestsConfig().connection()
    vault = Util.get_new_vault()
    ok_('Location' in vault)
    ok_('RequestId' in vault)
    vault_name = vault['Location'].split('/')[-1]
    _check_in_listing([vault_name])
    conn.delete_vault(vault_name)
    _check_not_in_listing([vault_name])


def test_archive_create():
    conn = GlacierTestsConfig().connection()
    vault = Util.get_new_vault()
    vault_name = vault['Location'].split('/')[-1]
    archive = Util.upload_archive(vault_name, b"hello", None)
    print(archive)
    ok_('ArchiveId' in archive)


def test_archive_delete():
    conn = GlacierTestsConfig().connection()
    vault = Util.get_new_vault()
    vault_name = vault['Location'].split('/')[-1]
    archive = Util.upload_archive(vault_name, b"hello", None)
    ok_('ArchiveId' in archive)
    archive_id = archive['ArchiveId']
    conn.delete_archive(vault_name, archive_id)


def _get_vault_names():
    conn = GlacierTestsConfig().connection()
    result = conn.list_vaults()
    return [x['VaultName'] for x in result['VaultList']]


def _check_not_in_listing(names):
    vault_names = _get_vault_names()
    eq_(len(set(vault_names).intersection(set(names))), 0)


def _check_in_listing(expected_names):
    vault_names = _get_vault_names()
    ok_(set(vault_names).issuperset(set(expected_names)))

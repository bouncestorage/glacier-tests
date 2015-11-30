from boto.glacier.exceptions import UnexpectedHTTPResponseError as GlacierError
import json
import nose
from nose.tools import eq_
from nose.tools import ok_

import dateutil.parser

from glaciertests.util import Util
from glaciertests.util import GlacierTestsConfig


def test_vault_list_all():
    conn = GlacierTestsConfig().connection()
    result = conn.list_vaults()
    ok_('RequestId' in result)
    ok_('VaultList' in result)
    ok_('Marker' in result)


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


def test_vault_describe_does_not_exist():
    conn = GlacierTestsConfig().connection()
    try:
        conn.describe_vault(GlacierTestsConfig().prefix() + '-doesnotexist')
    except GlacierError as e:
        eq_(e.code, 'ResourceNotFoundException')
        body = json.loads(e.body)
        eq_(body['type'], 'client')


def test_archive_create():
    conn = GlacierTestsConfig().connection()
    vault = Util.get_new_vault()
    vault_name = vault['Location'].split('/')[-1]
    archive = Util.upload_archive(vault_name, b"hello", None)
    ok_('ArchiveId' in archive)


def test_archive_delete():
    conn = GlacierTestsConfig().connection()
    vault = Util.get_new_vault()
    vault_name = vault['Location'].split('/')[-1]
    archive = Util.upload_archive(vault_name, b"hello", None)
    ok_('ArchiveId' in archive)
    archive_id = archive['ArchiveId']
    conn.delete_archive(vault_name, archive_id)


def test_create_inventory_job():
    vault = Util.get_new_vault()
    vault_name = vault['Location'].split('/')[-1]
    description = "test archive"
    conn = GlacierTestsConfig().connection()
    job_data = {'Type': 'inventory-retrieval'}
    job = conn.initiate_job(vault_name, job_data)
    ok_('JobId' in job)
    description = conn.describe_job(vault_name, job['JobId'])
    date = dateutil.parser.parse(description['CompletionDate'])
    date = dateutil.parser.parse(description['CreationDate'])
    eq_(description['StatusCode'], 'Succeeded')
    eq_(description['Action'], 'inventory-retrieval')


def test_create_archive_retrieval_job():
    vault = Util.get_new_vault()
    vault_name = vault['Location'].split('/')[-1]
    description = "test archive"
    archive = _setup_test_archive(vault_name, description)
    conn = GlacierTestsConfig().connection()
    job_data = {'Type': 'archive-retrieval',
                'ArchiveId': archive}
    job = conn.initiate_job(vault_name, job_data)
    ok_('JobId' in job)
    description = conn.describe_job(vault_name, job['JobId'])
    date = dateutil.parser.parse(description['CompletionDate'])
    date = dateutil.parser.parse(description['CreationDate'])
    eq_(description['RetrievalByteRange'], '0-4')
    eq_(description['StatusCode'], 'Succeeded')
    eq_(description['Completed'], True)
    eq_(description['ArchiveId'], archive)
    eq_(description['Action'], 'archive-retrieval')


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


def _setup_test_archive(vault, description=None):
    archive = Util.upload_archive(vault, b"hello", None)
    ok_('ArchiveId' in archive)
    return archive['ArchiveId']

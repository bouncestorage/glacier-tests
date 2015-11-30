from glaciertests.util import GlacierTestsConfig
import time


def purge_prefix_vaults():
    conn = GlacierTestsConfig().connection()
    all_vaults = conn.list_vaults()
    jobs = {}
    for vault in all_vaults['VaultList']:
        if vault['VaultName'].startswith(GlacierTestsConfig().prefix()):
            # Try to delete and only schedule an inventory job if delete fails
            try:
                print 'delete vault %s' % vault['VaultName']
                conn.delete_vault(vault['VaultName'])
            except Exception as e:
                print 'delete failed %s' % str(e)
                jobs[vault['VaultName']] = enumerate_vault(vault['VaultName'],
                                                           conn)
    while jobs:
        remaining = {}
        while jobs:
            vault, job_id = jobs.popitem()
            status = conn.describe_job(vault, job_id)
            if status['Completed'] == 'false':
                print 'Waiting for: %s' % job_id
                remaining[vault] = job_id
                continue
            resp = None
            try:
                resp = conn.get_job_output(vault, job_id)
            except Exception as e:
                print "Error: %s" % str(e)
                remaining[vault] = job_id
                continue
            for archive in resp['ArchiveList']:
                conn.delete_archive(vault, archive['ArchiveId'])
        jobs = remaining
        if jobs:
            time.sleep(10)


def enumerate_vault(vault, conn):
    job_data = {'Type': 'inventory-retrieval'}
    result = conn.initiate_job(vault, job_data)
    return result['JobId']


_multiprocess_shared_ = True


def setup():
    purge_prefix_vaults()


def teardown():
    purge_prefix_vaults()

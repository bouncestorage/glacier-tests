from glaciertests.util import GlacierTestsConfig

def purge_prefix_vaults():
    conn = GlacierTestsConfig().connection()
    all_vaults = conn.list_vaults()
    for vault in all_vaults['VaultList']:
        if vault['VaultName'].startswith(GlacierTestsConfig().prefix()):
            conn.delete_vault(vault['VaultName'])

def setup():
    purge_prefix_vaults()

def teardown():
    purge_prefix_vaults()

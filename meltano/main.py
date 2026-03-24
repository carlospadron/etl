import os
import subprocess
import sys
import textwrap
from pathlib import Path

ORIGIN_USER = os.environ['ORIGIN_USER']
ORIGIN_PASS = os.environ['ORIGIN_PASS']
ORIGIN_DB = os.environ['ORIGIN_DB']
ORIGIN_ADDRESS = os.environ['ORIGIN_ADDRESS']
ORIGIN_PORT = os.getenv('ORIGIN_PORT', '5432')

TARGET_USER = os.environ['TARGET_USER']
TARGET_PASS = os.environ['TARGET_PASS']
TARGET_DB = os.environ['TARGET_DB']
TARGET_ADDRESS = os.environ['TARGET_ADDRESS']
TARGET_PORT = os.getenv('TARGET_PORT', '5432')

SOURCE_TABLE = os.getenv('SOURCE_TABLE', 'os_open_uprn')

WORK_DIR = Path('/tmp/meltano_project')
WORK_DIR.mkdir(parents=True, exist_ok=True)

# Stream name that tap-postgres produces for a table in the public schema:
# schema + "-" + table  →  e.g. "public-os_open_uprn_2m"
source_stream = f"public-{SOURCE_TABLE}"

meltano_yml = textwrap.dedent(f"""\
default_environment: prod
project_id: etl-benchmark

environments:
  - name: prod

plugins:
  extractors:
    - name: tap-postgres
      variant: meltanolabs
      pip_url: git+https://github.com/MeltanoLabs/tap-postgres.git
      config:
        host: {ORIGIN_ADDRESS}
        port: {ORIGIN_PORT}
        user: {ORIGIN_USER}
        password: {ORIGIN_PASS}
        database: {ORIGIN_DB}
        filter_schemas:
          - public
        default_replication_method: FULL_TABLE
        stream_maps:
          "{source_stream}":
            __alias__: os_open_uprn
      select:
        - "{source_stream}.*"

  loaders:
    - name: target-postgres
      variant: meltanolabs
      pip_url: git+https://github.com/MeltanoLabs/target-postgres.git
      config:
        host: {TARGET_ADDRESS}
        port: {TARGET_PORT}
        user: {TARGET_USER}
        password: {TARGET_PASS}
        database: {TARGET_DB}
        default_target_schema: public
        hard_delete: true
        add_record_metadata: false
        activate_version: false
""")

(WORK_DIR / 'meltano.yml').write_text(meltano_yml)

env = {**os.environ, 'MELTANO_PROJECT_ROOT': str(WORK_DIR)}

# Install plugins
print('Installing Meltano plugins...', flush=True)
r = subprocess.run(['meltano', 'install'], cwd=WORK_DIR, env=env)
if r.returncode != 0:
    sys.exit(r.returncode)

# Run EL — stream_maps renames to os_open_uprn, so no post-rename needed
print(f'Running meltano el: {source_stream} -> public.os_open_uprn', flush=True)
r = subprocess.run(
    ['meltano', 'el', 'tap-postgres', 'target-postgres'],
    cwd=WORK_DIR, env=env,
)

sys.exit(r.returncode)

import os
import subprocess
import sys

source_table = os.getenv('SOURCE_TABLE', 'os_open_uprn')

print(os.getenv('SOURCEDB', ''))
print(os.getenv('TARGETDB', ''))

env = {**os.environ, 'SLING_THREADS': os.getenv('SLING_THREADS', '3')}

result = subprocess.run(
    [
        'sling', 'run',
        '--src-conn', 'SOURCEDB',
        '--src-stream', f'public.{source_table}',
        '--tgt-conn', 'TARGETDB',
        '--tgt-object', 'public.os_open_uprn',
        '--mode', 'full-refresh',
    ],
    env=env,
)
sys.exit(result.returncode)

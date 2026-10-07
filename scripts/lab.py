#!/usr/bin/env python3
"""Start and install a fresh local WordPress lab without exposing passwords."""

import argparse
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXEC_ENV = {key: value for key, value in os.environ.items()
            if not key.startswith(('COMPOSE_', 'WORDPRESS_', 'WP_', 'DB_', 'ADMINER_'))}


def run(command, **kwargs):
    return subprocess.run(command, cwd=ROOT, env=EXEC_ENV, check=True, **kwargs)


def write_private(path, text):
    # Exclusive creation: never overwrite credentials from an earlier run.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        stream.write(text)


def save_private(path, value):
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def finish_setup(cli, credentials_path, credentials):
    run(cli + ['option', 'update', 'blog_public', '0'])
    run(cli + ['option', 'update', 'timezone_string', 'Europe/Berlin'])
    run(cli + ['core', 'is-installed'])
    for option, expected in (('blog_public', '0'), ('timezone_string', 'Europe/Berlin'),
                             ('home', credentials['url'])):
        actual = run(cli + ['option', 'get', option], capture_output=True, text=True).stdout.strip()
        if actual != expected:
            raise RuntimeError(f'Final verification failed for {option}.')
    credentials['setup_complete'] = True
    save_private(credentials_path, credentials)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, help='Unique Compose project name')
    parser.add_argument('--wp-port', type=int, default=8080)
    parser.add_argument('--adminer-port', type=int, default=8088)
    parser.add_argument('--title', default='Local WordPress')
    parser.add_argument('--admin-user', default='local-admin')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', args.project):
        parser.error('Project name must use lowercase letters, digits, hyphens or underscores.')
    if not re.fullmatch(r'[a-zA-Z0-9_-]+', args.admin_user):
        parser.error('Admin user must use letters, digits, hyphens or underscores.')
    if not all(1024 <= p <= 65535 for p in (args.wp_port, args.adminer_port)):
        parser.error('Ports must be between 1024 and 65535.')
    if args.wp_port == args.adminer_port:
        parser.error('WordPress and Adminer ports must differ.')

    if os.environ.get('DOCKER_HOST') and os.environ.get('DOCKER_CONTEXT'):
        parser.error('Set either DOCKER_HOST or DOCKER_CONTEXT, not both.')
    context = run(['docker', 'context', 'show'], capture_output=True, text=True).stdout.strip()
    endpoint = os.environ.get('DOCKER_HOST') or run(
        ['docker', 'context', 'inspect', context, '--format', '{{.Endpoints.docker.Host}}'],
        capture_output=True, text=True).stdout.strip()
    if not endpoint.startswith(('unix://', 'npipe://')):
        parser.error('This installer only supports a local Docker daemon, not a remote endpoint.')
    daemon = run(['docker', 'info', '--format', '{{.ID}}'],
                 capture_output=True, text=True).stdout.strip()
    local = ROOT / '.local'
    if local.is_symlink() or (ROOT / '.env').is_symlink():
        parser.error('Local configuration must not be a symlink.')
    local.mkdir(mode=0o700, exist_ok=True)
    identity_path = local / 'project.json'
    identity = {'project': args.project, 'wp_port': args.wp_port,
                'adminer_port': args.adminer_port, 'root': str(ROOT), 'daemon': daemon}
    containers = run(['docker', 'container', 'ls', '-aq', '--filter',
                      f'label=com.docker.compose.project={args.project}'],
                     capture_output=True, text=True).stdout.split()
    for container in containers:
        owner = run(['docker', 'inspect', '--format',
                     '{{index .Config.Labels "com.docker.compose.project.working_dir"}}', container],
                    capture_output=True, text=True).stdout.strip()
        if owner != str(ROOT):
            parser.error('Compose resources belong to another checkout. Choose a new project name.')
    if identity_path.exists():
        if json.loads(identity_path.read_text()) != identity:
            parser.error('This directory already belongs to another project or port configuration.')
    else:
        # Protect other Compose resources even when called from a fresh checkout.
        for kind in ('container', 'volume', 'network'):
            existing = run(['docker', kind, 'ls', '-q', '--filter',
                            f'label=com.docker.compose.project={args.project}'],
                           capture_output=True, text=True).stdout.strip()
            if existing:
                parser.error('Compose project name already has resources. Choose a new name.')
        write_private(identity_path, json.dumps(identity, indent=2) + '\n')

    env_path = ROOT / '.env'
    if not env_path.exists():
        content = (ROOT / '.env.sample').read_text()
        values = {'WP_PORT': str(args.wp_port), 'ADMINER_PORT': str(args.adminer_port),
                  'DB_PASSWORD': secrets.token_hex(24),
                  'DB_ROOT_PASSWORD': secrets.token_hex(24)}
        for key, value in values.items():
            content = re.sub(rf'^{key}=.*$', f'{key}={value}', content, flags=re.MULTILINE)
        write_private(env_path, content)
    else:
        entries = dict(line.split('=', 1) for line in env_path.read_text().splitlines()
                       if '=' in line and not line.lstrip().startswith('#'))
        for key, value in (('WP_PORT', args.wp_port), ('ADMINER_PORT', args.adminer_port)):
            if entries.get(key) != str(value):
                parser.error(f'Existing .env has a different {key}; no credentials were overwritten.')

    compose = ['docker', 'compose', '--env-file', '.env', '-p', args.project, '-f', 'docker-compose.yml',
               '-f', 'compose.lab.yml']
    run(compose + ['config', '--quiet'])
    run(compose + ['up', '-d', '--wait', '--wait-timeout', '120'])
    cli = compose + ['run', '--rm', '-T', '--no-deps', 'cli',
                     '--skip-plugins', '--skip-themes']
    credentials_path = local / 'wordpress-admin.json'
    installed = subprocess.run(cli + ['core', 'is-installed'], cwd=ROOT, env=EXEC_ENV,
                               capture_output=True, text=True)
    if installed.returncode == 0:
        if credentials_path.exists():
            credentials = json.loads(credentials_path.read_text())
            if not credentials.get('setup_complete', True):
                expected_url = f'http://127.0.0.1:{args.wp_port}'
                if credentials['url'] != expected_url or credentials['user'] != args.admin_user:
                    raise RuntimeError('Saved credentials belong to another setup.')
                actual_url = run(cli + ['option', 'get', 'home'],
                                 capture_output=True, text=True).stdout.strip()
                if actual_url != expected_url:
                    raise RuntimeError('Installed site URL differs; refusing pending setup changes.')
                run(cli + ['user', 'get', credentials['user'], '--field=ID'], capture_output=True)
                finish_setup(cli, credentials_path, credentials)
                print('Pending local installation settings completed and verified.')
                return
        print('WordPress is already installed. Existing users, data and settings are preserved.')
        return
    # is-installed returns 1 for an uninstalled DB, but can also fail for other reasons.
    # Check the database separately; refuse any partially populated installation.
    run(cli + ['db', 'check'])
    tables = run(cli + ['db', 'query', 'SHOW TABLES', '--skip-column-names'],
                 capture_output=True, text=True).stdout.strip()
    if tables:
        raise RuntimeError('Database is not empty. Refusing to install over existing tables.')

    url = f'http://127.0.0.1:{args.wp_port}'
    if credentials_path.exists():
        credentials = json.loads(credentials_path.read_text())
        if credentials['url'] != url or credentials['user'] != args.admin_user:
            raise RuntimeError('Saved installation credentials belong to a different setup.')
    else:
        credentials = {'url': url, 'user': args.admin_user,
                       'email': 'admin@example.invalid', 'password': secrets.token_urlsafe(32),
                       'setup_complete': False}
        write_private(credentials_path, json.dumps(credentials, indent=2) + '\n')
    credentials['setup_complete'] = False
    save_private(credentials_path, credentials)
    run(cli + ['core', 'install', f'--url={url}', f'--title={args.title}',
               f'--admin_user={credentials["user"]}',
               f'--admin_email={credentials["email"]}', '--skip-email',
               '--prompt=admin_password'], input=credentials['password'] + '\n', text=True,
        capture_output=True)  # WP-CLI echoes prompted values, including passwords.
    finish_setup(cli, credentials_path, credentials)
    print(f'WordPress installed: {url}')
    print(f'Local admin credentials: {credentials_path} (private, ignored, outside webroot)')
    print('Offline installation uses English; language downloads are a separate step.')


if __name__ == '__main__':
    try:
        main()
    except (subprocess.CalledProcessError, RuntimeError, OSError, ValueError) as error:
        # Never dump subprocess arguments, environment or credential contents.
        if isinstance(error, subprocess.CalledProcessError):
            print(f'Local setup command failed (exit {error.returncode}).', file=sys.stderr)
        else:
            print(f'Local setup failed: {error}', file=sys.stderr)
        sys.exit(1)

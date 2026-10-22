#!/usr/bin/env python3
"""Cortez Voz: source installation; never starts the application or migrates data."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import tempfile
from distribution import download, extract, digest

ROOT = Path(__file__).resolve().parents[1]

def target_platform(system=None, machine=None):
    system = system or platform.system(); machine = (machine or platform.machine()).lower()
    machine = {'amd64': 'x86_64', 'aarch64': 'arm64'}.get(machine, machine)
    key = f'{system}-{machine}'
    if key not in ('Darwin-arm64', 'Windows-x86_64', 'Linux-x86_64'):
        raise ValueError('Plataforma ainda não suportada: '+key+'. Esta versão atende Mac Apple Silicon, Windows x64 e Linux x64 com glibc.')
    return key

def environment(root=ROOT):
    # Dependency build processes do not receive provider credentials from this shell.
    keep = ('PATH','SystemRoot','SYSTEMROOT','COMSPEC','PATHEXT','WINDIR','TEMP','TMP','TMPDIR','LANG','LC_ALL')
    env = {k:v for k,v in os.environ.items() if k in keep}
    local = root / '.cortez'
    env.update(HOME=str(local/'home'), USERPROFILE=str(local/'home'),
               APPDATA=str(local/'home'/'AppData'/'Roaming'), LOCALAPPDATA=str(local/'home'/'AppData'/'Local'),
               UV_CACHE_DIR=str(local/'uv-cache'), BUN_INSTALL_CACHE_DIR=str(local/'bun-cache'),
               UV_PYTHON_DOWNLOADS='never', UV_NO_CONFIG='1', PIP_CONFIG_FILE=os.devnull,
               HF_HUB_DISABLE_TELEMETRY='1', DO_NOT_TRACK='1', ELECTRON_SKIP_BINARY_DOWNLOAD='1')
    return env

def run(argv, cwd, env, timeout=1800):
    with subprocess.Popen([str(x) for x in argv], cwd=cwd, env=env,
                          start_new_session=os.name != 'nt') as proc:
        try: code = proc.wait(timeout=timeout)
        except BaseException:
            if os.name == 'nt': subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True,timeout=15)
            else: os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(); raise
    if code: raise ValueError('Etapa de instalação falhou; preserve o log e corrija a causa antes de repetir.')

def prepare(root=ROOT, apply=False):
    root = Path(root).resolve(); key = target_platform()
    if sys.version_info[:2] not in ((3,11),(3,12)):
        raise ValueError('Use Python 3.11 ou 3.12 para este runtime de voz.')
    specs = json.loads((root/'cortez/tools.lock.json').read_text())['platforms'][key]
    receipt = root/'.cortez/installed.json'
    locks = {name:digest(root/name) for name in ('uv.lock','bun.lock','pyproject.toml','cortez/tools.lock.json')}
    py = root/'.venv'/('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if receipt.is_file():
        previous = json.loads(receipt.read_text())
        if previous.get('locks') != locks: raise ValueError('Fontes alteradas; prepare uma revisão nova, preservando a anterior.')
        if py.is_file() and (root/'frontend/dist/index.html').is_file():
            return {**previous, 'status':'already_installed'}
        raise ValueError('Instalação incompleta; reparo precisa de uma ação explícita em nova pasta.')
    result = {'ok':True, 'status':'preview', 'platform':key, 'locks':locks,
              'downloads':['uv e Bun fixados por hash','dependências de uv.lock e bun.lock'],
              'database_started':False,'models_downloaded':False,'speech_tested':False,
              'interface':'navegador local, http://127.0.0.1:3930',
              'data_policy':'dados separados do código; primeiro início exige consentimento explícito'}
    if not apply: return result
    local = root/'.cortez'; local.mkdir(exist_ok=True)
    lockfile = local/'install.lock'
    with lockfile.open('x'):
        try:
            env = environment(root)
            Path(env['HOME']).mkdir(parents=True,exist_ok=True)
            binaries = {}
            for name,spec in specs.items():
                target = local/(name+('.exe' if os.name == 'nt' else ''))
                # A previous interrupted install never substitutes an unchecked executable.
                with tempfile.TemporaryDirectory(dir=local) as td:
                    tmp = Path(td); archive = tmp/'download'
                    download(spec,archive); extract(archive,tmp/'unpacked')
                    candidates = [p for p in (tmp/'unpacked').rglob(target.name) if p.is_file()]
                    if len(candidates)!=1: raise ValueError('Executável ausente ou ambíguo no pacote.')
                    os.replace(candidates[0],target); target.chmod(0o755)
                binaries[name] = target
            env['PATH'] = str(local)+os.pathsep+env.get('PATH','')
            # No project build/import is needed; backend/main.py sets its source paths.
            command = [binaries['uv'],'sync','--locked','--no-dev','--no-install-project',
                       '--no-group','cuda','--python',sys.executable,'--no-python-downloads']
            if key != 'Darwin-arm64': command += ['--group','cpu']
            run(command,root,env)
            run([binaries['bun'],'install','--frozen-lockfile','--ignore-scripts'],root,env)
            # Direct Vite invocation bypasses predev/setup/database hooks.
            run([binaries['bun'],'--bun',root/'electron/node_modules/vite/bin/vite.js',
                 'build','--config','vite.web.config.ts'],root/'electron',env)
            if not py.is_file() or not (root/'frontend/dist/index.html').is_file():
                raise ValueError('Instalação não produziu Python e interface esperados.')
            result.update(status='installed',tools={name:digest(p) for name,p in binaries.items()})
            receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        finally: lockfile.unlink(missing_ok=True)
    return result

def start(data_dir, initialize_data=False):
    if not initialize_data:
        raise ValueError('O primeiro início cria/atualiza o banco local do aplicativo. Autorize --initialize-data para o diretório escolhido.')
    if not (ROOT/'.cortez/installed.json').is_file(): raise ValueError('Prepare o aplicativo primeiro.')
    data = Path(data_dir).resolve()
    if data == ROOT or data.is_relative_to(ROOT): raise ValueError('Dados devem ficar fora da pasta versionada do aplicativo.')
    data.mkdir(parents=True,exist_ok=True)
    env = environment(ROOT)
    env.update(OMNIVOICE_DATA_DIR=str(data), OMNIVOICE_CACHE_DIR=str(data/'models'),
               HF_HOME=str(data/'models'), OMNIVOICE_BIND_HOST='127.0.0.1', OMNIVOICE_PORT='3930',
               VOICESTUDIO_DISABLE_UPDATER='1', OMNIVOICE_MCP_DISABLE='1',
               OMNIVOICE_PUBLIC_API_BASE='http://127.0.0.1:3930', CORTEZ_VOZ='1')
    py = ROOT/'.venv'/('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    print('Cortez Voz: http://127.0.0.1:3930 — dados em '+str(data),flush=True)
    run([py,'-m','uvicorn','main:app','--app-dir','backend','--host','127.0.0.1','--port','3930'],ROOT,env,86400)

if __name__ == '__main__':
    def interrupted(signum, frame):
        raise KeyboardInterrupt('Instalação interrompida')
    signal.signal(signal.SIGTERM, interrupted)
    p = argparse.ArgumentParser(); p.add_argument('--apply',action='store_true')
    p.add_argument('--start',action='store_true'); p.add_argument('--data-dir',type=Path)
    p.add_argument('--initialize-data',action='store_true'); args=p.parse_args()
    try:
        if args.start:
            if not args.data_dir: raise ValueError('Informe o diretório de dados.')
            start(args.data_dir,args.initialize_data)
        else: print(json.dumps(prepare(apply=args.apply),ensure_ascii=False,indent=2))
    except (ValueError,OSError,subprocess.SubprocessError) as exc:
        print(json.dumps({'ok':False,'error':str(exc)},ensure_ascii=False));sys.exit(1)

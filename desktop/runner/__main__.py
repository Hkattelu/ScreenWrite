"""
Pipeline runner - executed as a child process by the desktop server.

    python -m desktop.runner --config <run_dir>/run_config.json
    python -m desktop.runner --probe-resolve

Running the pipeline out-of-process means the UI can cancel with a process
terminate, a pipeline crash never takes the window down, and heavyweight
native libraries (ctranslate2, fusionscript) never load into the UI process.

run_config.json (written by the server, NO secrets - this process loads the
repo .env itself):
    {"run_id": ..., "repo_root": ..., "script_path": ..., "output_path": ...,
     "skip_fetch": bool, "orchestrator": {<VideoOrchestrator kwargs>}}

Exit codes: 0 = success, 3 = pipeline reported failure, 1 = crash.
"""

import argparse
import json
import os
import sys
import traceback
from pathlib import Path


def _atomic_write_json(path: Path, payload: dict) -> None:
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(payload, indent=2, default=str), encoding='utf-8')
    os.replace(tmp, path)


def probe_resolve() -> int:
    """Print one-line JSON describing Resolve availability. Always exits 0."""
    try:
        from screenwrite.resolve_integration import ResolveIntegration
        integration = ResolveIntegration()  # raises when Resolve isn't running
        info = integration.get_resolve_info()
        info['ok'] = bool(info.get('connected') and info.get('project_available'))
        print(json.dumps(info))
    except Exception as e:  # noqa: BLE001 - the whole point is a safe probe
        print(json.dumps({'ok': False, 'error': str(e)}))
    return 0


def run_pipeline(config_path: str) -> int:
    config = json.loads(Path(config_path).read_text(encoding='utf-8'))
    run_dir = Path(config_path).resolve().parent
    repo_root = Path(config['repo_root'])

    # Run from the repo so relative paths and .env behave like the CLI.
    os.chdir(repo_root)
    try:
        from dotenv import load_dotenv
        load_dotenv(repo_root / '.env')
    except ImportError:
        pass

    from desktop.runner.events import EventWriter, install_handlers, remove_handlers

    writer = EventWriter(run_dir / 'events.jsonl')
    handlers = install_handlers(writer, run_dir / 'run.log')

    redacted = dict(config)
    redacted['orchestrator'] = {
        k: v for k, v in config['orchestrator'].items() if 'key' not in k.lower()
    }
    writer.emit('run_started', run_id=config.get('run_id'), pid=os.getpid(),
                config=redacted)

    try:
        from screenwrite.orchestrator import VideoOrchestrator

        orchestrator_config = dict(config['orchestrator'])
        orchestrator_config['pexels_api_key'] = os.getenv('PEXELS_API_KEY')

        with VideoOrchestrator(**orchestrator_config) as orchestrator:
            result = orchestrator.orchestrate(
                script_path=config['script_path'],
                output_path=config['output_path'],
                skip_fetch=config.get('skip_fetch', False),
            )

        _atomic_write_json(run_dir / 'result.json', result)
        writer.emit('result', success=bool(result.get('success')),
                    workflow_result=result)
        return 0 if result.get('success') else 3
    except Exception as e:  # noqa: BLE001 - report, then die with code 1
        writer.emit('fatal', error=str(e), traceback=traceback.format_exc())
        return 1
    finally:
        remove_handlers(handlers)
        writer.close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog='desktop.runner')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--config', help='Path to run_config.json')
    group.add_argument('--probe-resolve', action='store_true',
                       help='Print Resolve availability as JSON and exit')
    args = parser.parse_args(argv)

    if args.probe_resolve:
        return probe_resolve()
    return run_pipeline(args.config)


if __name__ == '__main__':
    sys.exit(main())

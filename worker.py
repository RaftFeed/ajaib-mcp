"""One UIA/COM thread per request, with a cross-chat process lock."""
import json
import msvcrt
import os
from pathlib import Path
import sys
import tempfile


def main():
    if os.environ.get('AJAIB_ENABLE_LIVE_ACCESS') != '1':
        print(json.dumps({'error': 'Live access is disabled. Review LEGAL.md before enabling AJAIB_ENABLE_LIVE_ACCESS=1.'}))
        return
    # Contains only a lock byte, never account data.
    lock_path = Path(tempfile.gettempdir()) / 'codex-ajaib-readonly.lock'
    with lock_path.open('a+b') as lock:
        if lock.tell() == 0:
            lock.write(b'0')
            lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            print(json.dumps({'error': 'Another Ajaib read is in progress. Retry shortly.'}))
            return
        try:
            from terminal import Terminal
            request = json.loads(sys.stdin.read(1024))
            answer = Terminal().run(request['action'], request.get('symbol'))
            print(json.dumps(answer, ensure_ascii=True))
        except Exception:
            # Do not disclose exception text: UIA errors may contain account text.
            print(json.dumps({'error': 'Ajaib read failed. Keep the terminal open, restored and logged in; close dialogs and retry. If searching a symbol, bring the terminal to the foreground. No trading action was requested.'}))
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


if __name__ == '__main__':
    main()

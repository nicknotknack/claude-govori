"""Keeps Piper voices in memory: a reply starts in ~0.1 s instead of the ~1.5 s a fresh `piper` needs to load its model.

Started by bin/govori only once voice mode is on; exits after <idle seconds> without requests.
Usage: python govori-server.py <state dir> <idle seconds> [model.onnx ...]
Request: "<model>\n<length scale>\n<text>\0", or "quit\0". Answer: "ok\n" once playback has started, else "err\n".
"""
import fcntl
import os
import socket
import subprocess
import sys
import wave

SOCK, WAV, LOCK = "piper.sock", "piper.wav", "piper.lock"  # relative: socket paths are limited to 104 bytes
voices = {}
player = None


def voice(model):
    from piper import PiperVoice

    if model not in voices:
        voices[model] = PiperVoice.load(model)
    return voices[model]


def speak(model, scale, text):
    global player
    from piper.config import SynthesisConfig

    v, cfg = voice(model), SynthesisConfig(length_scale=float(scale))
    if player:  # a newer reply cuts off the previous one
        player.terminate()
        player.wait()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    with wave.open(WAV, "wb") as w:
        for i, line in enumerate(lines):  # line by line, like the piper CLI
            v.synthesize_wav(line, w, syn_config=cfg, set_wav_format=i == 0)
    player = subprocess.Popen(["afplay", WAV], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def read_request(conn):
    buf = b""
    while not buf.endswith(b"\0"):
        chunk = conn.recv(65536)
        if not chunk:
            break
        buf += chunk
    return buf.rstrip(b"\0").decode()


def serve(sock, idle, preload):
    while True:
        sock.settimeout(0 if preload else idle)
        try:
            conn, _ = sock.accept()
        except (socket.timeout, BlockingIOError):
            if not preload:
                return
            try:  # one at a time, so a waiting request goes first and needs at most one load to finish
                voice(preload.pop(0))
            except Exception:
                pass  # retried, and reported, on the first request that needs it
            continue
        with conn:
            conn.settimeout(5)
            answer = b"ok\n"
            try:
                request = read_request(conn)
                if request == "quit":
                    conn.sendall(answer)
                    return
                speak(*request.split("\n", 2))
            except Exception:
                answer = b"err\n"  # the client falls back to a one-shot piper
            try:
                conn.sendall(answer)
            except OSError:
                pass


def main():
    state_dir, idle, models = sys.argv[1], float(sys.argv[2]), sys.argv[3:]
    os.chdir(state_dir)
    os.umask(0o077)
    lock = open(LOCK, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return  # already running
    try:
        os.setsid()  # outlive the hook or command that started us
    except OSError:
        pass
    try:
        os.unlink(SOCK)  # left by a crash
    except OSError:
        pass
    sock = socket.socket(socket.AF_UNIX)
    sock.bind(SOCK)
    sock.listen(8)  # bound before loading, so early requests wait here instead of loading a second copy
    try:
        serve(sock, idle, models)
    finally:
        for path in (SOCK, WAV):
            try:
                os.unlink(path)
            except OSError:
                pass


if __name__ == "__main__":
    main()

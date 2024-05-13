"""
Interface with the `xcall` application from https://github.com/martinfinke/xcall.

`xcall` allows for translating the callbacks from the x-callback-url protocol to stdout/stderr.
This protocol is used to get replies from https://github.com/czottmann/obsidian-actions-uri.
"""
import json
import os
import os.path as op
import shutil
from subprocess import run
from urllib.parse import quote


def xcall_binary() -> str:
    """
    Find the `xcall` binary.

    In order the following are checked:
    - `xcall` binary in PATH.
    - `/Applications/xcall.app/Contents/MacOS/xcall`
    - `$HOME/Applications/xcall.app/Contents/MacOS/xcall`
    """
    path = shutil.which("xcall")
    if path is not None:
        return str(path)

    for path in [
        "/Applications/xcall.app/Contents/MacOS/xcall",
        op.expanduser("~/Applications/xcall.app/Contents/MacOS/xcall")
    ]:
        if op.exists(path):
            if not (op.isfile(path) and os.access(path, os.X_OK)):
                raise IOError("$path does not appear to be an executable file")
            return path

    raise FileNotFoundError("Did not find the `xcall` binary. Has `xcall.app` been installed from https://github.com/martinfinke/xcall.")


def update_key(key, value):
    """
    Update python keyword argument name to URL key->value pair.

    Replaces "_" with "-" in `key`.
    Replace python True/False in `value` with true/false strings.
    Quote any reserved characters in the `value`.
    """
    new_key = key.replace("-", "_")
    new_value = str(value).lower() if isinstance(value, bool) else value
    return new_key + "=" + quote(new_value)

def build_url(app_name: str, *actions: str, **keywords: str) -> str:
    """
    Build the URL used to call a specific application.

    The resulting URL will look something like:
    `app_name://action/action/action?key=value?key=value`
    """
    short_app_name = app_name.removesuffix(".app")
    if len(actions) == 0:
        if len(keywords) > 0:
            raise ValueError("Cannot construct an URL with no actions, yet with keywords.")
        return short_app_name

    action_string = "/".join([quote(a) for a in actions])
    keyword_string = "&".join(update_key(key, value) for (key, value) in keywords.items())
    if len(keywords) > 0:
        keyword_string = "?" + keyword_string

    return f"{short_app_name}://{action_string}{keyword_string}"


def xcall_raw(app_name: str, *actions: str, **keywords: str) -> str:
    """
    Call an application using the `x-callback-url` protocol.

    If there is an `x-error` reply, an error is raised with the message.
    Otherwise, the `x-succes` reply is returned as a string.
    Use :func:`xcall` to parse the reply as a JSON object.

    The URL can be defined based on the `app_name` and `actions`/`keywords`
    as described in :func:`build_url` or by supplying the URL directly as a string.
    """
    binary = xcall_binary()
    if ":/" in app_name:
        if len(actions) > 0 or len(keywords) > 0:
            raise ValueError(f"Cannot set actions/keywords when supplying the full URL {app_name}")
        url = app_name
    else:
        url = build_url(app_name, *actions, **keywords)

    proc = run([binary, "-url", url], capture_output=True)
    if len(proc.stderr) > 0:
        err = try_json_parse(proc.stderr.decode())
        raise ChildProcessError(f"{url} returned an error message: {err['errorMessage']}")
    return proc.stdout.decode()


def try_json_parse(input_string: str):
    """
    Try parsing the input string if it looks like a JSON.

    Otherwise, the input string is returned.
    """
    if not isinstance(input_string, str):
        return input_string
    stripped = input_string.strip()
    if len(stripped) == 0:
        return input_string
    if stripped[0] == "[" and stripped[-1] == "]":
        return [try_json_parse(elem) for elem in json.loads(input_string)]
    if stripped[0] == "{" and stripped[-1] == "}":
        return {
            key: try_json_parse(value)
            for key, value in json.loads(input_string).items()
        }
    return input_string


def xcall(app_name: str, *actions: str, **keywords: str) -> str:
    """
    Call an application using the `x-callback-url` protocol.

    If there is an `x-error` reply, an error is raised with the message.
    Otherwise, the `x-succes` reply is parsed as a JSON object, which is returned.
    Use :func:`xcall_raw` to not parse the reply.

    The URL can be defined based on the `app_name` and `actions`/`keywords`
    as described in :func:`build_url` or by supplying the URL directly as a string.
    """
    return try_json_parse(xcall_raw(app_name, *actions, **keywords))

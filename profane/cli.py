import os
from shlex import shlex
import yaml


def config_string_to_dict(s):
    s = " ".join(s.split())  # remove consecutive whitespace
    return config_list_to_dict(s.split())


def config_list_to_dict(l):
    d = {}

    for k, v in _config_list_to_pairs(l):
        _dot_to_dict(d, k, v)

    return d


def _recursive_update(ori_dict, new_dict):
    for k in new_dict:
        if k not in ori_dict:
            ori_dict[k] = new_dict[k]
        elif not isinstance(ori_dict[k], dict):
            ori_dict[k] = new_dict[k]
        else:
            ori_value, new_value = ori_dict[k], new_dict[k]
            ori_dict[k] = _recursive_update(ori_value, new_value)
    return ori_dict


def _load_yaml(fn):
    with open(fn) as f:
        config = yaml.load(f)

    if "_base_" in config:
        base_path = config["_base_"]
        base_config = _load_yaml(base_path)
        config = _recursive_update(ori_dict=base_config, new_dict=config)
        del config["_base_"]

    return config

def _dot_to_dict(d, k, v):
    if k.startswith(".") or k.endswith("."):
        raise ValueError(f"invalid path: {k}")

    if "." in k:
        path = k.split(".")
        current_k = path[0]
        remaining_path = ".".join(path[1:])

        d.setdefault(current_k, {})
        _dot_to_dict(d[current_k], remaining_path, v)
    elif k.lower() == "file":
        ext = os.path.splitext(v)[1]
        if ext == '.yaml':
            y = _load_yaml(v)
            d.update(y)
        else:        
            lst = _config_file_to_list(v)
            for new_k, new_v in _config_list_to_pairs(lst):
                _dot_to_dict(d, new_k, new_v)
    else:
        d[k] = v


def _config_list_to_pairs(l):
    pairs = []
    for kv in l:
        kv = kv.strip()

        if len(kv) == 0:
            continue

        if kv.count("=") != 1:
            raise ValueError(f"invalid 'key=value' pair: {kv}")

        k, v = kv.split("=")
        if len(v) == 0:
            raise ValueError(f"invalid 'key=value' pair: {kv}")

        pairs.append((k, v))

    return pairs


def _config_file_to_list(fn):
    lst = []
    ext = os.path.splitext(fn)[1]
    if ext == 'yaml':
        yaml_list = _load_yaml(fn)
        lst.extend(yaml_list)
    else:
        with open(os.path.expanduser(fn), "rt") as f:
            for line in f:
                lex = shlex(line)
                lex.whitespace = ""
                kvs = "".join(list(lex))
                for kv in kvs.strip().split():
                    lst.append(kv)

    return lst

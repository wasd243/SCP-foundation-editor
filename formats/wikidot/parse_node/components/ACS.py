try:
    import parse_node_py
    HAS_PARSE_NODE_RUST = True
except ImportError:
    HAS_PARSE_NODE_RUST = False

if not HAS_PARSE_NODE_RUST:
    print("[EXPORTER] 正向解析rust模块缺失，需检查parse_node_py / acs 生成模块 是否被正确导入")
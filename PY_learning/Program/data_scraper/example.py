#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import sys
from typing import Dict

import requests


def parse_kv_list(items, sep="=") -> Dict[str, str]:
    result = {}
    for item in items or []:
        if sep not in item:
            raise ValueError(f"参数格式错误: {item}，应为 key{sep}value")
        k, v = item.split(sep, 1)
        result[k.strip()] = v.strip()
    return result


def main():
    parser = argparse.ArgumentParser(description="命令行数据抓取脚本（requests）")
    parser.add_argument("url", nargs="?", default="https://httpbin.org/get", help="目标 URL（可省略）")
    parser.add_argument("-o", "--output", default="result.json", help="输出文件名")
    parser.add_argument("-X", "--method", default="GET", choices=["GET", "POST"], help="请求方法")
    parser.add_argument("-p", "--param", action="append", help="查询参数，格式: key=value，可重复")
    parser.add_argument("-d", "--data", action="append", help="POST 表单参数，格式: key=value，可重复")
    parser.add_argument("-H", "--header", action="append", help="请求头，格式: key:value，可重复")
    parser.add_argument("-t", "--timeout", type=float, default=10, help="超时秒数，默认 10")
    args = parser.parse_args()

    try:
        params = parse_kv_list(args.param, sep="=")
        data = parse_kv_list(args.data, sep="=")
        headers = parse_kv_list(args.header, sep=":")

        resp = requests.request(
            method=args.method,
            url=args.url,
            params=params if params else None,
            data=data if data else None,
            headers=headers if headers else None,
            timeout=args.timeout,
        )
        resp.raise_for_status()

        try:
            payload = resp.json()
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            print(f"抓取成功（JSON），已保存到: {args.output}")
        except ValueError:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"抓取成功（Text/HTML），已保存到: {args.output}")

    except Exception as e:
        print(f"抓取失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
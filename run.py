#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Paper Finder 启动脚本
用于启动生物学文献调研工具
"""

import os
import sys
import argparse
from app import app, init_db


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='启动Paper Finder生物学文献调研工具')
    parser.add_argument('--host', default='127.0.0.1', help='服务器主机地址 (默认: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口 (默认: 5000)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--init-db', action='store_true', help='初始化数据库')
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 检查是否需要初始化数据库
    if args.init_db:
        print("正在初始化数据库...")
        init_db()
        print("数据库初始化完成！")
    
    # 启动应用
    print(f"启动Paper Finder应用，访问地址: http://{args.host}:{args.port}")
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已停止运行")
        sys.exit(0)
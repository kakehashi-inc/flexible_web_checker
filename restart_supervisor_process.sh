#!/bin/bash

# カレントパスを取得して2階層分のディレクトリを-で結合したパスを取得
current_path=$(pwd)

# パスの最後のディレクトリを取得
last_dir=$(basename "$current_path")

process_name="${last_dir}"

# 引数が存在すればprocess_nameの末尾に追加
if [ $# -gt 0 ]; then
    process_name="${process_name}$1"
fi

supervisorctl restart $process_name

exit 0

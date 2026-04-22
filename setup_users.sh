#!/usr/bin/env bash
set -e

ENV_FILE="$(dirname "$0")/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "错误：找不到 $ENV_FILE"
  exit 1
fi

echo "=== TwoSpace 用户配置 ==="
echo ""

for i in 1 2; do
  echo "── 用户 $i ──"
  read -rp "  昵称: " name
  read -rsp "  密码: " password
  echo ""

  # 生成 bcrypt 哈希并转义 $ 为 $$
  hash=$(python3 -c "
import bcrypt, sys
pw = sys.argv[1].encode()
print(bcrypt.hashpw(pw, bcrypt.gensalt()).decode())
" "$password")

  escaped="${hash//\$/\$\$}"

  # 更新 .env
  sed -i "s|^USER${i}_NAME=.*|USER${i}_NAME=${name}|" "$ENV_FILE"
  sed -i "s|^USER${i}_PASSWORD_HASH=.*|USER${i}_PASSWORD_HASH=${escaped}|" "$ENV_FILE"

  echo "  ✓ 已更新"
  echo ""
done

echo "=== 完成，已写入 $ENV_FILE ==="

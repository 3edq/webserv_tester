#!/bin/bash

# WebServ シンプルテスト (curl使用)

# 色付きoutput用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_URL="http://localhost"
PORT1=8080
PORT2=8081

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🧪 WebServ シンプルテスト (curl)${NC}"
echo -e "${BLUE}========================================${NC}"

# webservが起動しているかチェック
check_server() {
    local port=$1
    if ! curl -s --connect-timeout 3 "${BASE_URL}:${port}/" > /dev/null; then
        echo -e "${RED}❌ webservがポート${port}で応答していません${NC}"
        echo -e "${YELLOW}💡 先に './webserv conf/default.conf' でサーバーを起動してください${NC}"
        return 1
    fi
    return 0
}

# テスト関数
run_test() {
    local test_name="$1"
    local curl_cmd="$2"
    local expected_pattern="$3"
    
    echo -e "${YELLOW}🔍 テスト: ${test_name}${NC}"
    echo -e "   コマンド: ${curl_cmd}"
    
    # curlを実行してレスポンスを取得
    response=$(eval "$curl_cmd" 2>/dev/null)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        if [ -n "$expected_pattern" ]; then
            if echo "$response" | grep -q "$expected_pattern"; then
                echo -e "${GREEN}   ✅ PASS${NC}"
            else
                echo -e "${RED}   ❌ FAIL (期待されるパターンが見つかりません)${NC}"
            fi
        else
            echo -e "${GREEN}   ✅ PASS (接続成功)${NC}"
        fi
    else
        echo -e "${RED}   ❌ FAIL (接続失敗)${NC}"
    fi
    echo
}

# サーバー起動チェック
if ! check_server $PORT1; then
    exit 1
fi

echo -e "${GREEN}✅ webservが起動していることを確認しました${NC}"
echo

# 基本的なテスト実行
echo -e "${BLUE}📋 基本機能テスト${NC}"

# 1. 基本的なGETリクエスト
run_test "基本的なGET" \
    "curl -s -i ${BASE_URL}:${PORT1}/" \
    "HTTP/"

# 2. 存在しないページ（404テスト）
run_test "404エラー" \
    "curl -s -i ${BASE_URL}:${PORT1}/nonexistent" \
    "404"

# 3. POSTリクエスト（アップロード）
run_test "POSTアップロード" \
    "curl -s -i -X POST -F 'upfile=@conf/default.conf' ${BASE_URL}:${PORT1}/upload/" \
    "HTTP/"

# 4. DELETEリクエスト
run_test "DELETEリクエスト" \
    "curl -s -i -X DELETE ${BASE_URL}:${PORT1}/delete/test.txt" \
    "HTTP/"

# 5. CGIリクエスト
run_test "CGI実行" \
    "curl -s -i ${BASE_URL}:${PORT1}/cgi/" \
    "HTTP/"

# 6. リダイレクト
run_test "リダイレクト" \
    "curl -s -i ${BASE_URL}:${PORT1}/redirect/" \
    "301\|302\|307"

# 7. ディレクトリリスティング
run_test "ディレクトリリスティング" \
    "curl -s -i ${BASE_URL}:${PORT1}/index/" \
    "HTTP/"

# バーチャルホストテスト（ポート8081が利用可能な場合）
if check_server $PORT2; then
    echo -e "${BLUE}📋 バーチャルホストテスト${NC}"
    
    # 8. default_server
    run_test "default_server" \
        "curl -s -i -H 'Host: default_server:8081' ${BASE_URL}:${PORT2}/" \
        "HTTP/"
    
    # 9. virtual_server
    run_test "virtual_server" \
        "curl -s -i -H 'Host: virtual_server:8081' ${BASE_URL}:${PORT2}/" \
        "HTTP/"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}✅ シンプルテスト完了${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}💡 詳細なテストを実行するには 'python3 test_webserv.py' を使用してください${NC}" 
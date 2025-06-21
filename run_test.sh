#!/bin/bash

# WebServ テスト実行スクリプト

set -e  # エラー時に終了

# 色付きoutput用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🧪 WebServ 課題要件テストスイート${NC}"
echo -e "${BLUE}========================================${NC}"

# 前提条件チェック
echo -e "${YELLOW}📋 前提条件をチェック中...${NC}"

# Makefileが存在するかチェック
if [ ! -f "Makefile" ]; then
    echo -e "${RED}❌ Makefileが見つかりません${NC}"
    exit 1
fi

# Python3とrequestsモジュールのチェック
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3が見つかりません。Python3をインストールしてください。${NC}"
    exit 1
fi

if ! python3 -c "import requests" 2>/dev/null; then
    echo -e "${YELLOW}⚠️ requestsモジュールが見つかりません。インストールしています...${NC}"
    pip3 install requests
fi

# webservをビルド
echo -e "${YELLOW}🔨 webservをビルド中...${NC}"
make clean >/dev/null 2>&1 || true
if ! make; then
    echo -e "${RED}❌ webservのビルドに失敗しました${NC}"
    exit 1
fi

# webservの実行ファイルが存在するかチェック
if [ ! -f "./webserv" ]; then
    echo -e "${RED}❌ webservの実行ファイルが見つかりません${NC}"
    exit 1
fi

# 設定ファイルが存在するかチェック
if [ ! -f "conf/default.conf" ]; then
    echo -e "${RED}❌ 設定ファイル (conf/default.conf) が見つかりません${NC}"
    exit 1
fi

# テスト用ディレクトリの準備
echo -e "${YELLOW}📁 テスト環境を準備中...${NC}"

# 必要なディレクトリを作成
mkdir -p docs upload static cgi-bin errors

# テスト用のHTMLファイルを作成
if [ ! -f "docs/index.html" ]; then
    cat > docs/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>WebServ Test Page</title>
</head>
<body>
    <h1>WebServ テストページ</h1>
    <p>このページはwebservのテスト用です。</p>
    <ul>
        <li><a href="/upload/">アップロード</a></li>
        <li><a href="/static/">静的ファイル</a></li>
        <li><a href="/cgi/">CGI</a></li>
        <li><a href="/redirect/">リダイレクト</a></li>
    </ul>
</body>
</html>
EOF
fi

# バーチャルホスト用のファイル
if [ ! -f "docs/default.html" ]; then
    cat > docs/default.html << 'EOF'
<!DOCTYPE html>
<html><head><title>Default Server</title></head>
<body><h1>Default Server Page</h1></body></html>
EOF
fi

if [ ! -f "docs/virtual.html" ]; then
    cat > docs/virtual.html << 'EOF'
<!DOCTYPE html>
<html><head><title>Virtual Server</title></head>
<body><h1>Virtual Server Page</h1></body></html>
EOF
fi

# テスト用のCGIスクリプト
if [ ! -f "cgi-bin/cgi.sh" ]; then
    cat > cgi-bin/cgi.sh << 'EOF'
#!/bin/bash
echo "Content-Type: text/html"
echo ""
echo "<!DOCTYPE html>"
echo "<html><head><title>CGI Test</title></head>"
echo "<body>"
echo "<h1>CGI Test Success</h1>"
echo "<p>現在時刻: $(date)</p>"
echo "<p>環境変数:</p><ul>"
echo "<li>REQUEST_METHOD: $REQUEST_METHOD</li>"
echo "<li>QUERY_STRING: $QUERY_STRING</li>"
echo "</ul>"
echo "</body></html>"
EOF
    chmod +x cgi-bin/cgi.sh
fi

# エラーページの作成
for code in 404 403 500; do
    if [ ! -f "errors/${code}.html" ]; then
        cat > errors/${code}.html << EOF
<!DOCTYPE html>
<html><head><title>Error ${code}</title></head>
<body><h1>Error ${code}</h1><p>WebServ Custom Error Page</p></body></html>
EOF
    fi
done

# 既存のwebservプロセスを停止
echo -e "${YELLOW}🛑 既存のwebservプロセスを停止中...${NC}"
pkill -f "./webserv" 2>/dev/null || true
sleep 1

# ポートが使用中でないかチェック
for port in 8080 8081; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️ ポート $port が使用中です。プロセスを終了しています...${NC}"
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
done

echo -e "${GREEN}✅ 前提条件とテスト環境の準備が完了しました${NC}"

# Pythonテストスクリプトを実行
echo -e "${BLUE}🚀 テストを開始します...${NC}"
python3 test_webserv.py

# テスト結果の確認
if [ $? -eq 0 ]; then
    echo -e "${GREEN}🎉 テストが正常に完了しました！${NC}"
else
    echo -e "${RED}😞 テストで問題が発見されました。${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}✅ WebServ テスト完了${NC}"
echo -e "${BLUE}========================================${NC}" 
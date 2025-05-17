#!/bin/bash
# SSL証明書を生成するスクリプト

mkdir -p ./opensearch/config/certs

# rootCAの作成
openssl genrsa -out ./opensearch/config/certs/root-ca-key.pem 2048
openssl req -new -x509 -sha256 -key ./opensearch/config/certs/root-ca-key.pem -out ./opensearch/config/certs/root-ca.pem -days 730 -subj "/C=JP/ST=Tokyo/L=Tokyo/O=YourOrg/OU=IT/CN=root-ca"

# adminクライアント証明書の作成
openssl genrsa -out ./opensearch/config/certs/admin-key-temp.pem 2048
openssl pkcs8 -inform PEM -outform PEM -in ./opensearch/config/certs/admin-key-temp.pem -topk8 -nocrypt -v1 PBE-SHA1-3DES -out ./opensearch/config/certs/admin-key.pem
openssl req -new -key ./opensearch/config/certs/admin-key.pem -out ./opensearch/config/certs/admin.csr -days 730 -subj "/C=JP/ST=Tokyo/L=Tokyo/O=YourOrg/OU=IT/CN=admin"
openssl x509 -req -in ./opensearch/config/certs/admin.csr -CA ./opensearch/config/certs/root-ca.pem -CAkey ./opensearch/config/certs/root-ca-key.pem -CAcreateserial -out ./opensearch/config/certs/admin.pem -days 730

# ノード証明書の作成
openssl genrsa -out ./opensearch/config/certs/node-key-temp.pem 2048
openssl pkcs8 -inform PEM -outform PEM -in ./opensearch/config/certs/node-key-temp.pem -topk8 -nocrypt -v1 PBE-SHA1-3DES -out ./opensearch/config/certs/node-key.pem
openssl req -new -key ./opensearch/config/certs/node-key.pem -out ./opensearch/config/certs/node.csr -days 730 -subj "/C=JP/ST=Tokyo/L=Tokyo/O=YourOrg/OU=IT/CN=node"
openssl x509 -req -in ./opensearch/config/certs/node.csr -CA ./opensearch/config/certs/root-ca.pem -CAkey ./opensearch/config/certs/root-ca-key.pem -CAcreateserial -out ./opensearch/config/certs/node.pem -days 730

# 不要なファイルの削除
rm ./opensearch/config/certs/*.csr
rm ./opensearch/config/certs/*-temp.pem

echo "証明書の生成が完了しました。"

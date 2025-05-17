#!/bin/bash

# OpenSearchコンテナ内でsecurityadminツールを実行
docker exec opensearch bash -c '
cd /usr/share/opensearch
plugins/opensearch-security/tools/securityadmin.sh \
  -cd /usr/share/opensearch/config/opensearch-security/ \
  -icl \
  -nhnv \
  -cacert config/root-ca.pem \
  -cert config/kirk.pem \
  -key config/kirk-key.pem \
  -h localhost
'

# FROM opensearchproject/opensearch:2.18.0
# FROM krayinc/opensearch:2.17.1-sudachi-ingest-attachment
FROM opensearchproject/opensearch:2.17.1

RUN opensearch-plugin install --batch https://github.com/WorksApplications/elasticsearch-sudachi/releases/download/v3.3.0/opensearch-2.17.1-analysis-sudachi-3.3.0.zip

USER root

RUN yum install -y unzip

USER opensearch

RUN curl -O http://sudachi.s3-website-ap-northeast-1.amazonaws.com/sudachidict/sudachi-dictionary-20241021-core.zip &&   unzip sudachi-dictionary-20241021-core.zip &&   mkdir -p /usr/share/opensearch/config/sudachi &&   mv sudachi-dictionary-20241021/system_core.dic /usr/share/opensearch/config/sudachi/system_core.dic &&   rm -rf sudachi-dictionary-20241021-core.zip sudachi-dictionary-20241021/

RUN touch /usr/share/opensearch/config/synonyms.txt

COPY synonyms.txt* /usr/share/opensearch/config/synonyms.txt

# RUN yum update -y
# RUN yum install -y sudo
# RUN sudo yum install openssl -y

# RUN openssl genrsa -out root-ca-key.pem 2048
# RUN openssl req -new -x509 -sha256 -key root-ca-key.pem -out root-ca.pem -days 730 -subj "/C=JP/ST=Tokyo/L=Tokyo/O=Example Company/OU=IT/CN=admin"

# RUN openssl genrsa -out admin-key-temp.pem 2048
# RUN openssl pkcs8 -inform PEM -outform PEM -in admin-key-temp.pem -topk8 -nocrypt -v1 PBE-SHA1-3DES -out admin-key.pem
# RUN openssl req -new -key admin-key.pem -out admin.csr -subj "/C=JP/ST=Tokyo/L=Tokyo/O=Example Company/OU=IT/CN=admin"
# RUN openssl x509 -req -in admin.csr -CA root-ca.pem -CAkey root-ca-key.pem -CAcreateserial -sha256 -out admin.pem -days 730 -subj "/C=JP/ST=Tokyo/L=Tokyo/O=Example Company/OU=IT/CN=admin"
# RUN rm admin-key-temp.pem
# RUN chmod 644 /usr/share/opensearch/config/admin-key.pem

# RUN opensearch-plugin install \
# https://github.com/WorksApplications/elasticsearch-sudachi/releases/download/v3.2.3/opensearch-2.17.1-analysis-sudachi-3.2.3.zip
# USER opensearch
# RUN ./gradlew -PengineVersion=os:2.18.0 build -x test

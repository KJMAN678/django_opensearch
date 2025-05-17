FROM opensearchproject/opensearch:2.17.1

RUN opensearch-plugin install --batch https://github.com/WorksApplications/elasticsearch-sudachi/releases/download/v3.3.0/opensearch-2.17.1-analysis-sudachi-3.3.0.zip

USER root

RUN yum install -y unzip

USER opensearch

RUN curl -O http://sudachi.s3-website-ap-northeast-1.amazonaws.com/sudachidict/sudachi-dictionary-20241021-core.zip &&   unzip sudachi-dictionary-20241021-core.zip &&   mkdir -p /usr/share/opensearch/config/sudachi &&   mv sudachi-dictionary-20241021/system_core.dic /usr/share/opensearch/config/sudachi/system_core.dic &&   rm -rf sudachi-dictionary-20241021-core.zip sudachi-dictionary-20241021/

RUN touch /usr/share/opensearch/config/synonyms.txt

COPY synonyms.txt* /usr/share/opensearch/config/synonyms.txt

RUN mkdir -p /usr/share/opensearch/config/backup
COPY backup/* /usr/share/opensearch/config/backup/

# RUN mkdir -p /usr/share/opensearch/config/opensearch-security
# COPY opensearch-security/* /usr/share/opensearch/config/opensearch-security/

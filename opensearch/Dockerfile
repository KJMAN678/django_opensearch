FROM opensearchproject/opensearch:2.18.0

USER root

RUN yum install -y wget unzip

RUN /usr/share/opensearch/bin/opensearch-plugin install --batch https://github.com/WorksApplications/elasticsearch-sudachi/releases/download/v3.3.0/opensearch-2.18.0-analysis-sudachi-3.3.0.zip
RUN mkdir /usr/share/opensearch/config/sudachi
RUN wget https://github.com/WorksApplications/SudachiDict/releases/download/v20250129/sudachi-dictionary-20250129-small.zip -O sudachi-dictionary-20250129-small.zip
RUN unzip sudachi-dictionary-20250129-small.zip -d /usr/share/opensearch/config/sudachi
# COPY sudachi-dictionary-*/system_core.dic /usr/share/opensearch/config/sudachi/system_core.dic
# RUN rm sudachi-dictionary-20250129-small.zip

# # ユーザーをopensearchに戻す
USER opensearch

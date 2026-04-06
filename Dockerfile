FROM jekyll/jekyll:4

WORKDIR /srv/content

# Install Python + bash for your scripts
USER root
RUN apk add --no-cache python3 py3-pip bash \
    && pip install pyyaml

USER root
# Keep container running root for gem installation and avoid permission issues
# Scripts will handle gem install automatically
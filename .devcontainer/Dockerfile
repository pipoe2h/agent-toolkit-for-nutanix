FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ARG OPENCODE_VERSION=1.19.4
ARG SKILLS_CLI_VERSION=1.7.4

USER vscode
WORKDIR /workspaces

ENV NPM_CONFIG_PREFIX="/home/vscode/.local/share/npm"
ENV PATH="/home/vscode/.opencode/bin:/home/vscode/.local/bin:/home/vscode/.local/share/npm/bin:${PATH}"

RUN curl -fsSL https://opencode.ai/install | bash -s -- --version "${OPENCODE_VERSION}" \
    && npm install --global "skills@${SKILLS_CLI_VERSION}" \
    && opencode --version \
    && skills --version

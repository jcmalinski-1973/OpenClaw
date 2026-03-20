#!/bin/bash
# Deploy OpenClaw no servidor de produção
# Uso: bash deploy.sh [branch]
# Exemplo: bash deploy.sh claude/validate-bread-king-orders-hKgsd

set -euo pipefail

# Garantir que Docker esteja no PATH (pode estar ausente em shells não-interativos)
export PATH="$PATH:/usr/bin:/usr/local/bin:/usr/local/docker/bin"

# Resolver o comando $DC (v2 plugin ou v1 standalone)
if $DC version &>/dev/null 2>&1; then
    DC="$DC"
elif docker-compose version &>/dev/null 2>&1; then
    DC="docker-compose"
else
    echo "ERRO: $DC não encontrado. Instale o Docker antes de continuar."
    exit 1
fi

BRANCH="${1:-claude/validate-bread-king-orders-hKgsd}"
DEPLOY_DIR="/home/jcmalinski/OpenClaw"
REPO_URL="https://github.com/jcmalinski-1973/OpenClaw.git"

echo "==> Deploy OpenClaw | branch: $BRANCH"
echo "==> Destino: $DEPLOY_DIR"

# ── 1. Clonar ou atualizar repositório ─────────────────────────────────────
if [ -d "$DEPLOY_DIR/.git" ]; then
    echo "==> Atualizando repositório existente..."
    cd "$DEPLOY_DIR"
    git fetch origin
    git checkout "$BRANCH"
    git reset --hard "origin/$BRANCH"
else
    echo "==> Clonando repositório..."
    git clone -b "$BRANCH" "$REPO_URL" "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
fi

# ── 2. Criar .env se não existir ────────────────────────────────────────────
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    echo "==> Criando .env a partir do .env.example..."
    cp "$DEPLOY_DIR/.env.example" "$DEPLOY_DIR/.env"

    # Herdar variáveis do PedidoBK se existirem
    PEDIDOBK_ENV="/home/jcmalinski/PedidoBK/PedidoBK/.env"
    if [ -f "$PEDIDOBK_ENV" ]; then
        echo "==> Copiando configurações do PedidoBK existente..."
        source "$PEDIDOBK_ENV"
        [ -n "${DB_PASSWORD:-}" ]       && sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/"             "$DEPLOY_DIR/.env"
        [ -n "${GCS_BUCKET_NAME:-}" ]   && sed -i "s/^GCS_BUCKET_NAME=.*/GCS_BUCKET_NAME=$GCS_BUCKET_NAME/" "$DEPLOY_DIR/.env"
        [ -n "${GCS_PROJECT_ID:-}" ]    && sed -i "s/^GCS_PROJECT_ID=.*/GCS_PROJECT_ID=$GCS_PROJECT_ID/"     "$DEPLOY_DIR/.env"
        [ -n "${GCS_PREFIX:-}" ]        && sed -i "s/^GCS_PREFIX=.*/GCS_PREFIX=$GCS_PREFIX/"                 "$DEPLOY_DIR/.env"
        [ -n "${STORAGE_BACKEND:-}" ]   && sed -i "s/^STORAGE_BACKEND=.*/STORAGE_BACKEND=$STORAGE_BACKEND/"  "$DEPLOY_DIR/.env"
    fi

    # HOST_USER para montar ADC do gcloud
    sed -i "s/^HOST_USER=.*/HOST_USER=$(whoami)/" "$DEPLOY_DIR/.env"

    echo "==> ATENÇÃO: revise o arquivo $DEPLOY_DIR/.env antes de continuar"
    echo "    Pressione ENTER para continuar ou Ctrl+C para abortar"
    read -r
fi

# ── 3. Build do frontend ─────────────────────────────────────────────────────
echo "==> Buildando frontend..."
cd "$DEPLOY_DIR/frontend"
npm ci --silent
npx vite build

# ── 4. Subir containers ──────────────────────────────────────────────────────
echo "==> Subindo containers Docker..."
cd "$DEPLOY_DIR"

# Para o stack anterior se estiver rodando neste diretório
$DC down 2>/dev/null || true

$DC up -d --build

# ── 5. Aguardar banco ficar saudável ─────────────────────────────────────────
echo "==> Aguardando banco de dados..."
for i in $(seq 1 30); do
    if $DC exec -T db pg_isready -U pedidobk -q 2>/dev/null; then
        echo "    Banco pronto."
        break
    fi
    echo "    Tentativa $i/30..."
    sleep 2
done

# ── 6. Executar migrações ────────────────────────────────────────────────────
echo "==> Executando migrações Alembic..."
$DC exec -T backend alembic upgrade head

# ── 7. Verificar saúde da API ─────────────────────────────────────────────────
echo "==> Verificando API..."
sleep 3
curl -sf http://localhost/health && echo " API OK" || echo " AVISO: /health não respondeu"

echo ""
echo "✓ Deploy concluído!"
echo "  Acesse: http://$(hostname -I | awk '{print $1}')"

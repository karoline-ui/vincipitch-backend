# 🚀 Deploy VinciPitch.AI no Google Cloud Platform

## Pré-requisitos

1. Conta no GCP com projeto criado
2. `gcloud` CLI instalado e configurado
3. APIs habilitadas:
   - Cloud Run
   - Cloud Build
   - Container Registry

```bash
# Habilitar APIs necessárias
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

---

## Opção 1: Deploy Manual (Cloud Run)

### 1. Configurar variáveis de ambiente

```bash
# No Console GCP > Cloud Run > Seu serviço > Variáveis de ambiente
# Ou via CLI:

gcloud run deploy vincipitch-api \
  --set-env-vars="SUPABASE_URL=https://seu-projeto.supabase.co" \
  --set-env-vars="SUPABASE_ANON_KEY=sua-anon-key" \
  --set-env-vars="SUPABASE_SERVICE_KEY=sua-service-key" \
  --set-env-vars="OPENAI_API_KEY=sk-sua-api-key" \
  --set-env-vars="OPENAI_MODEL=gpt-4o-mini" \
  --set-env-vars="APP_ENV=production"
```

### 2. Build e Deploy

```bash
cd backend

# Build da imagem
gcloud builds submit --tag gcr.io/SEU_PROJETO/vincipitch-api

# Deploy no Cloud Run
gcloud run deploy vincipitch-api \
  --image gcr.io/SEU_PROJETO/vincipitch-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300
```

---

## Opção 2: Deploy Automático (Cloud Build)

### 1. Configurar Secrets no Secret Manager

```bash
# Criar secrets
echo -n "sua-supabase-url" | gcloud secrets create SUPABASE_URL --data-file=-
echo -n "sua-anon-key" | gcloud secrets create SUPABASE_ANON_KEY --data-file=-
echo -n "sua-service-key" | gcloud secrets create SUPABASE_SERVICE_KEY --data-file=-
echo -n "sk-sua-openai-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
```

### 2. Deploy via Cloud Build

```bash
cd backend
gcloud builds submit --config cloudbuild.yaml
```

### 3. Configurar Trigger (CI/CD)

1. Vá para Cloud Build > Triggers
2. Crie novo trigger
3. Conecte ao seu repositório GitHub/GitLab
4. Configure para rodar `cloudbuild.yaml` em push para `main`

---

## Verificar Deploy

### Health Check
```bash
curl https://SEU-SERVICO-URL/health
# Resposta: {"ok": true, "status": "healthy"}
```

### Informações do Ambiente
```bash
curl https://SEU-SERVICO-URL/whoami
# Resposta: {"app": "VinciPitch.AI", "version": "1.0.0", "env": "production", ...}
```

### API Docs
Acesse: `https://SEU-SERVICO-URL/docs`

---

## Frontend (Vercel/Netlify)

Para o frontend Next.js, recomendo deploy no Vercel:

```bash
cd frontend

# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel

# Configurar variável de ambiente
# NEXT_PUBLIC_API_URL=https://SEU-SERVICO-CLOUDRUN-URL/api/v1
```

---

## Custos Estimados (GCP)

- **Cloud Run**: ~$0 com free tier (2M requests/mês)
- **Container Registry**: ~$0.10/GB/mês
- **Cloud Build**: 120 min/dia grátis

Para projetos pequenos, pode ficar **grátis** ou custar **< $10/mês**.

---

## Troubleshooting

### Erro de memória
```bash
gcloud run services update vincipitch-api --memory 2Gi
```

### Erro de timeout
```bash
gcloud run services update vincipitch-api --timeout 600
```

### Ver logs
```bash
gcloud run services logs read vincipitch-api --limit 50
```

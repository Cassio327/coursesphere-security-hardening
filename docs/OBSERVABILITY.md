# Observabilidade e confiabilidade

## Sinais implementados

### Logs estruturados

O backend emite JSON em `stdout` para que o runtime possa coletar sem arquivos locais. Cada requisição registra:

- horário, nível e evento;
- `request_id` recebido ou gerado;
- método, caminho, endpoint e status;
- duração em milissegundos;
- identificador da instância.

Eventos de autenticação registram sucesso ou motivo genérico de falha, sem armazenar o token. O Nginx também registra o endereço upstream usado em cada resposta.

### Health check

`GET /health` indica se o processo consegue atender requisições e identifica a réplica:

```json
{
  "status": "healthy",
  "service": "coursesphere-backend",
  "instance": "backend-1"
}
```

O endpoint é usado pelos healthchecks dos containers e pelo Nginx indiretamente. Em evolução futura, um readiness check separado deve validar dependências críticas com timeout curto.

### Métricas Prometheus

`GET /metrics` expõe:

- `coursesphere_http_requests_total` por método, endpoint, status e instância;
- `coursesphere_http_request_duration_seconds` como histograma;
- `coursesphere_http_requests_in_progress` por instância;
- `coursesphere_build_info` com a versão da aplicação.

Prometheus coleta as duas réplicas a cada 10 segundos. O dashboard `CourseSphere - Reliability` é provisionado no Grafana durante a inicialização.

## SLIs e SLOs

### SLI 1 — Disponibilidade da API

**Definição:** proporção de requisições que não terminam em erro 5xx.

```promql
1 - (
  sum(rate(coursesphere_http_requests_total{status=~"5.."}[5m]))
  /
  clamp_min(sum(rate(coursesphere_http_requests_total[5m])), 0.001)
)
```

**SLO proposto:** 99,5% das requisições sem erro 5xx em uma janela móvel de 30 dias.

**Error budget:** 0,5%, equivalente a aproximadamente 216 minutos de indisponibilidade em 30 dias quando medido continuamente.

### SLI 2 — Latência da API

**Definição:** percentil 95 da duração das requisições HTTP.

```promql
histogram_quantile(
  0.95,
  sum by (le) (rate(coursesphere_http_request_duration_seconds_bucket[5m]))
)
```

**SLO proposto:** p95 menor ou igual a 500 ms em pelo menos 95% das janelas de cinco minutos de um período de 30 dias.

O endpoint de consultas pode depender de provedor externo. Em produção, ele deve ter SLI próprio, timeout explícito e um SLO menos agressivo que as rotas locais.

## Dashboard

O dashboard funcional contém quatro painéis:

1. disponibilidade nos últimos cinco minutos;
2. latência p95;
3. requisições por instância, útil para confirmar balanceamento;
4. proporção de respostas 5xx.

Acesso local:

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- credenciais exclusivamente locais: `admin` / `local-observability-only`

## Riscos de disponibilidade

| Risco | Consequência | Recomendação |
|---|---|---|
| Firebase como dependência externa | login e perfil indisponíveis | timeout, circuit breaker e indicador separado |
| OpenAI como dependência externa | consultas lentas ou indisponíveis | timeout, retry com jitter e limite de custo |
| Nginx único no Compose | ponto único de falha | load balancer gerenciado ou múltiplas réplicas |
| Rate limiter em memória | limite inconsistente entre réplicas | Redis ou API Gateway |
| Ausência de fila | picos atingem diretamente o backend | fila para trabalhos longos e backpressure |
| Métricas locais ao processo | perda após reinício | Prometheus remoto e retenção adequada |

## Alertas recomendados

- disponibilidade menor que 99,5% por 10 minutos;
- p95 acima de 500 ms por 15 minutos;
- consumo rápido de error budget em janelas de uma e seis horas;
- uma das instâncias ausente no Prometheus por mais de dois ciclos;
- aumento de falhas de autenticação ou bloqueios por rate limiting.

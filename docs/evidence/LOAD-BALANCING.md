# Evidência de balanceamento

Execução automatizada no GitHub Actions em 27/10/2026, após construir as imagens e iniciar Nginx, frontend e duas réplicas do backend.

Comando:

```bash
./scripts/demo-load-balancing.sh
```

Saída sanitizada:

```text
Requesting http://localhost:8080/api/health eight times:
1: {"instance":"backend-1","service":"coursesphere-backend","status":"healthy"}
2: {"instance":"backend-1","service":"coursesphere-backend","status":"healthy"}
3: {"instance":"backend-2","service":"coursesphere-backend","status":"healthy"}
4: {"instance":"backend-1","service":"coursesphere-backend","status":"healthy"}
5: {"instance":"backend-2","service":"coursesphere-backend","status":"healthy"}
6: {"instance":"backend-1","service":"coursesphere-backend","status":"healthy"}
7: {"instance":"backend-2","service":"coursesphere-backend","status":"healthy"}
8: {"instance":"backend-1","service":"coursesphere-backend","status":"healthy"}
PASS: responses were distributed between backend-1 and backend-2.
```

Na mesma execução, `scripts/security-smoke-test.sh` confirmou:

```text
PASS: unauthenticated access was rejected and security headers are active.
```

O script encerra com erro se qualquer uma das duas instâncias não aparecer nas respostas, tornando a evidência verificável e repetível.

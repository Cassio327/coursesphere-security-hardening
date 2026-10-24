# CourseSphere Security Hardening

Projeto desenvolvido para o desafio técnico de AppSec, SRE e DevOps do V-LAB.

O trabalho parte da aplicação [CourseSphere](https://github.com/LambdaAK/CourseSphere) e tem como objetivo analisar vulnerabilidades reais, aplicar correções na causa raiz e adicionar práticas básicas de segurança, observabilidade e confiabilidade.

## Status

Em desenvolvimento.

## Objetivos

- documentar pelo menos cinco vulnerabilidades reproduzíveis;
- corrigir pelo menos três vulnerabilidades sem quebrar as funcionalidades existentes;
- implementar melhorias de hardening;
- adicionar logs estruturados, health check e métricas;
- definir SLIs e SLOs relevantes;
- containerizar a aplicação e demonstrar balanceamento entre instâncias;
- manter instruções e evidências suficientes para reprodução.

## Organização do trabalho

O desenvolvimento será dividido em etapas acompanhadas por issues e branches:

1. baseline reproduzível;
2. análise de segurança;
3. correções e hardening;
4. observabilidade e confiabilidade;
5. infraestrutura e balanceamento;
6. documentação e validação final.

## Segurança do ambiente

Os testes devem ser executados somente em ambiente local e isolado. Credenciais, tokens, arquivos de configuração privados e resultados contendo dados sensíveis não devem ser versionados.

## Origem

Aplicação de referência: [LambdaAK/CourseSphere](https://github.com/LambdaAK/CourseSphere).

As alterações de segurança, confiabilidade, infraestrutura e documentação deste repositório fazem parte do desafio técnico.

## Desenvolvimento local

As instruções de preparação, execução e validação estão em [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md).

# Deploy no Vercel

Este projeto foi adaptado para funcionar como backend serverless no Vercel.

## Arquivos Criados/Modificados

- `vercel.json`: Configuração do Vercel para rotas e builds
- `api/index.py`: Handler serverless que importa e exporta o app FastAPI
- `requirements.txt`: Dependências do projeto (na raiz)
- `.vercelignore`: Arquivos e diretórios ignorados no deploy
- `app/db/session.py`: Ajustado para suporte serverless com NullPool

## Como fazer o deploy

### 1. Instalar Vercel CLI (se ainda não tiver)
```bash
npm i -g vercel
```

### 2. Fazer login no Vercel
```bash
vercel login
```

### 3. Deploy
```bash
vercel
```

Ou para produção:
```bash
vercel --prod
```

## Variáveis de Ambiente Necessárias

Configure as seguintes variáveis no painel do Vercel (Settings > Environment Variables):

- `DATABASE_URL`: URL de conexão do PostgreSQL (ex: `postgresql://user:password@host:port/database`)
- `SECRET_KEY`: Chave secreta para JWT (gerar uma chave segura)
- Outras variáveis de ambiente que seu projeto usa (ex: API keys, etc.)

## Estrutura do Projeto

```
licita_backend/
├── api/
│   └── index.py          # Handler serverless do Vercel
├── app/
│   ├── main.py           # App FastAPI principal
│   ├── api/
│   ├── core/
│   ├── db/
│   └── ...
├── vercel.json           # Configuração do Vercel
├── requirements.txt      # Dependências Python
└── .vercelignore        # Arquivos ignorados no deploy
```

## Notas Importantes

1. **Banco de Dados**: O projeto usa PostgreSQL. Certifique-se de que o banco está acessível do Vercel e configure a variável `DATABASE_URL` corretamente.

2. **Connection Pooling**: O código foi ajustado para usar `NullPool` no ambiente serverless, o que é apropriado para funções serverless.

3. **Timeout**: Por padrão, o Vercel tem um timeout de 10 segundos para planos Hobby. Considere o plano Pro para timeouts maiores se necessário.

4. **Cold Starts**: Como é serverless, pode haver cold starts. Considere usar Vercel Pro para melhor performance.

5. **Rotas**: Todas as rotas estão configuradas com o prefixo `/api`. Por exemplo:
   - `/api/` - Health check
   - `/api/docs` - Documentação Swagger
   - `/api/auth/...` - Rotas de autenticação
   - etc.

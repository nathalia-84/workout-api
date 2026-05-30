# TODO — Ordem de Desenvolvimento Sugerida

- [x] **Configuração Base do Projeto**: Implementar a stack (FastAPI, Python 3.11+, Pydantic v2). Configurar a conexão assíncrona com MongoDB (Motor) em `app/core/database.py`. Incluir variáveis de ambiente essenciais (e.g., `MONGO_URI`, `JWT_SECRET`) e configurar o ambiente com Docker e Docker Compose. 

- [ ] **Módulo de Autenticação (Auth)**: Implementar as rotas `POST /auth/register` (cadastro) e `POST /auth/login` (retorna JWT). Configurar a lógica de geração e validação de JWT em `app/core/security.py`. Criar a dependência `get_current_user` em `app/core/dependencies.py` para proteger rotas.

- [x] **Seed de Catálogo (`muscle_groups` e `exercises`)**: Criar os scripts em `seeds/` para popular as coleções de catálogo de grupos musculares e exercícios. O modelo `exercises` deve suportar filtros por `muscle_group_id`, `difficulty` e `equipment`. 

- [x] **CRUD de Workouts**: Implementar o CRUD completo (POST, GET, PUT, DELETE) na rota `/workouts`, focando na modelagem que armazena a lista de exercícios de um usuário com detalhes de séries e cargas (`reps`, `load_kg`).

- [ ] **CRUD de Training Plans**: Implementar o CRUD completo (POST, GET, PUT, DELETE) na rota `/training-plans`, focando na modelagem do agendamento (`schedule`) que referencia os treinos criados.

- [ ] **Sessões de Treino e Máquina de Estados**: Implementar as rotas para criar e gerenciar sessões. Criar a lógica da Máquina de Estados de Sessões (`pending -> in_progress -> paused -> completed`) em `services/sessions.py` e as rotas PATCH de transição correspondentes.

- [ ] **Utilitários Genéricos de Listagem**: Desenvolver um utilitário reutilizável em `app/core/` para suportar paginação (`?page`, `?limit`), filtros dinâmicos (`?query`) e projeções de campo (`?fields`) em todas as listagens da API, aplicando-o às rotas de domínio (como `/workouts`, que hoje aceita apenas `limit`). A paginação deve usar `?page` (base 1) e `?limit` convertidos em `skip`/`limit`. Os filtros via `?query` recebem um JSON repassado ao Mongo (ex.: `{"age":{"$gt":18}}`, `{"name":{"$regex":"Bo"}}`), retornando erro quando o JSON for inválido. As projeções via `?fields` devem permitir incluir (`name`, `name,age`) ou excluir (`-name`) campos.

- [ ] **Tratamento de Erros e Logs**: Implementar o middleware de erro global em `app/middlewares/error_handler.py`. Revisar todas as rotas para garantir o retorno dos Códigos HTTP corretos (200, 201, 404, 422, etc.) e a aplicação de logging nativo em operações relevantes.

- [ ] **Documentação e Revisão Final**: Escrever o `README.md` com nome dos integrantes, descrição do projeto, tecnologias utilizadas, instruções de instalação e execução e exemplos de uso de todas as rotas (incluindo `?page`, `?limit`, `?query` e `?fields`). Revisar a cobertura de todos os requisitos e bônus do projeto, incluindo a validação Pydantic e a documentação Swagger/OpenAPI.

- [ ] **Deploy Online da API**: Publicar a API em um serviço de hospedagem (e.g., Render, Railway, Fly.io) com o MongoDB acessível (e.g., MongoDB Atlas), configurando as variáveis de ambiente de produção (`MONGO_URI`, `MONGO_DB_NAME`, `JWT_SECRET`) e documentando a URL pública no `README.md`.

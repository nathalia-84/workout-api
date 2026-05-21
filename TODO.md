# TODO — Ordem de Desenvolvimento Sugerida

- [x] **Configuração Base do Projeto**: Implementar a stack (FastAPI, Python 3.11+, Pydantic v2). Configurar a conexão assíncrona com MongoDB (Motor) em `app/core/database.py`. Incluir variáveis de ambiente essenciais (e.g., `MONGO_URI`, `JWT_SECRET`) e configurar o ambiente com Docker e Docker Compose. 

- [ ] **Módulo de Autenticação (Auth)**: Implementar as rotas `POST /auth/register` (cadastro) e `POST /auth/login` (retorna JWT). Configurar a lógica de geração e validação de JWT em `app/core/security.py`. Criar a dependência `get_current_user` em `app/core/dependencies.py` para proteger rotas.

- [x] **Seed de Catálogo (`muscle_groups` e `exercises`)**: Criar os scripts em `seeds/` para popular as coleções de catálogo de grupos musculares e exercícios. O modelo `exercises` deve suportar filtros por `muscle_group_id`, `difficulty` e `equipment`. 

- [ ] **CRUD de Workouts**: Implementar o CRUD completo (POST, GET, PUT, DELETE) na rota `/workouts`, focando na modelagem que armazena a lista de exercícios de um usuário com detalhes de séries e cargas (`reps`, `load_kg`).

- [ ] **CRUD de Training Plans**: Implementar o CRUD completo (POST, GET, PUT, DELETE) na rota `/training-plans`, focando na modelagem do agendamento (`schedule`) que referencia os treinos criados.

- [ ] **Sessões de Treino e Máquina de Estados**: Implementar as rotas para criar e gerenciar sessões. Criar a lógica da Máquina de Estados de Sessões (`pending -> in_progress -> paused -> completed`) em `services/sessions.py` e as rotas PATCH de transição correspondentes.

- [ ] **Utilitários Genéricos de Listagem**: Desenvolver um utilitário reutilizável em `app/core/` para suportar paginação (`?page`, `?limit`), filtros dinâmicos (`?query`) e projeções de campo (`?fields`) em todas as listagens da API.

- [ ] **Tratamento de Erros e Logs**: Implementar o middleware de erro global em `app/middlewares/error_handler.py`. Revisar todas as rotas para garantir o retorno dos Códigos HTTP corretos (200, 201, 404, 422, etc.) e a aplicação de logging nativo em operações relevantes.

- [ ] **Documentação e Revisão Final**: Escrever o `README.md` e revisar a cobertura de todos os requisitos e bônus do projeto, incluindo a validação Pydantic e a documentação Swagger/OpenAPI.

-- 1. Cria a Restrição de Chave Única no PNCP_ID (Se não existir)
-- Isso garante que não haja duplicatas na importação.
ALTER TABLE public.licitacoes_raw
ADD CONSTRAINT licitacoes_raw_pncp_id_key UNIQUE (pncp_id);

-- 2. Cria o Índice Composto para Filtros (Otimização de Busca)
CREATE INDEX IF NOT EXISTS idx_raw_filtros_composto 
ON public.licitacoes_raw (sistema_origem, codigo_modalidade);

-- 3. (Opcional, se a tabela não existia) Criação do Índice de Chave Primária
-- Se a tabela já existia, o PKEY já deve estar lá.
-- ALTER TABLE public.licitacoes_raw ADD PRIMARY KEY (id);

-- 1. Cria o Índice de Busca Otimizada (Índice em Expressão)
-- (valor_unitario * quantidade)
CREATE INDEX IF NOT EXISTS idx_itens_busca_otimizada 
ON public.licitacoes_itens 
USING btree (licitacao_id, valor_unitario, quantidade, (valor_unitario * quantidade) DESC);

-- 2. Cria o Índice de Cobertura (Covering Index)
-- Otimiza consultas que filtram pela expressão e retornam descrição/valores
CREATE INDEX IF NOT EXISTS idx_itens_order_cover 
ON public.licitacoes_itens 
USING btree ((valor_unitario * quantidade) DESC, licitacao_id) 
INCLUDE (descricao, valor_unitario, quantidade);

-- 3. Cria o Índice de Limite
CREATE INDEX IF NOT EXISTS idx_itens_order_limit 
ON public.licitacoes_itens 
USING btree ((valor_unitario * quantidade) DESC, licitacao_id);

-- 4. Cria a Chave Estrangeira (FK)
-- Garante a integridade referencial entre itens e licitações_raw
ALTER TABLE public.licitacoes_itens
ADD CONSTRAINT licitacoes_itens_licitacao_id_fkey 
FOREIGN KEY (licitacao_id) REFERENCES licitacoes_raw(id);
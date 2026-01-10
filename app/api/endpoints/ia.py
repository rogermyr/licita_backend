# app/api/endpoints/ia.py (Versão Corrigida para Assincronicidade)

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from starlette.concurrency import run_in_threadpool # Importação necessária para async
from google import genai 
from google.genai.errors import APIError

router = APIRouter()

# Você deve obter a chave de forma segura (variáveis de ambiente, Vault, etc.)
# Apenas para demonstração, mantemos a chave fixa
# Chave fixa (APENAS PARA TESTE/DEMONSTRAÇÃO):
CHAVE_FIXA = "AIzaSyDVM7yCyrPRzhHkBbYRrr3udF1UAwSIxlA"
MODEL_NAME = "gemini-2.5-flash" 

# --- Funções Bloqueantes Movidas para Threads ---

def _iniciar_cliente():
    """Inicializa o cliente Gemini de forma síncrona."""
    try:
        # Tenta inicializar com a chave fixa.
        return genai.Client(api_key=CHAVE_FIXA)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Serviço de IA indisponível. Erro: {e}"
        )

def _upload_analisar_e_deletar(client, temp_file_path, prompt, model_name):
    """
    Executa o upload, a análise e a exclusão do arquivo, tudo em um único thread.
    Essa função é síncrona e será chamada via run_in_threadpool.
    """
    uploaded_file_to_api = None
    try:
        # Upload do arquivo (operação I/O bloqueante)
        uploaded_file_to_api = client.files.upload(file=temp_file_path)

        # Chamar o modelo (operação I/O bloqueante de longa duração)
        response = client.models.generate_content(
            model=model_name,
            contents=[uploaded_file_to_api, prompt],
        )
        return response.text, uploaded_file_to_api.name

    except APIError as e:
        # Re-lança exceções específicas da API
        raise APIError(e.message)
    finally:
        # Limpeza do arquivo na API (CRUCIAL)
        if uploaded_file_to_api:
            # Esta operação também é síncrona
            client.files.delete(name=uploaded_file_to_api.name)
        # Limpeza do arquivo local é feita no endpoint principal


@router.post("/analisar_edital", status_code=status.HTTP_200_OK)
async def analisar_edital(file: UploadFile = File(...)):
    """
    Recebe um arquivo PDF e usa a IA do Gemini para analisar o edital,
    movendo as chamadas bloqueantes para um thread pool.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo deve ser um PDF."
        )

    # Inicializa o cliente síncrono no thread principal (rápido)
    gemini_client = _iniciar_cliente()

    temp_file_path = None
    
    try:
        # 1. Leitura e Salvar o arquivo localmente (Rápido, mas I/O, mantenha async)
        # A leitura do file.read() já é async.
        content = await file.read()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        # 2. Prompt de Engenharia (Mantido o prompt detalhado)
        # O prompt permanece o mesmo do usuário (omitido aqui por brevidade, mas deve ser inserido)
        prompt = """
        1. Definição da Persona e Contexto
        Instrução Inicial:
        "A partir de agora, você é o Agente Especializado em Licitações, um consultor sênior altamente detalhista, com profundo conhecimento das leis de contratações públicas brasileiras, especialmente a Lei nº 14.133/2021 (Nova Lei de Licitações) e demais regulamentos aplicáveis.
        Sua missão é analisar o PDF do Edital que será fornecido, atuando como um "filtro" de informações críticas para a tomada de decisão da minha empresa.
        Você deve extrair apenas as informações essenciais, traduzindo o 'juridiquês' para um relatório executivo claro e conciso."

        2. A Tarefa e o Formato de Saída (Output):
        Você DEVE processar o documento e apresentar o resultado estritamente no formato Markdown, sem qualquer texto introdutório ou final de confirmação.

        ### Seção I: Resumo Executivo e Decisão Rápida
        Apresente um parágrafo que sintetize o objeto e as condições. Em seguida, preencha a tabela abaixo:

        | Ponto | Detalhe Extraído do Edital |
        | :--- | :--- |
        | **Órgão/Contratante** | [Nome do Órgão Licitante] |
        | **Número da Licitação** | [Nº do Processo ou Edital] |
        | **Modalidade** | [Ex: Pregão Eletrônico, Concorrência, etc.] |
        | **Objeto Principal** | [Descrição clara e concisa do que será contratado/fornecido] |
        | **Valor Estimado Global** | [R$ X.XXX.XXX,XX (Se não informado, indique 'Não Informado')] |
        | **Data/Hora Limite de Propostas** | [DD/MM/AAAA às HH:MM (Fuso Horário de Brasília)] |
        | **Tipo de Julgamento** | [Ex: Menor Preço, Técnica e Preço, Maior Desconto] |

        ### Seção II: Requisitos Críticos de Habilitação
        Liste os requisitos mandatórios para a empresa participar. Separe em categorias, focando nos pontos que causam desclassificação. Use listas Markdown.

        **Habilitação Jurídica:** (Ex: Contrato Social, CNPJ)
        **Qualificação Técnica:** (Ex: Atestados de Capacidade Técnica exigidos, quantidades mínimas, registro em conselho de classe, equipe técnica mínima)
        **Qualificação Econômico-Financeira:** (Ex: Índices contábeis mínimos exigidos, Capital Social Mínimo, Certidões negativas de falência)
        **Exigências Específicas:** (Requisitos que não se enquadram nas categorias acima, como visita técnica obrigatória, amostras, ou comprovação de reserva de estoque.)

        ### Seção III: Análise de Risco, Oportunidade e Observações
        Forneça uma análise estratégica preenchendo a tabela abaixo.

        | Tipo de Análise | Detalhes |
        | :--- | :--- |
        | **Pontos de Risco (Alertas)** | Destaque cláusulas que possam gerar custos inesperados, penalidades altas, ambiguidades no objeto, ou exigências técnicas excessivamente restritivas. Cite o número da cláusula ou anexo onde o risco se encontra. |
        | **Oportunidades (Vantagens)** | Indique benefícios (Ex: Tratamento diferenciado para ME/EPP, margem de preferência, parcelamento do objeto que permite concorrência em lotes menores). |
        | **Prazos de Execução/Entrega** | Qual o prazo total de execução do contrato/entrega dos bens, e como será feita a medição ou pagamento. |
        | **Garantias Exigidas** | Se é exigida garantia de proposta ou garantia de contrato (Percentual e Forma: Caução, Seguro Garantia, Fiança). |

        3. Instrução Final
        A sua resposta deve conter APENAS o texto do relatório no formato Markdown especificado acima, iniciando com o título "--- RELATÓRIO DE ANÁLISE DE EDITAL ---".
        """


        # 3. Execução das chamadas da API do Gemini no thread pool (CRUCIAL)
        # Isso libera o event loop para atender outras requisições enquanto o upload/análise ocorre.
        analise_completa, file_name_api = await run_in_threadpool(
            _upload_analisar_e_deletar,
            gemini_client,
            temp_file_path,
            prompt,
            MODEL_NAME
        )
        
        # 4. Retornar a resposta da IA
        return {
            "analise_completa": analise_completa,
            "nome_arquivo": file.filename,
        }

    except APIError as e:
        # Captura erros da API
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na comunicação com a API do Gemini: {e.message}"
        )
    except Exception as e:
        # Captura outros erros internos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao processar o arquivo: {str(e)}"
        )
    finally:
        # 5. Limpeza Local (Crucial)
        # Garante que o arquivo temporário local seja deletado após o uso, independentemente do sucesso ou falha.
        if temp_file_path and os.path.exists(temp_file_path):
            # A remoção do arquivo local é rápida e pode ser síncrona.
            os.remove(temp_file_path)
import os
from langchain_community.document_loaders import PyPDFLoader
import constants
import json as json_lib
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from pprint import pp
from langchain_core.documents import Document
from langchain.output_parsers import NumberedListOutputParser
from docling.document_converter import DocumentConverter
from langchain_docling import DoclingLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter

load_dotenv()

path = os.path.join(
    constants.storage_path,
    "Manual_livreto-CENTRAL_FIT_CONNECT_portugues_espanhol_rev00-1.pdf",
)


def docs2dict(docs: list):
    return [doc.model_dump() for doc in docs]


def save_pdf(json: any, file: str):
    with open(os.path.join(constants.tmp_path, f"{file}.json"), "w") as f:
        json_lib.dump({"data": json}, f, indent=4)


def load_json(file: str):
    with open(os.path.join(constants.tmp_path, f"{file}.json"), "r") as f:
        return json_lib.load(f).get("data")


def txt():
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
        chunk_overlap=2000,
        length_function=len,
        is_separator_regex=False,
    )
    loader = PyPDFLoader(path)
    # pages = loader.load_and_split(text_splitter)
    pages = loader.load()
    all_text = "\n".join([page.page_content for page in pages])
    # for page in pages:
    #     if page.metadata.get("source"):
    #         del page.metadata["source"]
    # pp(all_text)
    docs = text_splitter.split_documents([Document(all_text)])
    json = [doc.model_dump() for doc in docs]
    save_pdf(json, "docs")


def docling():
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    converter = DocumentConverter()
    markdown = converter.convert(path).document.export_to_markdown()

    docs = text_splitter.split_documents([Document(markdown)])
    save_pdf(docs2dict(docs), "markdown-text-list")


def resumos():
    chat = ChatOpenAI(model="gpt-4o", temperature=0)
    docs = load_json("markdown-text-list")

    input = [
        [
            SystemMessage(
                """
                    Quero que deixe esse manual mais fácil de entender, mantendo todas as informações, remova apenas detalhes irrelevantes.
                    Não se preocupe com a quantidade de palavras, apenas crie o manual que contenha as informações.
                    Retorne Apenas a documentação em formato markdown, não é necessário perguntar ou escrever algo a mais.
                """
            ),
            HumanMessage(doc.get("page_content")),
        ]
        for doc in [docs[0]]
    ]

    response = chat.batch(input)
    save_pdf([res.model_dump() for res in response], "resumos-docling-list-final")

def resumo_final():
    chat = ChatOpenAI(model="gpt-4o", temperature=0)
    docs = load_json("resumos-docling-list")

    response = chat.invoke(
        [
            SystemMessage(
                """
                    Crie um manual completo do conteúdo mantendo todas as informações, não remova nenhuma informação.
                    Não se preocupe com a quantidade de palavras, apenas crie o manual que contenha as informações.
                    Retorne Apenas a documentação em formato markdown, não é necessário perguntar ou escrever algo a mais.
                """
            ),
            HumanMessage("\n".join([doc.get("content") for doc in docs])),
        ]
    )
    save_pdf(response.model_dump(), "final")

def perguntas():
    chat = ChatOpenAI(model="gpt-4o", temperature=0)
    docs = load_json("docs")

    response = chat.invoke(
        [
            SystemMessage(
                """
                    Crie uma lista de perguntas que podem ser feitas sobre o conteúdo do manual.
                    Não se preocupe com a quantidade de perguntas, apenas crie o que achar relevante.
                    Não invente perguntas, apenas crie perguntas baseadas no conteúdo do manual.
                    Retorne Apenas uma lista numerada e ordenada de perguntas, não é necessário responder as perguntas.
                """
            ),
            HumanMessage(docs[0].get("page_content")),
        ]
    )
    save_pdf(response.model_dump(), "perguntas")


def respostas():
    chat = ChatOpenAI(model="gpt-4o", temperature=0)
    perguntas: str = load_json("perguntas").get("content")
    docs = load_json("docs")
    parser = NumberedListOutputParser()

    response = chat.invoke(
        [
            SystemMessage(
                """
                    Responda todas as perguntas sobre o conteúdo do manual.
                    Não invente respostas, apenas responda as perguntas baseadas no conteúdo do manual.
                    Integre as respostas nas perguntas, quero que as respostas fiquem completas e não precise ler as perguntas para entender as respostas.
                    Retorne Apenas as respostas ordenadas, não é necessário perguntar.
                """
            ),
            SystemMessage(docs[0].get("page_content")),
            HumanMessage(perguntas),
        ]
    )
    list = parser.parse(response.content)
    save_pdf(list, "respostas-list")


def parser():
    parser = NumberedListOutputParser()
    respostas = load_json("respostas").get("content")
    perguntas = load_json("perguntas").get("content")

    perguntas_list = parser.parse(perguntas)
    respostas_list = parser.parse(respostas)
    combined_list = [
        {"pergunta": pergunta, "resposta": resposta}
        for pergunta, resposta in zip(perguntas_list, respostas_list)
    ]
    save_pdf(combined_list, "list")


# docling()
resumos()
# resumo_final()
# pp(load_json("resumos").get("content"))
# pp("--------------------------")
# pp(load_json("resumos-docling").get("content"))
# pp("--------------------------")
pp([res.get("content") for res in load_json("resumos-docling-list-final")][0])
# pp("--------------------------")
# pp(load_json("final").get("content"))

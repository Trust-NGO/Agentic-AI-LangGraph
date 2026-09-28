from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
separators=[ "\n\n", # First try paragraph boundaries
            "\n",# Then line boundaries
            " ",# Then word boundaries
            "", # Finally character boundaries
        ],
    chunk_size=1000,
    chunk_overlap=200
)

def split_documents(documents):
    #print(f"split doc:{documents}")
    if not documents:
        raise FileNotFoundError("Document is not loaded")

    chunks = text_splitter.split_documents(documents)
    print(f"Original documents Count: {len(documents)}")
    print(f"Generated chunks : {len(chunks)}")
    return chunks
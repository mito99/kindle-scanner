import os
from dotenv import load_dotenv
from llama_parse import LlamaParse

load_dotenv()
api_key = os.getenv("LLAMA_CLOUD_API_KEY")


def main():
    parser = LlamaParse(
        api_key=api_key, result_type="markdown", mode="acurate", language="ja"
    )

    documents = parser.load_data("output.pdf")
    with open("output.md", "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(doc.text + "\n\n")

# 
if __name__ == "__main__":
    main()

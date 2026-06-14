import os
import re


def generate_credits():
    print("--- Credit Generator for CREDITS.md ---")

    # 1. Gather basic input
    name = input("Input asset name (e.g., Align Right Icon):\n> ")
    link = input("Input link:\n> ")

    print("\nPlease paste the details block below.")
    print("Include COLLECTION:, LICENSE:, and AUTHOR: lines (then press Ctrl+D or Ctrl+Z + Enter to finish):")

    # Reading multi-line input safely
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break
    details_text = "\n".join(lines)

    # 2. Extract information using Regex
    # re.IGNORECASE makes it resilient to "Collection:" or "COLLECTION:"
    # (.*?)(?=\n|$体) captures everything on that line until a newline or end of string
    collection_match = re.search(
        r"COLLECTION:\s*(.*)", details_text, re.IGNORECASE
    )
    license_match = re.search(r"LICENSE:\s*(.*)", details_text, re.IGNORECASE)
    author_match = re.search(
        r"(?:UPLOADER/AUTHOR|AUTHOR):\s*(.*)", details_text, re.IGNORECASE
    )

    # Extract the matched groups or default to "N/A" if not found
    collection = (
        collection_match.group(1).strip() if collection_match else "N/A"
    )
    license_type = (
        license_match.group(1).strip() if license_match else "N/A"
    )
    author = author_match.group(1).strip() if author_match else "N/A"

    # 3. Format into Markdown
    markdown_entry = f"- [{name}]({link})\n"
    markdown_entry += f"    - COLLECTION: {collection}\n"
    markdown_entry += f"    - LICENSE: {license_type}\n"
    markdown_entry += f"    - AUTHOR: {author}\n\n"


    print("\n-------------------------------------------------------------")
    print(markdown_entry)


if __name__ == "__main__":
    generate_credits()

#!/usr/bin/env python3

import argparse
import requests
import subprocess
import sys
import re
from bs4 import BeautifulSoup

# =========================
# Variables
# =========================

DEFAULT_MODEL_NAME = "llama3.2-vision:11b"
DEFAULT_MAX_CHARS = 500
EXAMPLE_URL = "https://example.com/article"

# =========================
# Functions
# =========================

def fetch_article(url):
    """
    Retrieve raw HTML from the given URL and return as text.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the article: {e}")
        sys.exit(1)
    return response.text

def extract_main_text(html_content):
    """
    Parse HTML and return the main textual content.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator="\n").strip()

def llama_run(model_name, prompt):
    """
    Call ollama with a given model name and prompt, returning the model's output.
    """
    result = subprocess.run(
        ["ollama", "run", model_name],
        input=prompt,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("Error running ollama command:", result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def remove_disclaimers_and_mentions(text):
    """
    Remove lines referencing 'rewrite', 'rewriting', 'the article', 'disclaimer', etc.
    Flatten into one paragraph.
    """
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        lower_line = line.lower().strip()
        if any(kw in lower_line for kw in ["rewrite", "rewriting", "disclaimer", "the article"]):
            continue
        cleaned_lines.append(line)
    paragraph = " ".join(cleaned_lines)
    paragraph = re.sub(r"\s+", " ", paragraph).strip()
    return paragraph

def strip_bullet_points(text):
    """
    Detect lines or inline segments that start with bullets, enumerations, or code blocks.
    Remove them or merge them into a single paragraph line.
    """
    lines = text.splitlines()
    cleaned_lines = []

    # Regex to detect bullets, enumerations, or code delimiters at line start:
    # e.g., '*', '-', '1.', '1)', or triple-backticks
    bullet_pattern = re.compile(r"^(\*|-|\d+\.)\s?|\d+\)\s?|^```")
    for line in lines:
        new_line = re.sub(bullet_pattern, "", line.strip())
        if new_line:
            cleaned_lines.append(new_line)

    # Flatten to a single paragraph
    paragraph = " ".join(cleaned_lines)
    paragraph = re.sub(r"\s+", " ", paragraph).strip()
    return paragraph

def enforce_character_limit(text, max_chars):
    """
    Strictly enforce a character limit; if truncated, end with a period.
    """
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars].rstrip()
    if not truncated.endswith("."):
        truncated += "."
    return truncated

def pass_one_summary(main_text, max_chars, model_name):
    """
    The first pass tries to produce a bullet-free, disclaimer-free summary in one go.
    """
    prompt_1 = (
        f"Produce a concise, single-paragraph TLDR of the text below in under {max_chars} characters. "
        "Do not include bullet points, enumerations, disclaimers, code listings, or references to rewriting. "
        "Simply provide the gist in plain text:\n\n"
        f"{main_text}\n\n"
        "Summary:"
    )
    output_1 = llama_run(model_name, prompt_1)
    return output_1

def pass_two_rewrite(first_pass_output, max_chars, model_name):
    """
    The second pass rewrites the summary if it still contains bullets, disclaimers, etc.
    """
    prompt_2 = (
        f"Rewrite the following text into a single paragraph under {max_chars} characters. "
        "Remove any bullet points, enumerations, disclaimers, code listings, or references to rewriting/the article. "
        "Do not apologize or explain. Just produce the final summary:\n\n"
        f"{first_pass_output}\n\n"
        "Final summary:"
    )
    output_2 = llama_run(model_name, prompt_2)
    return output_2

def summarize_text_with_llama(text, max_chars=DEFAULT_MAX_CHARS, model_name=DEFAULT_MODEL_NAME):
    """
    Two-pass approach to handle disclaimers and bullet points:
      1) Prompt to produce a bullet-free summary.
      2) If bullet points or disclaimers appear, second pass to rewrite them.
      3) Finally, do a post-processing scrub and enforce a character limit.
    """
    # --- PASS ONE ---
    first_pass = pass_one_summary(text, max_chars, model_name)

    # Check for bullet points or disclaimers in the first pass
    pass_one_cleaned = remove_disclaimers_and_mentions(first_pass)
    has_bullets = re.search(r"(\*|-|\d+\.)", pass_one_cleaned)  # inline detection

    if has_bullets:
        # --- PASS TWO ---
        second_pass = pass_two_rewrite(pass_one_cleaned, max_chars, model_name)
        second_pass_cleaned = remove_disclaimers_and_mentions(second_pass)
        final_text = strip_bullet_points(second_pass_cleaned)
    else:
        # If no bullet points found, proceed with pass one output
        final_text = strip_bullet_points(pass_one_cleaned)

    # Enforce character limit at the very end
    final_text = enforce_character_limit(final_text, max_chars)
    return final_text

def main():
    parser = argparse.ArgumentParser(
        description="Generate a bullet-free, disclaimer-free TL;DR from a local LLaMA model."
    )
    parser.add_argument(
        "-u", "--url",
        required=False,
        default=EXAMPLE_URL,
        help=f"URL of the article to summarize. Default: {EXAMPLE_URL}"
    )
    parser.add_argument(
        "-c", "--characters",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"Maximum number of characters for the summary. Default: {DEFAULT_MAX_CHARS}"
    )
    parser.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL_NAME,
        help=f"Local LLaMA model name to use with ollama. Default: {DEFAULT_MODEL_NAME}"
    )
    args = parser.parse_args()

    # Gather arguments, falling back to defaults if not specified
    max_chars = args.characters
    model_name = args.model
    url = args.url

    # Fetch and parse article
    html_content = fetch_article(url)
    main_text = extract_main_text(html_content)

    # Summarize
    summary = summarize_text_with_llama(
        text=main_text,
        max_chars=max_chars,
        model_name=model_name
    )

    print("\n--- SUMMARY ---\n")
    print(summary)
    print("\n---------------")

if __name__ == "__main__":
    main()

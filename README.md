# TL;DR Article Summarizer

This is a **two-pass summarizer** that generates concise, single-paragraph summaries of webpages using a local LLaMA-based model (via [ollama](https://github.com/jmorganca/ollama)). The script is designed to remove bullet points, enumerations, disclaimers, code listings, and references to “the article,” ensuring a clean TL;DR at or below a specified character limit.

---

## Subscribe to my Channels!
- **👉 Checkout some more awesome tools at [GetCyber](https://getcyber.me/tools)**
- **👉 Subscribe to my YouTube Channel [GetCyber - YouTube](https://youtube.com/getCyber)**
- **👉 Discord Server [GetCyber - Discord](https://discord.gg/YUf3VpDeNH)**

---

## Features

1. **Local Model**  
   - Uses a local LLaMA model through `ollama`; no external API calls.

2. **Two-Pass Summarization**  
   - **Pass One**: Tries to produce a bullet-free, disclaimer-free summary.  
   - **Pass Two**: If bullet points or disclaimers sneak in, it rewrites them in a second pass.

3. **Post-Processing**  
   - Removes any leftover disclaimers or references, merges everything into a single paragraph, and enforces a strict character limit.

4. **Configurable Defaults**  
   - Specify your preferred model name, default max characters, or an example URL at the top of the script.  
   - Override defaults via command-line arguments.

5. **CLI Usage**  
   - Simple command-line interface with `-u/--url`, `-c/--characters`, and `-m/--model`.

---

## Prerequisites

1. **Python 3.7+**  
   You’ll need Python 3.7 or later.

2. **[ollama](https://github.com/jmorganca/ollama)**  
   Install and configure ollama on your system, making sure you have a LLaMA-based model (e.g., `llama3.2-vision:11b`) available.

3. **Python Libraries**  
   - `requests`  
   - `beautifulsoup4`

---

## Installation

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/Dan-Duran/tldr.git
   cd tldr
   ```

2. **Create a Virtual Environment (Optional, but recommended)**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate       # On Linux or macOS
   # For Windows: .\venv\Scripts\activate
   ```

3. **Install Dependencies**  
   ```bash
   pip install requests beautifulsoup4
   ```
   *(Or just `pip install -r requirements.txt` if you create one.)*

4. **Confirm `ollama` Installation**  
   Ensure you can run `ollama` on the command line, and that your local model is downloaded. Example:
   ```bash
   ollama list
   # Should display your available models.
   ```

---

## Usage

Inside your project folder, run:

```bash
python tldr.py [options]
```

### Command-Line Arguments
- REQUIRED: **`-u` / `--url`**: URL of the article to summarize. Defaults to an example URL if not provided.  
- OPTIONAL: **`-c` / `--characters`**: Maximum number of characters (default defined at the top of `tldr.py`, e.g., 500).  
- OPTIONAL: **`-m` / `--model`**: The local model name to use (default is `llama3.2-vision:11b`).  

### Examples

1. **Using all defaults**  
   ```bash
   python tldr.py
   ```
   This will summarize the default `EXAMPLE_URL` using the default model and a 500-character limit.

2. **Specify a custom URL**  
   ```bash
   python tldr.py --url https://example.com/interesting-article
   ```

3. **Set a character limit of 300**  
   ```bash
   python tldr.py -u https://example.com/interesting-article -c 300
   ```

4. **Use a different local model**  
   ```bash
   python tldr.py -u https://example.com/interesting-article -m "jimscard/whiterabbit-neo:latest"
   ```

5. **Combine your own URL, character limit, and model**  
   ```bash
   python tldr.py --url https://example.com/another-article --characters 250 --model "qwen2.5-coder:14b"
   ```

---

## How It Works

1. **Pass One**  
   - The script instructs the model to produce a concise paragraph without bullet points, disclaimers, or enumerations.  

2. **Check & Rewrite**  
   - If bullet points or disclaimers are found, the script prompts the model a second time to remove them and produce a final summary.  

3. **Post-Processing**  
   - References to “the article,” disclaimers, or rewriting are removed.  
   - Any bullet points that remain are stripped out in code.  
   - Everything is merged into a single paragraph, then truncated to the desired character limit.

4. **Final Output**  
   - The summary is displayed in your terminal as a clean paragraph—no disclaimers, bullet points, or enumerations.

---

## Customization

- **Default Variables**: At the top of `tldr.py`, you’ll find:
  ```python
  DEFAULT_MODEL_NAME = "llama3.2-vision:11b"
  DEFAULT_MAX_CHARS = 500
  EXAMPLE_URL = "https://example.com/article"
  ```
  Adjust these as you see fit.

- **Regex Tweaks**: If you find certain bullet styles or disclaimers still sneaking through, you can enhance the regex or add more keywords in `remove_disclaimers_and_mentions`.

- **Model Parameters**: If `ollama` supports temperature or top-k/p flags, you could add them to the `subprocess.run` call in `llama_run`.

---

## Example Output

When successfully run, you should see output like:

```text
--- SUMMARY ---

This is a brief, single-paragraph overview of the content, stripped of bullet points and disclaimers.

---------------
```

---

## Contributing

1. **Fork** this repository.  
2. **Create** a new branch and commit your changes.  
3. **Open** a pull request in this repository describing your changes.

Bug reports, feature requests, and improvements are welcome!

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE). Feel free to use and modify this script as you see fit. Contributions are always welcome!

---

**Enjoy** your bullet-free, disclaimer-free, two-pass TL;DR Summarizer! If you have any questions, open an issue or reach out. Happy summarizing!

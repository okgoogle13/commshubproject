import os

target_dir = "/Users/okgoogle13/Downloads/Computer purchase"
files = [
  "Perplexity Results Stage 1.md",
  "Claude response stage 2.md",
  "Gemini Results Stage 1.md",
  "# STAGE 1: Local LLM + Multimodal Hardwa.md",
  "# STAGE 2_ Concrete Hardware Options for Local LLM (1).md",
  "ChatGPT Research - Stage 1 Strategic Landscape.md",
  "# STAGE 1_ Local LLM + Multimodal Hardware Landsca.md",
  "Claude Response Stage 1.md",
  "ChatGPT Research - Stage 2 Product Recommendations (AU).md",
  "Perplexity Results Stage 2.md",
  "consolidated_personal_shopper_product_doc.md",
  "# STAGE 2_ Concrete Hardware Options for Local LLM.md"
]

with open("tables.md", "w") as out:
    for f in files:
        full_path = os.path.join(target_dir, f)
        if not os.path.exists(full_path): continue
        with open(full_path, "r") as inf:
            lines = inf.readlines()
        
        in_table = False
        out.write(f"\n# FROM FILE: {f}\n")
        for line in lines:
            if "|" in line and "-" in line and "---" in line:
                pass # Header separator
            if line.strip().startswith("|") and line.strip().endswith("|"):
                out.write(line)

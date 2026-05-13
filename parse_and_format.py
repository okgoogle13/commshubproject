import os
import re
import csv

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
  "# STAGE 2_ Concrete Hardware Options for Local LLM.md",
  "Stage 1 Prompt.md",
  "Stage 2 Prompt.md"
]

def clean_text(text):
    text = re.sub(r'\[\^.*?\]', '', text) # Strip markdown footnotes
    text = re.sub(r'<[^>]+>', '', text) # Strip inline HTML
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return text.strip()

out_md = []
out_md.append("# Comprehensive LLM Recommendation Log\n")

# Phase 4 - By Source
out_md.append("## Recommendations by Source\n")

sources = {
    "ChatGPT": ["ChatGPT Research - Stage 1 Strategic Landscape.md", "ChatGPT Research - Stage 2 Product Recommendations (AU).md"],
    "Claude": ["Claude Response Stage 1.md", "Claude response stage 2.md"],
    "Gemini": ["Gemini Results Stage 1.md"],
    "Perplexity": ["Perplexity Results Stage 1.md", "Perplexity Results Stage 2.md"],
    "Manual Spreadsheet / Product Ledger": ["consolidated_personal_shopper_product_doc.md", "local_llm_hardware_options_ledger.csv"],
    "Unknown Source": ["# STAGE 1: Local LLM + Multimodal Hardwa.md", "# STAGE 1_ Local LLM + Multimodal Hardware Landsca.md", "# STAGE 2_ Concrete Hardware Options for Local LLM (1).md", "# STAGE 2_ Concrete Hardware Options for Local LLM.md"]
}

all_products = []

def parse_md_table(lines, source_name, source_file):
    header = []
    rows = []
    in_table = False
    for line in lines:
        if "|" in line:
            parts = [clean_text(p) for p in line.split("|")[1:-1]]
            if "---" in line and "-" in line:
                in_table = True
                continue
            if not in_table:
                header = parts
            else:
                if len(parts) > 1 and any(parts):
                    rows.append(parts)
        else:
            in_table = False
    
    # Process rows if they look like products
    for row in rows:
        row_str = " ".join(row).lower()
        if any(term in row_str for term in ["rtx", "mac", "ram", "gb", "ssd", "ryzen", "intel"]):
            # Try to map to standard columns: Product, Category, Status, Price, VRAM, RAM, Retailer, Rank, Source_File, Notes
            prod = row[0] if len(row) > 0 else "Unknown"
            if len(prod) < 3 or "description" in prod.lower() or "axis_name" in prod.lower():
                continue
            price = "Unknown"
            vram = "Unknown"
            ram = "Unknown"
            notes = " ".join(row[1:])
            for p in row:
                if "$" in p or "aud" in p.lower(): price = p
                if "vram" in p.lower() or ("gb" in p.lower() and "ram" not in p.lower() and "ssd" not in p.lower() and len(p) < 10): vram = p
                if "ram" in p.lower() or ("gb" in p.lower() and len(p) < 10 and "vram" not in p.lower()): ram = p
            
            all_products.append({
                "source": source_name,
                "file": source_file,
                "product": prod,
                "category": "Unknown", # Will categorize later
                "status": "Unknown",
                "price": price,
                "vram": vram,
                "ram": ram,
                "retailer": "Unknown",
                "rank": "Unknown",
                "notes": notes
            })

for source, s_files in sources.items():
    out_md.append(f"### {source}")
    out_md.append("| Product_or_Build_Name | Category | Status | Price_AUD | GPU_VRAM | RAM_GB | Retailer_or_Source | Rank_or_Score | Source_File | Notes |")
    out_md.append("|---|---|---|---:|---|---:|---|---|---|---|")
    
    for f in s_files:
        path = os.path.join(target_dir, f)
        if not os.path.exists(path):
            continue
        if f.endswith(".csv"):
            with open(path, "r") as csvf:
                reader = csv.DictReader(csvf)
                for row in reader:
                    prod = clean_text(row.get("Product / Build", "Unknown"))
                    if not prod or prod == "Unknown": continue
                    status = clean_text(row.get("Status", "Unknown"))
                    price = clean_text(row.get("Price AUD", "Unknown"))
                    vram = clean_text(row.get("VRAM or Unified GB", "Unknown"))
                    ram = clean_text(row.get("RAM / Unified", "Unknown"))
                    retailer = clean_text(row.get("Seller / Retailer", "Unknown"))
                    notes = clean_text(row.get("Notes", ""))
                    cat = clean_text(row.get("Screen / Form Factor", "Unknown"))
                    all_products.append({
                        "source": source,
                        "file": f,
                        "product": prod,
                        "category": cat,
                        "status": status,
                        "price": price,
                        "vram": vram,
                        "ram": ram,
                        "retailer": retailer,
                        "rank": "Unknown",
                        "notes": notes,
                        "cpu": clean_text(row.get("CPU", "Unknown")),
                        "url": clean_text(row.get("Source / Link", "Unknown")),
                        "storage": clean_text(row.get("Storage", "Unknown"))
                    })
                    out_md.append(f"| {prod} | {cat} | {status} | {price} | {vram} | {ram} | {retailer} | Unknown | {f} | {notes} |")
        else:
            with open(path, "r") as mdf:
                lines = mdf.readlines()
            
            # Simple heuristic extraction
            table_lines = [l for l in lines if "|" in l]
            parse_md_table(table_lines, source, f)

            # Re-read for all_products that were added from this file
            prods_this_file = [p for p in all_products if p['file'] == f and p['source'] == source]
            for p in prods_this_file:
                # To prevent duplicates if the CSV already added it
                if f.endswith(".csv"): continue
                out_md.append(f"| {p['product']} | {p['category']} | {p['status']} | {p['price']} | {p['vram']} | {p['ram']} | {p['retailer']} | {p['rank']} | {p['file']} | {p['notes']} |")

    out_md.append("\n")

# Phase 5 - Categorized Master Ledger
out_md.append("---\n\n# Categorized Master Ledger\n")

categories = {
    "Windows Towers": ["tower", "desktop", "build"],
    "Windows Laptops": ["laptop", "mobile"],
    "Mini PCs": ["mini", "oculink", "egpu"],
    "Apple Macs & Mac Minis": ["mac", "apple", "studio", "mbp", "m3", "m4", "m2"]
}

for cat_name, keywords in categories.items():
    out_md.append(f"### {cat_name}")
    out_md.append("| Model | Category | Price_AUD | CPU | GPU_VRAM | RAM_GB | Storage | URL | AI_Notes |")
    out_md.append("|---|---|---|---|---|---|---|---|---|")
    
    seen = set()
    for p in all_products:
        prod_lower = p['product'].lower()
        matched = any(k in prod_lower for k in keywords) or any(k in str(p.get('category', '')).lower() for k in keywords)
        
        # Override for specific matches
        if "mac" in prod_lower and cat_name != "Apple Macs & Mac Minis": matched = False
        if "laptop" in prod_lower and cat_name != "Windows Laptops": matched = False
        if "tower" in prod_lower and cat_name != "Windows Towers": matched = False
        if "mini" in prod_lower and cat_name != "Mini PCs": matched = False
        
        # Default to Windows Towers if nothing else matches (just to not drop anything)
        if not any(any(k in prod_lower or k in str(p.get('category', '')).lower() for k in keywords_inner) for keywords_inner in categories.values()):
            if cat_name == "Windows Towers":
                matched = True

        if matched:
            if p['product'] not in seen:
                seen.add(p['product'])
                cpu = p.get('cpu', 'Unknown')
                storage = p.get('storage', 'Unknown')
                url = p.get('url', 'Unknown')
                out_md.append(f"| {p['product']} | {p.get('category', 'Unknown')} | {p['price']} | {cpu} | {p['vram']} | {p['ram']} | {storage} | {url} | {p['notes']} |")
    out_md.append("\n")

with open("research/comprehensive_llm_recommendation_log.md", "w") as f:
    f.write("\n".join(out_md))


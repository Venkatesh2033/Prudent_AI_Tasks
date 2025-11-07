# generate_transactions
from datetime import datetime
import random, os, textwrap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

OUT_DIR = "C:/Users/venky/OneDrive/Desktop/prudent task"
os.makedirs(OUT_DIR, exist_ok=True)

currencies = [("$", "USD"), ("₹", "INR"), ("€", "EUR"), ("£", "GBP")]
types = ["CREDIT", "DEBIT"]
prefixes = ["AB", "XY", "INR", "HH", "EURO", "TX", "CN", "US"]

# --- Helpers ---
def gen_id(prefix):
    return f"{prefix}{random.randint(10, 999)}"

def fmt_amount(val, cur):
    if random.random() < 0.3:
        return f"{cur}{val:,.2f}"
    else:
        return f"{cur}{val:.2f}"

# --- Generate normal transactions ---
transactions = []
for _ in range(38):
    ttype = random.choice(types)
    cur, cname = random.choice(currencies)
    amt = round(random.uniform(100, 80000), 2)
    tid = gen_id(random.choice(prefixes))
    transactions.append(f"TXN:{ttype.ljust(6)} | AMT:{fmt_amount(amt, cur)} | ID:{tid}")

# --- Add controlled anomalies ---
malicious = [
    
    "TXN:DEBIT  | AMT:$250000.00 | ID:BIGTXN1",
    
    "TXN:CREDIT | AMT:-₹5000.00 | ID:NEG001",
    
    "TXN:DEBIT  | AMT:$0.00 | ID:ZERO001",
    
    "TXN:CREDIT | AMT:¤1234.56 | ID:UNKN01",

    "TXN:DEBIT  | AMT:$1500.00 | ID:OR'1'='1';--", # SQL injection
    "TXN:CREDIT | AMT:$250.00 | ID:<script>alert(1)</script>", # XSS injection
    
    "TXN:DEBIT  | AMT:$10000.00 | ID:DUP100",
    "TXN:CREDIT | AMT:$12000.00 | ID:DUP100",
    
    "MALFORMED ENTRY - AMT:$1000 ID:",
    
    "TXN:CREDIT | AMT:500USD | ID:SUF01",
    
    "TXN:DEBIT  | AMT:$0.05 | ID:FRAC01",

    "TXN:CREDIT | ID:MISSINGAMT"
]
for m in malicious:
    pos = random.randint(0, len(transactions))
    transactions.insert(pos, m)

transactions = transactions[:50]

# --- Write .log file ---
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
header = f"# Transaction Log generated: {now}\n"
log_path = os.path.join(OUT_DIR, "transactions_fixed.log")
with open(log_path, "w", encoding="utf-8") as f:
    f.write(header)
    for line in transactions:
        f.write(line + "\n")

pdf_path = os.path.join(OUT_DIR, "transactions.pdf")
wrapped_lines = []
for line in transactions:
    wrapped = textwrap.wrap(line, width=100)
    wrapped_lines.extend(wrapped)

page_lines_per_page = 45
pages = [wrapped_lines[i:i+page_lines_per_page] for i in range(0, len(wrapped_lines), page_lines_per_page)]

with PdfPages(pdf_path) as pdf:
    for page in pages:
        fig = plt.figure(figsize=(8.27, 11.69))
        plt.axis("off")
        txt = "\n".join(page)
        plt.text(0.02, 0.98, header + txt, va="top", family="monospace", fontsize=9)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

print(f"✅ New dataset generated:\n  {log_path}\n  {pdf_path}")

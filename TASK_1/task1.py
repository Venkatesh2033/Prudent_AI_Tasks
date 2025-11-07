import re
import io
import pdfplumber
import pytesseract
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
import gradio as gr

def extract_text_from_file(file_obj):
    
    if file_obj is None:
        return ""

    name = file_obj.name.lower()

    # --- Text-based files ---
    if name.endswith((".txt", ".log", ".csv")):
        return file_obj.read().decode("utf-8", errors="ignore")

    # --- PDF files ---
    elif name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    # --- Image files (OCR) ---
    elif name.endswith((".png", ".jpg", ".jpeg")):
        image = Image.open(file_obj)
        text = pytesseract.image_to_string(image)
        return text

    else:
        return "⚠️ Unsupported file format."

def extract_transactions(log_text: str):
    pattern = r"TXN:([A-Z]+)\s*\|\s*AMT:\s*([$₹€]?)([\d,]+(?:\.\d+)?)\s*\|\s*ID:([A-Za-z0-9]+)"
    matches = re.findall(pattern, log_text)
    results = []
    for txn_type, currency, amount_str, txn_id in matches:
        amount = float(amount_str.replace(',', ''))
        currency = currency if currency else "N/A"
        results.append((txn_type, amount, txn_id, currency))
    return results

def build_dataframe(log_text: str) -> pd.DataFrame:
    data = extract_transactions(log_text)
    df = pd.DataFrame(data, columns=["Type", "Amount", "ID", "Currency"])
    return df

def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    model = IsolationForest(contamination=0.15, random_state=42)
    df["Anomaly"] = model.fit_predict(df[["Amount"]])
    return df

def plot_summary(df: pd.DataFrame):
    if df.empty:
        return None
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    sns.barplot(x="Type", y="Amount", data=df, estimator=sum, ax=axes[0])
    axes[0].set_title("Total Transaction Amount per Type")

    sns.boxplot(x="Type", y="Amount", data=df, hue="Anomaly", palette="Set2", ax=axes[1])
    axes[1].set_title("Anomaly Visualization")
    axes[1].legend(title="Anomaly (-1 = outlier)")
    plt.tight_layout()
    return fig

def process_input(file_obj, manual_text):
    # 1️⃣ Prefer file if uploaded, else use manual text
    if file_obj is not None:
        text = extract_text_from_file(file_obj)
    else:
        text = manual_text or ""

    if not text.strip():
        return "⚠️ No valid input text found.", None, None

    # 2️⃣ Extract, analyze, visualize
    df = build_dataframe(text)
    if df.empty:
        return "⚠️ No valid transactions found in this file.", None, None

    df = detect_anomalies(df)
    fig = plot_summary(df)

    summary = df.groupby("Type")["Amount"].agg(["count", "sum", "mean"])
    summary_text = f"📊 **Transaction Summary:**\n\n{summary.to_markdown()}"
    total = df["Amount"].sum()
    summary_text += f"\n\n💰 **Total Value:** {total:,.2f}\n"

    anomalies = df[df["Anomaly"] == -1]
    if not anomalies.empty:
        summary_text += f"\n🚨 **Anomalies Detected ({len(anomalies)}):**\n"
        summary_text += anomalies[["Type", "Amount", "ID"]].to_markdown()
    else:
        summary_text += "\n✅ No anomalies detected."

    return summary_text, df, fig

with gr.Blocks(title="Transaction Extractor (Regex + ML + OCR)") as demo:
    gr.Markdown("# 💳 Transaction Value Extractor\n### OCR + PDF + Regex + ML Detection")

    with gr.Row():
        file_input = gr.File(label="📁Upload File (.txt, .pdf, .jpg, .png, .csv)")
        manual_input = gr.Textbox(lines=6, label="Or Paste Transaction Log")

    analyze_btn = gr.Button("Analyze 🚀")

    output_summary = gr.Markdown()
    output_df = gr.Dataframe(label="Extracted Transactions")
    output_plot = gr.Plot(label="Visual Summary")

    analyze_btn.click(
        fn=process_input,
        inputs=[file_input, manual_input],
        outputs=[output_summary, output_df, output_plot]
    )

demo.launch(debug=True)


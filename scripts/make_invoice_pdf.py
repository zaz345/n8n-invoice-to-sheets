"""生成 n8n 演示用的发票 PDF（全虚构）。

用法：
    python make_invoice_pdf.py            # 生成全部
    python make_invoice_pdf.py brightwater  # 只生成指定的一张

输出写在同目录下。
"""
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).parent

DARK = colors.HexColor("#1f2937")
MUTED = colors.HexColor("#6b7280")
LINE = colors.HexColor("#e5e7eb")
BAND = colors.HexColor("#f3f4f6")

styles = getSampleStyleSheet()
h_brand = ParagraphStyle("brand", parent=styles["Normal"], fontName="Helvetica-Bold",
                         fontSize=17, leading=21, textColor=DARK)
small = ParagraphStyle("small", parent=styles["Normal"], fontName="Helvetica",
                       fontSize=8.4, leading=12, textColor=MUTED)
doc_title = ParagraphStyle("doctitle", parent=styles["Normal"], fontName="Helvetica-Bold",
                           fontSize=26, leading=30, textColor=DARK, alignment=2)
meta = ParagraphStyle("meta", parent=styles["Normal"], fontName="Helvetica",
                      fontSize=9, leading=14, textColor=DARK)
meta_r = ParagraphStyle("metar", parent=meta, alignment=2)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontName="Helvetica",
                      fontSize=8.8, leading=12, textColor=DARK)


SPECS = [
    {
        "key": "northwind",
        "file": "invoice_NW-2026-0442.pdf",
        "vendor": "NORTHWIND TRADERS LTD",
        "vendor_addr": ["Unit 7, Kestrel Business Park", "Reading RG2 6UB, United Kingdom"],
        "tax_line": "VAT GB 418 226 907",
        "client": "Halden Instrumentation GmbH",
        "client_addr": ["Werner-von-Siemens-Str. 12", "68159 Mannheim, Germany",
                        "Attn: Accounts Payable"],
        "number": "INV-2026-0442",
        "issued": "14 October 2026",
        "due": "13 November 2026",
        "terms": "Net 30",
        "currency": "USD",
        "items": [
            ("NW-1180", "Aluminium enclosure, 2U rack mount", 6, 184.00),
            ("NW-2094", "Thermal pad sheet, 100x100mm", 40, 6.75),
            ("NW-3310", "Cable harness, shielded, 1.5m", 24, 12.40),
            ("SVC-070", "Assembly and burn-in labour (hours)", 8, 62.50),
        ],
        "tax_rate": 0.20,
        "tax_label": "VAT 20%",
        "bank": ["Barclays Bank UK PLC", "Sort code 20-45-77", "Account 41822690",
                 "IBAN GB29 BARC 2045 7741 8226 90"],
    },
    {
        "key": "brightwater",
        "file": "invoice_BW-2026-1187.pdf",
        "vendor": "BRIGHTWATER LOGISTICS BV",
        "vendor_addr": ["Waalhaven Oostzijde 81", "3087 BM Rotterdam, Netherlands"],
        "tax_line": "VAT NL 8214 55 903 B01",
        "client": "Meridian Retail Group AG",
        "client_addr": ["Chausseestrasse 74", "10115 Berlin, Germany",
                        "Attn: Finance Department"],
        "number": "BW-2026-1187",
        "issued": "2 November 2026",
        "due": "2 December 2026",
        "terms": "Net 30",
        "currency": "EUR",
        "items": [
            ("FRT-40HC", "Ocean freight, 40ft high cube, RTM-SHA", 2, 620.00),
            ("CUS-EXP", "Export customs clearance and handling", 1, 285.00),
            ("DOC-BL", "Bill of lading and documentation fee", 1, 95.00),
        ],
        "tax_rate": 0.0,
        "tax_label": "VAT 0% (reverse charge)",
        "bank": ["ING Bank N.V.", "BIC INGBNL2A", "IBAN NL91 INGB 0006 3412 78"],
    },
    {
        "key": "atlas",
        "file": "invoice_AP-2026-0773.pdf",
        "vendor": "ATLAS PRINT & PACKAGING LTD",
        "vendor_addr": ["Unit 12, Calder Works", "Leeds LS10 1AB, United Kingdom"],
        "tax_line": "VAT GB 302 771 448",
        "client": "Kestrel Media Group",
        "client_addr": ["18 Fitzwilliam Square", "Dublin D02 YH79, Ireland",
                        "Attn: Accounts Payable"],
        "number": "AP-2026-0773",
        "issued": "6 November 2026",
        "due": "15 December 2026",
        "terms": "Net 39",
        "currency": "GBP",
        "items": [
            ("PRT-A4-8PP", "A4 brochure, 8pp, 170gsm silk, print run", 5000, 0.42),
            ("PRT-DL-ENV", "DL window envelopes, self-seal", 5000, 0.06),
            ("FIN-SADDLE", "Saddle-stitch finishing and trim", 1, 340.00),
            ("DEL-PALLET", "Palletised delivery, Leeds to Dublin", 2, 118.50),
        ],
        "tax_rate": 0.20,
        "tax_label": "VAT 20%",
        "bank": ["Lloyds Bank plc", "Sort code 30-96-26", "Account 27314460",
                 "IBAN GB15 LOYD 3096 2627 3144 60"],
    },
]


def build(spec: dict) -> Path:
    out = HERE / spec["file"]
    doc = SimpleDocTemplate(
        str(out), pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title=f"Invoice {spec['number']}", author=spec["vendor"],
    )
    story = []

    vendor_html = (f"{spec['vendor']}<br/>"
                   f'<font size="8.4" color="#6b7280">'
                   + "<br/>".join(spec["vendor_addr"])
                   + f"<br/>{spec['tax_line']}</font>")
    head = Table(
        [[Paragraph(vendor_html, h_brand),
          Paragraph("INVOICE<br/>"
                    '<font size="8.4" color="#6b7280">Original copy</font>',
                    doc_title)]],
        colWidths=[100 * mm, 70 * mm],
    )
    head.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story += [head, Spacer(1, 9 * mm)]

    meta_rows = [
        ("Invoice number", spec["number"]),
        ("Invoice date", spec["issued"]),
        ("Due date", spec["due"]),
        ("Payment terms", spec["terms"]),
        ("Currency", spec["currency"]),
    ]
    client_html = spec["client"] + "<br/>" + "<br/>".join(spec["client_addr"])
    left = [[Paragraph("<b>BILL TO</b>", small)],
            [Paragraph(client_html, meta)]]
    right = [[Paragraph(k, small), Paragraph(f"<b>{v}</b>", meta_r)]
             for k, v in meta_rows]

    lt = Table(left, colWidths=[80 * mm])
    lt.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    rt = Table(right, colWidths=[34 * mm, 36 * mm])
    rt.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                            ("TOPPADDING", (0, 0), (-1, -1), 1.5),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5)]))

    band = Table([[lt, rt]], colWidths=[90 * mm, 70 * mm])
    band.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 0),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story += [band, Spacer(1, 9 * mm)]

    data = [["SKU", "Description", "Qty", "Unit price", "Amount"]]
    subtotal = 0.0
    for sku, desc, qty, unit in spec["items"]:
        amt = qty * unit
        subtotal += amt
        data.append([sku, Paragraph(desc, cell), str(qty), f"{unit:,.2f}", f"{amt:,.2f}"])
    tax = round(subtotal * spec["tax_rate"], 2)
    total = round(subtotal + tax, 2)

    items = Table(data, colWidths=[24 * mm, 76 * mm, 14 * mm, 28 * mm, 28 * mm],
                  repeatRows=1)
    items.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.8),
        ("TEXTCOLOR", (0, 0), (-1, 0), MUTED),
        ("BACKGROUND", (0, 0), (-1, 0), BAND),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, MUTED),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE),
    ]))
    story += [items, Spacer(1, 6 * mm)]

    cur = spec["currency"]
    tot = Table(
        [["", "Subtotal", f"{subtotal:,.2f} {cur}"],
         ["", spec["tax_label"], f"{tax:,.2f} {cur}"],
         ["", "Total due", f"{total:,.2f} {cur}"]],
        colWidths=[90 * mm, 40 * mm, 40 * mm],
    )
    tot.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TEXTCOLOR", (1, 0), (-1, -1), DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("FONTNAME", (1, 2), (-1, 2), "Helvetica-Bold"),
        ("FONTSIZE", (1, 2), (-1, 2), 10.5),
        ("LINEABOVE", (1, 2), (-1, 2), 0.8, DARK),
    ]))
    story += [tot, Spacer(1, 10 * mm)]

    story.append(Paragraph(
        "<b>Payment details</b> &nbsp; " + " &nbsp;|&nbsp; ".join(spec["bank"])
        + "<br/>Please quote the invoice number on the transfer.",
        small))

    doc.build(story)
    print(f"{out.name}  {out.stat().st_size / 1024:.1f} KB   "
          f"subtotal={subtotal:.2f} total={total:.2f} {cur}")
    return out


if __name__ == "__main__":
    want = sys.argv[1] if len(sys.argv) > 1 else None
    for s in SPECS:
        if want is None or want == s["key"]:
            build(s)

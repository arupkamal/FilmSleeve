#!/usr/bin/env python3
"""Tkinter GUI for generating 5 x 6 cm film-sleeve QR labels."""

from datetime import datetime
from pathlib import Path
from io import BytesIO
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import qrcode
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.units import cm, mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
except ImportError as exc:
    print("Missing dependency:", exc)
    print('Install with: python3 -m pip install reportlab "qrcode[pil]"')
    sys.exit(1)

PAPERS = {"A4": A4, "LETTER": letter}
LABEL_W, LABEL_H = 5 * cm, 6.5 * cm
GAP = 5 * mm
SERIAL_WIDTH = 4


def get_prefix():
    while True:
        value = input("Sleeve prefix (1–20 characters): ").strip().upper()
        if not value:
            print("Prefix cannot be blank.")
        elif len(value) > 20:
            print("Prefix must be 20 characters or fewer.")
        elif any(ord(ch) < 32 for ch in value):
            print("Control characters are not allowed.")
        else:
            return value


def get_start():
    while True:
        try:
            n = int(input("Starting serial (integer, minimum 1): ").strip())
            if n >= 1:
                return n
        except ValueError:
            pass
        print("Enter a whole number of at least 1.")


def qr_buffer(value):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=8, border=2)
    qr.add_data(value)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return buf


def draw_label(pdf, x, y, sleeve_type, stock_prefix, serial, timestamp):
    # Solid rounded label perimeter.
    pdf.saveState()
    pdf.setStrokeColor(colors.HexColor("#263746"))
    pdf.setLineWidth(0.9)
    pdf.setDash()
    pdf.roundRect(x, y, LABEL_W, LABEL_H, 3 * mm, stroke=1, fill=0)
    pdf.restoreState()

    # Sleeve type and serial.
    pdf.setFillColor(colors.HexColor("#34495E"))
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawCentredString(x + LABEL_W/2, y + LABEL_H - 5.2*mm,
                          stock_prefix)
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica-Bold", 10.5 if len(serial) <= 12 else 8)
    pdf.drawCentredString(x + LABEL_W/2, y + LABEL_H - 10.8*mm, serial)

    # QR code.
    # QR payload includes the full stock classification and visible serial.
    qr_value = f"{stock_prefix}/{serial}"
    qr_size = 23.4 * mm
    pdf.drawImage(ImageReader(qr_buffer(qr_value)),
                  x + (LABEL_W-qr_size)/2, y + LABEL_H - 10.8*mm - 2*mm - qr_size,
                  width=qr_size, height=qr_size,
                  preserveAspectRatio=True, mask="auto")

    # Index grid below QR: serial on the first line, letter on the second.
    # Reading order is left-to-right, top-to-bottom: #️⃣, serial-A ... serial-H.
    grid_w, grid_h = 16.5 * mm, 22 * mm
    cell_w, cell_h = grid_w / 3, grid_h / 3
    gx = x + (LABEL_W-grid_w)/2
    gy = y + 3.5*mm

    pdf.saveState()
    pdf.setStrokeColor(colors.HexColor("#263746"))
    pdf.setLineWidth(0.45)
    pdf.setDash()
    pdf.rect(gx, gy, grid_w, grid_h, stroke=1, fill=0)
    for k in (1, 2):
        pdf.line(gx+k*cell_w, gy, gx+k*cell_w, gy+grid_h)
        pdf.line(gx, gy+k*cell_h, gx+grid_w, gy+k*cell_h)

    # Tiny QR code in the first cell, encoding the same full value as the main QR.
    mini_qr_size = min(cell_h - 0.45*mm, cell_w - 1.0*mm)
    mini_qr_x = gx + (cell_w-mini_qr_size)/2
    mini_qr_y = gy + grid_h - cell_h + (cell_h-mini_qr_size)/2
    pdf.drawImage(ImageReader(qr_buffer(qr_value)),
                  mini_qr_x, mini_qr_y,
                  width=mini_qr_size, height=mini_qr_size,
                  preserveAspectRatio=True, mask="auto")

    for i, letter in enumerate("ABCDEFGH", start=1):
        row, col = divmod(i, 3)
        cx = gx + (col+0.5)*cell_w
        cy = gy + grid_h - (row+0.5)*cell_h
        pdf.setFillColor(colors.HexColor("#555555"))
        serial_font = 2.8
        available_width = cell_w - 0.8 * mm
        index_number = serial[-SERIAL_WIDTH:]
        while serial_font > 1.5 and pdf.stringWidth(index_number, "Helvetica", serial_font) > available_width:
            serial_font -= 0.1
        pdf.setFont("Helvetica", serial_font)
        pdf.drawCentredString(cx, cy+0.5*mm, index_number)
        pdf.setFillColor(colors.black)
        pdf.setFont("Helvetica-Bold", 5.2)
        pdf.drawCentredString(cx, cy-1.7*mm, letter)
    pdf.restoreState()

    # Tiny timestamp footer below the index grid.
    pdf.setFillColor(colors.HexColor("#555555"))
    pdf.setFont("Helvetica", 3.8)
    pdf.drawCentredString(x + LABEL_W/2, y + 1.5*mm, timestamp)


def draw_guides(pdf, left, bottom):
    grid_w = 3*LABEL_W + 2*GAP
    grid_h = 3*LABEL_H + 2*GAP
    pdf.saveState()
    pdf.setStrokeColor(colors.HexColor("#777777"))
    pdf.setLineWidth(0.6)
    pdf.setDash(2, 2)

    # Cut lines centred in the 5 mm gutters.
    for col in range(2):
        xx = left + (col+1)*LABEL_W + (col+0.5)*GAP
        pdf.line(xx, bottom, xx, bottom+grid_h)
    for row in range(2):
        yy = bottom + (row+1)*LABEL_H + (row+0.5)*GAP
        pdf.line(left, yy, left+grid_w, yy)

    # Outer dotted boundary exactly 5 mm beyond the outside label edges.
    offset = 5 * mm
    l, r = left-offset, left+grid_w+offset
    b, t = bottom-offset, bottom+grid_h+offset
    pdf.line(l, b, r, b)
    pdf.line(l, t, r, t)
    pdf.line(l, b, l, t)
    pdf.line(r, b, r, t)
    pdf.restoreState()


def create_pdf(paper, sleeve_type, prefix, start, output, film_type="NEG", color_mode="BW"):
    pw, ph = PAPERS[paper.upper()]
    grid_w = 3*LABEL_W + 2*GAP
    grid_h = 3*LABEL_H + 2*GAP
    left = (pw-grid_w)/2
    bottom = (ph-grid_h)/2
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    pdf = canvas.Canvas(str(output), pagesize=(pw, ph), pageCompression=1)
    pdf.setTitle(f"{color_mode}/{film_type}{sleeve_type}/{prefix} Film Sleeve Labels")
    pdf.setAuthor("Film Sleeve QR Label Generator")

    for i in range(9):
        row, col = divmod(i, 3)
        x = left + col*(LABEL_W+GAP)
        y = ph-bottom-LABEL_H-row*(LABEL_H+GAP)
        serial = f"{prefix}.{start+i:0{SERIAL_WIDTH}d}"
        stock_prefix = f"{color_mode}/{film_type}{sleeve_type}"
        draw_label(pdf, x, y, sleeve_type, stock_prefix, serial, stamp)

    draw_guides(pdf, left, bottom)
    pdf.showPage()
    pdf.save()



def main():
    root = tk.Tk()
    root.title("Film Sleeve QR Label Generator")
    root.resizable(False, False)
    root.minsize(430, 410)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    outer = ttk.Frame(root, padding=18)
    outer.grid(row=0, column=0, sticky="nsew")
    outer.columnconfigure(0, weight=1)

    ttk.Label(
        outer, text="Film Sleeve QR Label Generator",
        font=("TkDefaultFont", 15, "bold")
    ).grid(row=0, column=0, sticky="w", pady=(0, 4))
    ttk.Label(
        outer, text="Nine labels per page · 5 × 6.5 cm · 5 mm spacing"
    ).grid(row=1, column=0, sticky="w", pady=(0, 16))

    paper_var = tk.StringVar(value="LETTER")
    film_var = tk.StringVar(value="120")
    film_type_var = tk.StringVar(value="NEG")
    color_var = tk.StringVar(value="BW")
    prefix_var = tk.StringVar()
    start_var = tk.StringVar(value="1")
    filename_var = tk.StringVar()

    paper_box = ttk.LabelFrame(outer, text="Paper size", padding=10)
    paper_box.grid(row=2, column=0, sticky="ew", pady=(0, 10))
    ttk.Radiobutton(paper_box, text="Letter (default)", variable=paper_var,
                    value="LETTER").grid(row=0, column=0, padx=(0, 22), sticky="w")
    ttk.Radiobutton(paper_box, text="A4", variable=paper_var,
                    value="A4").grid(row=0, column=1, sticky="w")

    film_box = ttk.LabelFrame(outer, text="Film format", padding=10)
    film_box.grid(row=3, column=0, sticky="ew", pady=(0, 12))
    ttk.Radiobutton(film_box, text="120 film (default)", variable=film_var,
                    value="120").grid(row=0, column=0, padx=(0, 22), sticky="w")
    ttk.Radiobutton(film_box, text="35 mm film", variable=film_var,
                    value="35").grid(row=0, column=1, sticky="w")

    process_box = ttk.LabelFrame(outer, text="Film type", padding=10)
    process_box.grid(row=4, column=0, sticky="ew", pady=(0, 10))
    ttk.Radiobutton(process_box, text="Negative (NEG)", variable=film_type_var,
                    value="NEG").grid(row=0, column=0, padx=(0, 22), sticky="w")
    ttk.Radiobutton(process_box, text="Positive (POS)", variable=film_type_var,
                    value="POS").grid(row=0, column=1, sticky="w")

    color_box = ttk.LabelFrame(outer, text="Color", padding=10)
    color_box.grid(row=5, column=0, sticky="ew", pady=(0, 12))
    ttk.Radiobutton(color_box, text="Black & white (BW)", variable=color_var,
                    value="BW").grid(row=0, column=0, padx=(0, 22), sticky="w")
    ttk.Radiobutton(color_box, text="Color (COL)", variable=color_var,
                    value="COL").grid(row=0, column=1, sticky="w")

    fields = ttk.Frame(outer)
    fields.grid(row=6, column=0, sticky="ew")
    fields.columnconfigure(1, weight=1)

    ttk.Label(fields, text="Prefix (1–20 characters):").grid(
        row=0, column=0, sticky="w", pady=5, padx=(0, 12))
    prefix_entry = ttk.Entry(fields, textvariable=prefix_var, width=26)
    prefix_entry.grid(row=0, column=1, sticky="ew", pady=5)

    ttk.Label(fields, text="Starting serial:").grid(
        row=1, column=0, sticky="w", pady=5, padx=(0, 12))
    ttk.Entry(fields, textvariable=start_var, width=26).grid(
        row=1, column=1, sticky="ew", pady=5)

    ttk.Label(fields, text="Output PDF:").grid(
        row=2, column=0, sticky="w", pady=5, padx=(0, 12))
    output_row = ttk.Frame(fields)
    output_row.grid(row=2, column=1, sticky="ew", pady=5)
    output_row.columnconfigure(0, weight=1)
    ttk.Entry(output_row, textvariable=filename_var).grid(
        row=0, column=0, sticky="ew")

    def browse():
        prefix = prefix_var.get().strip().upper() or "FILM"
        try:
            serial = max(1, int(start_var.get().strip()))
        except ValueError:
            serial = 1
        suggested = f"film_sleeve_{color_var.get()}_{film_type_var.get()}{film_var.get()}_{prefix}{serial:04d}.pdf"
        path = filedialog.asksaveasfilename(
            parent=root, title="Save label PDF", defaultextension=".pdf",
            initialfile=suggested, filetypes=[("PDF files", "*.pdf")]
        )
        if path:
            filename_var.set(path)

    ttk.Button(output_row, text="Browse…", command=browse).grid(
        row=0, column=1, padx=(6, 0))

    def generate():
        prefix = prefix_var.get().strip().upper()
        if not prefix:
            messagebox.showerror("Missing prefix", "Enter a sleeve prefix.", parent=root)
            prefix_entry.focus_set()
            return
        if len(prefix) > 20 or any(ord(ch) < 32 for ch in prefix):
            messagebox.showerror(
                "Invalid prefix", "Prefix must be 1–20 characters and contain no control characters.",
                parent=root)
            prefix_entry.focus_set()
            return
        try:
            serial = int(start_var.get().strip())
            if serial < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid serial", "Starting serial must be a whole number of at least 1.",
                parent=root)
            return

        output_text = filename_var.get().strip()
        if not output_text:
            browse()
            output_text = filename_var.get().strip()
            if not output_text:
                return
        output = Path(output_text).expanduser()
        if output.suffix.lower() != ".pdf":
            output = output.with_suffix(".pdf")

        try:
            create_pdf(paper_var.get(), film_var.get(), prefix, serial, output,
                       film_type_var.get(), color_var.get())
        except Exception as exc:
            messagebox.showerror("Could not create PDF", str(exc), parent=root)
            return

        messagebox.showinfo(
            "PDF created",
            f"Created successfully:\\n{output.resolve()}\\n\\n"
            f"Serials: {', '.join(f'{prefix}.{n:04d}' for n in range(serial, serial + 9))}",
            parent=root
        )

    buttons = ttk.Frame(outer)
    buttons.grid(row=7, column=0, sticky="e", pady=(18, 0))
    ttk.Button(buttons, text="Generate PDF", command=generate).grid(row=0, column=0)

    ttk.Label(
        outer, text="The first nine consecutive serials are placed on each page.",
        foreground="#666666"
    ).grid(row=8, column=0, sticky="w", pady=(12, 0))

    # Calculate the finished window size and position it in the screen centre.
    root.update_idletasks()
    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = max(0, (screen_width - window_width) // 2)
    y = max(0, (screen_height - window_height) // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    prefix_entry.focus_set()
    root.bind("<Return>", lambda _event: generate())
    root.mainloop()


if __name__ == "__main__":
    main()

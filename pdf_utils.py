import fitz  # PyMuPDF

def replace_text_with_style(input_pdf, output_pdf, old_text, new_text):
    doc = fitz.open(input_pdf)
    
    for page in doc:
        # Case-insensitive search (works in older PyMuPDF versions)
        matches = (
            page.search_for(old_text) 
            + page.search_for(old_text.lower())
            + page.search_for(old_text.upper())
            + page.search_for(old_text.title())
        )

        for inst in matches:
            fontsize = 12  # default

            # Get font size
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                for l in b.get("lines", []):
                    for s in l.get("spans", []):
                        if old_text.lower() in s["text"].lower():
                            fontsize = s["size"]
                            break

            # Replace text
            page.add_redact_annot(inst, fill=(1, 1, 1))
            page.apply_redactions()
            x, y = inst.tl
            page.insert_text((x, y), new_text, fontname="helv", fontsize=fontsize, color=(0, 0, 0))

    doc.save(output_pdf)


def highlight_text_in_pdf(input_pdf, output_pdf, target_text):
    doc = fitz.open(input_pdf)
    
    for page in doc:
        matches = (
            page.search_for(target_text)
            + page.search_for(target_text.lower())
            + page.search_for(target_text.upper())
            + page.search_for(target_text.title())
        )

        for inst in matches:
            highlight = page.add_highlight_annot(inst)
            highlight.set_colors(stroke=(1, 1, 0), fill=(1, 1, 0, 0.3))
            highlight.update()

    # Flatten annotations
    for page in doc:
        for annot in page.annots() or []:
            annot.update()
            annot.flatten()

    doc.save(output_pdf)

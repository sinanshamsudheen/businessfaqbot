from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_sample_pdf():
    doc = SimpleDocTemplate("sample_document.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    with open("sample_document.txt", "r") as file:
        lines = file.readlines()
    
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            p = Paragraph(line[2:], styles['Heading1'])
            story.append(p)
            story.append(Spacer(1, 12))
        elif line.startswith("## "):
            p = Paragraph(line[3:], styles['Heading2'])
            story.append(p)
            story.append(Spacer(1, 12))
        elif line.startswith("### "):
            p = Paragraph(line[4:], styles['Heading3'])
            story.append(p)
            story.append(Spacer(1, 12))
        elif line.startswith("- "):
            p = Paragraph(f"• {line[2:]}", styles['Normal'])
            story.append(p)
        elif line:
            p = Paragraph(line, styles['Normal'])
            story.append(p)
        else:
            story.append(Spacer(1, 12))
    
    doc.build(story)

if __name__ == "__main__":
    create_sample_pdf()
    print("Sample PDF created successfully!")
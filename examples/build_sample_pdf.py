"""Rebuild the bilingual PDF fixture offline: pip install reportlab fonttools.

Pass --source-font PATH to rebuild the bundled font subset from the upstream
Noto Sans TC variable TTF. Otherwise use the already bundled subset.
"""
from argparse import ArgumentParser
from pathlib import Path

PAGES = (
    (
        "Lecture 1: Scarcity and Resource Allocation (Page 1 of 3)",
        "第一頁：稀少性與資源分配",
        "1. Resources such as time, budget, and attention are finite.",
        "2. Scarcity requires every decision-maker to choose among alternatives.",
    ),
    (
        "Lecture 1: Opportunity Cost (Page 2 of 3)",
        "機會成本是為某個選擇而放棄的最佳替代方案價值。",
        "Opportunity cost is the value of the next-best alternative forgone.",
        "機會成本不僅包含實際花掉的金錢，也涵蓋時間與其他隱性成本。",
    ),
    (
        "Lecture 1: Marginal Analysis and Review (Page 3 of 3)",
        "第三頁：邊際分析與課堂思考題",
        "Optimal allocation occurs when marginal benefit equals marginal cost.",
        "課堂思考：為甚麼免費的選擇仍然可能具有高昂的機會成本？",
    ),
)
DATA = Path(__file__).resolve().parent / "data"
FONT = DATA / "fonts" / "NoteWeaverDemo-Regular.ttf"


def subset_font(source: Path) -> None:
    from fontTools import subset
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont

    font = TTFont(source)
    instantiateVariableFont(font, {"wght": 400}, inplace=True)
    options = subset.Options()
    options.name_IDs = ["*"]
    options.name_languages = ["*"]
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(text="\n".join(line for page in PAGES for line in page))
    subsetter.subset(font)
    names = {1: "NoteWeaver Demo", 2: "Regular", 3: "NoteWeaverDemo-Regular",
             4: "NoteWeaver Demo Regular", 6: "NoteWeaverDemo-Regular",
             16: "NoteWeaver Demo", 17: "Regular"}
    for record in font["name"].names:
        if record.nameID in names:
            record.string = names[record.nameID].encode(record.getEncoding())
    FONT.parent.mkdir(parents=True, exist_ok=True)
    font.save(FONT)
    font.close()


def build_pdf() -> None:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen.canvas import Canvas

    pdfmetrics.registerFont(TTFont("NoteWeaverDemo", str(FONT)))
    canvas = Canvas(str(DATA / "sample_lecture_3p.pdf"), pagesize=(720, 480), invariant=1)
    canvas.setTitle("NoteWeaver bilingual lecture fixture")
    canvas.setAuthor("NoteWeaver contributors")
    for page in PAGES:
        canvas.setFillColorRGB(0.12, 0.23, 0.37)
        canvas.setFont("NoteWeaverDemo", 17)
        canvas.drawString(40, 420, page[0])
        canvas.setFillColorRGB(0.15, 0.17, 0.2)
        canvas.setFont("NoteWeaverDemo", 13)
        for index, line in enumerate(page[1:]):
            canvas.drawString(40, 350 - index * 65, line)
        canvas.showPage()
    canvas.save()


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--source-font", type=Path)
    args = parser.parse_args()
    if args.source_font:
        subset_font(args.source_font)
    build_pdf()

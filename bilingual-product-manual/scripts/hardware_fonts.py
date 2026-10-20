"""Use installed fonts; make temporary outline-compatible PDF subsets when needed."""
from pathlib import Path
import subprocess, shutil
from fontTools.ttLib import TTFont as Font
from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from manual import require


def locate_font(family, bold=False, explicit=None):
    if explicit:
        p=Path(explicit).expanduser().resolve()
        require(p.is_file(), 'The specified font file does not exist')
        return p
    require(shutil.which('fc-match'), 'Font discovery unavailable; supply --font-regular and --font-bold')
    query=family+(':style=Bold' if bold else ':style=Regular')
    result=subprocess.run(['fc-match','-f','%{family}\n%{file}',query],capture_output=True,text=True,check=True).stdout.splitlines()
    require(len(result)>1 and family.casefold() in result[0].casefold(), 'Requested font is not installed; supply font files or select an installed family')
    p=Path(result[1]);require(p.is_file(),'Font discovery did not return a font file');return p


def register_pdf_fonts(family, text, temporary, regular=None, bold=None):
    """CFF is converted only in a temporary, per-document subset; never ship fonts."""
    paths={};characters={ord(c) for c in text if not c.isspace()}
    for weight,explicit in [('Regular',regular),('Bold',bold)]:
        source=locate_font(family,weight=='Bold',explicit)
        font=Font(source,fontNumber=0)
        require(not (characters-set(font.getBestCmap())), 'Font is missing characters used by this document; choose a complete Latin/CJK font')
        options=subset.Options();options.name_IDs=['*'];options.name_legacy=True
        sub=subset.Subsetter(options=options);sub.populate(unicodes=characters|{32});sub.subset(font)
        destination=Path(temporary)/('hardware-'+weight+'.ttf')
        if 'glyf' in font:
            font.save(destination)
        else:
            glyphset=font.getGlyphSet();order=font.getGlyphOrder();glyphs={}
            for name in order:
                pen=TTGlyphPen(None)
                glyphset[name].draw(Cu2QuPen(pen,max_err=0.75,reverse_direction=True))
                glyphs[name]=pen.glyph()
            builder=FontBuilder(font['head'].unitsPerEm,isTTF=True)
            builder.setupGlyphOrder(order);builder.setupCharacterMap(font.getBestCmap())
            builder.setupGlyf(glyphs);builder.setupHorizontalMetrics({n:font['hmtx'][n] for n in order})
            builder.setupHorizontalHeader(ascent=font['hhea'].ascent,descent=font['hhea'].descent,lineGap=font['hhea'].lineGap)
            builder.setupNameTable({'familyName':family,'styleName':weight,'uniqueFontIdentifier':'HardwareTemporary'+weight,'fullName':family+' '+weight,'psName':'HardwareTemporary'+weight})
            os2=font['OS/2']
            builder.setupOS2(sTypoAscender=os2.sTypoAscender,sTypoDescender=os2.sTypoDescender,sTypoLineGap=os2.sTypoLineGap,usWinAscent=os2.usWinAscent,usWinDescent=os2.usWinDescent)
            builder.setupPost();builder.setupMaxp();builder.save(destination)
        pdfmetrics.registerFont(TTFont('Hardware'+weight,str(destination)))
        paths[weight]=str(source)
        font.close()
    return paths

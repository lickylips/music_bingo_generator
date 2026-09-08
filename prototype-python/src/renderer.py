from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
import io

class PDFRenderer:
    def render_to_bytes(self, cards, title="Music Bingo", suffix="", page_size_name="A4", cards_per_sheet=2, include_artist=True, jackpot=False):
        """
        Renders cards to a PDF in memory.
        """
        import reportlab.lib.pagesizes as pagesizes
        
        buffer = io.BytesIO()
        
        # Resolve page size dynamically
        page_size_tuple = getattr(pagesizes, page_size_name, A4)
        
        # Margins: 0.5cm all around (closer to edge)
        margin = 0.5 * cm
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=page_size_tuple,
            rightMargin=margin, leftMargin=margin,
            topMargin=margin, bottomMargin=margin
        )
        
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        # Style for the Title Text inside the box
        title_text_style = ParagraphStyle(
            'BingoTitleText',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=16,
            leading=20
        )
        
        # Style for cell content
        cell_style_base = ParagraphStyle(
            'CellStyle',
            parent=styles['BodyText'],
            alignment=TA_CENTER,
            leading=10,  # Line spacing
            spaceBefore=0,
            spaceAfter=0
        )
        
        # Dimensions
        page_width = page_size_tuple[0] - 2*margin
        col_width = page_width / 5
        
        usable_page_height = page_size_tuple[1] - 2*margin
        card_spacer = 0.5 * cm
        total_spacer_height = (cards_per_sheet - 1) * card_spacer if cards_per_sheet > 1 else 0
        usable_height_per_card = (usable_page_height - total_spacer_height) / cards_per_sheet
        
        grid_height = usable_height_per_card - 2.0 * cm 
        row_height = grid_height / 5
        
        # Grid Style
        grid_style_list = [
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            # Padding
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]
        if not jackpot:
            grid_style_list.append(('BACKGROUND', (2,2), (2,2), colors.lightgrey)) # Free Space
        grid_style = TableStyle(grid_style_list)

        # Title Box Style
        title_box_style = TableStyle([
            ('BOX', (0,0), (-1,-1), 2, colors.black), # Thick border
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ])

        for i, card in enumerate(cards):
            # 1. Title Box
            # Wrap title in a Table to get the box effect
            display_title = title
            if suffix:
                display_title = f"{title} - {suffix}"
            title_p = Paragraph(display_title, title_text_style)
            title_table = Table([[title_p]], colWidths=[page_width])
            title_table.setStyle(title_box_style)
            elements.append(title_table)
            
            # Small spacer between title and grid
            elements.append(Spacer(1, 0.3*cm))
            
            # 2. Build Table Data
            table_data = []
            for row in card:
                row_data = []
                for cell in row:
                    raw_title = cell['title']
                    artist = cell['artist']
                    
                    # Heuristic for Font Size
                    # Title length
                    t_len = len(raw_title)
                    if t_len < 15:
                        f_size = 14
                    elif t_len < 30:
                        f_size = 11
                    elif t_len < 50:
                        f_size = 9
                    else:
                        f_size = 8
                    
                    # Free Space Check
                    if not jackpot and raw_title == "FREE SPACE":
                        f_size = 14
                        display_text = f"<b>{raw_title}</b>"
                    else:
                        # Construct HTML for Paragraph
                        # Bold title, variable size
                        display_text = f'<font size="{f_size}"><b>{raw_title}</b></font>'
                        if artist and include_artist:
                            # Artist smaller and italic
                            display_text += f'<br/><font size="{f_size-2}"><i>{artist}</i></font>'
                    
                    p = Paragraph(display_text, cell_style_base)
                    row_data.append(p)
                table_data.append(row_data)
            
            # 3. Create Grid Table
            t = Table(table_data, colWidths=[col_width]*5, rowHeights=[row_height]*5)
            t.setStyle(grid_style)
            elements.append(t)
            
            # 4. Spacing or Page Break
            if (i + 1) % cards_per_sheet == 0:
                # End of page
                elements.append(PageBreak())
            else:
                # Add space for next card
                elements.append(Spacer(1, card_spacer))

        doc.build(elements)
        buffer.seek(0)
        return buffer

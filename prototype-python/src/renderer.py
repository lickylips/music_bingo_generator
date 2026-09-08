from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
import io

class PDFRenderer:
    def render_to_bytes(self, cards, title="Music Bingo", suffix="", page_size_name="A4", cards_per_sheet=2, include_artist=True, jackpot=False, track_list=None):
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

        if track_list:
            display_title = title
            if suffix:
                display_title = f"{title} - {suffix}"
            cover_title_p = Paragraph(f"Track List: {display_title}", title_text_style)
            cover_title_table = Table([[cover_title_p]], colWidths=[page_width])
            cover_title_table.setStyle(title_box_style)
            elements.append(cover_title_table)
            elements.append(Spacer(1, 0.5*cm))

            unique_tracks = {}
            for t in track_list:
                key = (t['title'].strip().lower(), t['artist'].strip().lower() if t['artist'] else "")
                if key not in unique_tracks:
                    unique_tracks[key] = t
            
            sorted_tracks = sorted(unique_tracks.values(), key=lambda x: x['title'].lower())

            track_style = ParagraphStyle('TrackStyle', parent=styles['BodyText'], fontSize=10, leading=14)

            table_data = []
            half = (len(sorted_tracks) + 1) // 2
            for i in range(half):
                t1 = sorted_tracks[i]
                t1_text = f"[  ] {t1['title']}"
                if t1['artist'] and include_artist:
                    t1_text += f" - <i>{t1['artist']}</i>"
                p1 = Paragraph(t1_text, track_style)
                
                if i + half < len(sorted_tracks):
                    t2 = sorted_tracks[i + half]
                    t2_text = f"[  ] {t2['title']}"
                    if t2['artist'] and include_artist:
                        t2_text += f" - <i>{t2['artist']}</i>"
                    p2 = Paragraph(t2_text, track_style)
                else:
                    p2 = Paragraph("", track_style)
                
                table_data.append([p1, p2])
            
            if table_data:
                track_table = Table(table_data, colWidths=[page_width/2.0, page_width/2.0])
                track_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ]))
                elements.append(track_table)
            elements.append(PageBreak())

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

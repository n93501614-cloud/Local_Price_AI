from pathlib import Path

from datetime import datetime

from reportlab.lib.pagesizes import A4

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors

from reportlab.lib.styles import (
    getSampleStyleSheet
)


def create_pdf_report(

    query,

    location,

    products,

    stores,

    recommendation,

    history
):

    path = Path(
        "localprice_ai_report.pdf"
    )


    styles = (
        getSampleStyleSheet()
    )


    document = SimpleDocTemplate(

        str(path),

        pagesize=A4
    )


    story = []


    story.append(

        Paragraph(

            "LocalPrice AI — "
            "Shopping Intelligence Report",

            styles["Title"]
        )
    )


    story.append(
        Spacer(1, 10)
    )


    story.append(

        Paragraph(

            f"<b>Product:</b> {query}",

            styles["BodyText"]
        )
    )


    story.append(

        Paragraph(

            f"<b>Location:</b> {location}",

            styles["BodyText"]
        )
    )


    story.append(

        Paragraph(

            "<b>Generated:</b> "
            +
            datetime.now().strftime(
                "%d %b %Y %H:%M"
            ),

            styles["BodyText"]
        )
    )


    story.append(
        Spacer(1, 15)
    )


    if recommendation:

        story.append(

            Paragraph(
                "AI Recommendation",
                styles["Heading2"]
            )
        )


        story.append(

            Paragraph(

                recommendation[
                    "headline"
                ],

                styles["BodyText"]
            )
        )


        story.append(

            Paragraph(

                recommendation[
                    "explanation"
                ],

                styles["BodyText"]
            )
        )


        story.append(
            Spacer(1, 10)
        )


    # =====================================================
    # ONLINE PRICES
    # =====================================================

    story.append(

        Paragraph(
            "Online Prices",
            styles["Heading2"]
        )
    )


    data = [

        [
            "Seller",
            "Price",
            "Rating",
            "Reviews"
        ]
    ]


    for product in products[:15]:

        data.append(

            [

                str(
                    product.get(
                        "source",
                        ""
                    )
                )[:30],

                str(
                    product.get(
                        "price_text",
                        ""
                    )
                ),

                str(
                    product.get(
                        "rating"
                    )
                    or
                    "N/A"
                ),

                str(
                    product.get(
                        "reviews"
                    )
                    or
                    0
                )
            ]
        )


    table = Table(
        data,
        repeatRows=1
    )


    table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            )
        ])
    )


    story.append(
        table
    )


    story.append(
        Spacer(1, 15)
    )


    # =====================================================
    # LOCAL STORES
    # =====================================================

    story.append(

        Paragraph(
            "Nearby Stores",
            styles["Heading2"]
        )
    )


    store_data = [

        [
            "Store",
            "Rating",
            "Reviews",
            "Address"
        ]
    ]


    for store in stores[:15]:

        store_data.append(

            [

                str(
                    store.get(
                        "title",
                        ""
                    )
                )[:28],

                str(
                    store.get(
                        "rating"
                    )
                    or
                    "N/A"
                ),

                str(
                    store.get(
                        "reviews"
                    )
                    or
                    0
                ),

                str(
                    store.get(
                        "address",
                        ""
                    )
                )[:45]
            ]
        )


    store_table = Table(

        store_data,

        repeatRows=1
    )


    store_table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            )
        ])
    )


    story.append(
        store_table
    )


    story.append(
        Spacer(1, 15)
    )


    story.append(

        Paragraph(

            "Disclaimer: prices, availability and "
            "delivery information are search-result "
            "snapshots. Verify the final price, "
            "variant, seller and stock before purchasing.",

            styles["Italic"]
        )
    )


    document.build(
        story
    )


    return str(path)

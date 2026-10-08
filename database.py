import sqlite3

from datetime import datetime, timezone


DB_PATH = "localprice_ai.db"


class PriceDB:

    def __init__(
        self,
        path=DB_PATH
    ):

        self.path = path

        self._init()


    def _connect(self):

        return sqlite3.connect(
            self.path
        )


    def _init(self):

        connection = self._connect()

        cursor = connection.cursor()


        cursor.execute("""

            CREATE TABLE IF NOT EXISTS price_history (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                product_query TEXT,

                title TEXT,

                source TEXT,

                price REAL,

                url TEXT,

                product_id TEXT,

                timestamp TEXT
            )

        """)


        cursor.execute("""

            CREATE TABLE IF NOT EXISTS alerts (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                product_query TEXT,

                target_price REAL,

                active INTEGER DEFAULT 1,

                created_at TEXT
            )

        """)


        connection.commit()

        connection.close()


    def save_price(

        self,

        product_query,

        title,

        source,

        price,

        url="",

        product_id=""
    ):

        connection = self._connect()


        connection.execute("""

            INSERT INTO price_history

            (
                product_query,
                title,
                source,
                price,
                url,
                product_id,
                timestamp
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)

        """, (

            product_query,

            title,

            source,

            price,

            url,

            product_id,

            datetime.now(
                timezone.utc
            ).isoformat()
        ))


        connection.commit()

        connection.close()


    def get_history(
        self,
        product_query
    ):

        connection = self._connect()

        cursor = connection.cursor()


        cursor.execute("""

            SELECT

                product_query,

                title,

                source,

                price,

                url,

                product_id,

                timestamp

            FROM price_history

            WHERE product_query = ?

            ORDER BY timestamp ASC

        """, (
            product_query,
        ))


        rows = cursor.fetchall()


        connection.close()


        keys = [

            "product_query",

            "title",

            "source",

            "price",

            "url",

            "product_id",

            "timestamp"
        ]


        return [

            dict(
                zip(
                    keys,
                    row
                )
            )

            for row in rows
        ]


    def add_alert(

        self,

        product_query,

        target_price
    ):

        connection = self._connect()


        connection.execute("""

            INSERT INTO alerts

            (
                product_query,
                target_price,
                created_at
            )

            VALUES (?, ?, ?)

        """, (

            product_query,

            target_price,

            datetime.now(
                timezone.utc
            ).isoformat()
        ))


        connection.commit()

        connection.close()


    def get_alerts(self):

        connection = self._connect()

        cursor = connection.cursor()


        cursor.execute("""

            SELECT

                id,

                product_query,

                target_price,

                active,

                created_at

            FROM alerts

            ORDER BY id DESC

        """)


        rows = cursor.fetchall()


        connection.close()


        keys = [

            "id",

            "product_query",

            "target_price",

            "active",

            "created_at"
        ]


        return [

            dict(
                zip(
                    keys,
                    row
                )
            )

            for row in rows
        ]
      

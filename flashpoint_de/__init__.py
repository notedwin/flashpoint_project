import pandas as pd
import duckdb
import os
import requests
from collections import Counter
import click
import time


CON = duckdb.connect("file.db")
NUM_BOOKS = 52000


@click.group()
def cli():
    pass


@cli.command()
@click.option("--document", prompt="book", help="Book we want frequest words from")
@click.option("--limit", default=10, help="Number of words we want")
def search_words(document, limit):
    # if we do not have a number, we do a fuzzy search
    if not document.isdigit():
        document = CON.execute(
            f"""
                    SELECT
                        "Text#",
                        title
                    FROM catalog
                    WHERE title LIKE '%{document}%'
                    LIMIT 1
                    """
        ).fetchone()
        print(f"Looking at {document[1]}")
        document = document[0]
        if not document:
            raise Exception(f"No Book with {document} in title!")

    document = f"{int(document):05}"
    click.echo(
        CON.sql(
            f"""
                SELECT
                    word,
                    count
                FROM book_{document}
                ORDER BY 2 DESC
                LIMIT {limit}
                """
        )
    )


@cli.command()
@click.option("--word", prompt="word", help="word we want to find")
@click.option("--limit", default=10, help="Number of books we want")
def search_documents(word, limit):
    """
    search_documents is more complex than search_words since we have to query thousands of tables, to do this I did group tables by 1000, got the top 10 books from that bunch and added it to the final dataframe, where I limit again by 10
    """

    # We have to dynamically generate SQL the way I made tables
    CON.execute("SET max_expression_depth TO 1100")
    result_df = pd.DataFrame(columns=["Title", "book_id", "count"])
    for num in range(0, NUM_BOOKS, 1000):
        query = """
            SELECT c.title, 
            book_id,
            count
            FROM (
            """

        for table_num in range(num, num + 1001):
            query += f"""
                    SELECT {table_num:05} as book_id, count FROM book_{table_num:05}
                    WHERE word = '{word}'
                """
            if table_num < num + 1000:
                query += "UNION ALL "

        query += f"""
            )
            LEFT JOIN catalog c
            ON book_id = "Text#"
            ORDER BY count DESC
            LIMIT {limit}
            """
        chunk_result = CON.execute(query).fetch_df()
        # print(chunk_result)
        result_df = pd.concat([result_df, chunk_result], ignore_index=True)

    result = CON.query(
        f"""
        SELECT 
        Title,
        book_id, 
        count 
        FROM result_df 
        ORDER BY COUNT DESC
        LIMIT {limit}
        """
    ).to_df()
    print(result)


if __name__ == "__main__":
    cli()

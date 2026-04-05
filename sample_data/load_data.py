import pandas as pd
from tqdm import tqdm
from conn_db.client import client as db_client
from conn_emb_hugging_face.client import get_document_embedding


def load_stock_data(stock_symbol, df_stock):
    collection_name = stock_symbol

    try:
        db_client.delete_collection(name=collection_name)
        print(f"  ✓ Deleted existing '{collection_name}' collection")
    except Exception:
        pass

    collection = db_client.get_or_create_collection(name=collection_name)

    print(f"  Loading {len(df_stock)} articles for {stock_symbol}...")

    for _, row in tqdm(df_stock.iterrows(), total=len(df_stock), desc=f"  {stock_symbol}", leave=False):
        doc_id = str(int(row['Unnamed: 0']))
        content = f"(Stock {row['stock']}) - {row['title']}"
        metadata = {
            "stock": row['stock'],
            "date": row['date']
        }

        embedding = get_document_embedding(content)

        collection.add(
            ids=[doc_id],
            documents=[content],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    count = collection.count()
    print(f"  ✓ {stock_symbol}: {count} documents loaded\n")


def load_top_stocks(top_n=20):
    csv_path = "sample_data/analyst_ratings_processed.csv"
    df = pd.read_csv(csv_path)

    top_stocks = df['stock'].value_counts().head(top_n)

    print(f"Loading top {top_n} stocks into separate collections")
    print(f"Total articles to process: {top_stocks.sum():,}\n")

    for rank, (stock_symbol, article_count) in enumerate(top_stocks.items(), 1):
        print(f"[{rank}/{top_n}] Processing {stock_symbol} ({article_count:,} articles)")

        df_stock = df[df['stock'] == stock_symbol]

        load_stock_data(stock_symbol, df_stock)

    print("=" * 60)
    print(f"✓ Successfully created {top_n} collections")
    print("=" * 60)


if __name__ == "__main__":
    load_top_stocks(top_n=20)

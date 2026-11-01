import logging
import pandas as pd
import sqlite3

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IPLETLPipeline:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect_db(self):
        """Establish connection to SQLite IPL Data Warehouse."""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to SQLite database: {self.db_name}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def extract_and_transform(self, csv_file_path):
        """Extract raw match/ball data and perform data cleaning and transformation."""
        logger.info(f"EXTRACT & TRANSFORM: Processing dataset from {csv_file_path}")
        try:
            df = pd.read_csv(csv_file_path)
            
            # Data Cleaning & Handling Nulls
            df['batsman'] = df['batsman'].fillna('Unknown Player')
            df['bowler'] = df['bowler'].fillna('Unknown Bowler')
            df['venue'] = df['venue'].fillna('Neutral Venue')
            
            # Data Type Enforcements
            df['runs_scored'] = pd.to_numeric(df['runs_scored'], errors='coerce').fillna(0).astype(int)
            df['is_wicket'] = pd.to_numeric(df['is_wicket'], errors='coerce').fillna(0).astype(int)
            
            # Feature Engineering: Calculate total legal deliveries or boundary flags
            df['is_boundary'] = df['runs_scored'].apply(lambda x: 1 if x >= 4 else 0)
            
            df = df.drop_duplicates()
            logger.info(f"Transformation complete. Cleaned {len(df)} ball-by-ball records.")
            return df
        except Exception as e:
            logger.error(f"Error during extract/transform phase: {e}")
            raise

    def load(self, df, table_name):
        """Load transformed IPL data into SQLite warehouse table."""
        logger.info(f"LOAD: Committing data into table '{table_name}'")
        try:
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    match_id INTEGER,
                    inning INTEGER,
                    batting_team TEXT,
                    bowling_team TEXT,
                    batsman TEXT,
                    bowler TEXT,
                    runs_scored INTEGER,
                    is_wicket INTEGER,
                    venue TEXT,
                    is_boundary INTEGER
                );
            """)

            # Bulk insert records
            records = [
                (
                    int(row['match_id']),
                    int(row['inning']),
                    str(row['batting_team']),
                    str(row['bowling_team']),
                    str(row['batsman']),
                    str(row['bowler']),
                    int(row['runs_scored']),
                    int(row['is_wicket']),
                    str(row['venue']),
                    int(row['is_boundary'])
                )
                for _, row in df.iterrows()
            ]

            self.cursor.executemany(f"""
                INSERT INTO {table_name} 
                (match_id, inning, batting_team, bowling_team, batsman, bowler, runs_scored, is_wicket, venue, is_boundary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, records)

            self.connection.commit()
            logger.info("LOAD Complete. IPL data successfully written to warehouse.")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.connection.rollback()
            raise

    def close(self):
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed.")

if __name__ == "__main__":
    db_file = 'ipl_analytics.db'
    
    # Create sample raw ball-by-ball source CSV for demonstration
    dummy_csv = 'raw_ipl_matches.csv'
    sample_df = pd.DataFrame({
        'match_id': [335982, 335982, 335982, 335983, 335983],
        'inning': [1, 1, 1, 2, 2],
        'batting_team': ['Kolkata Knight Riders', 'Kolkata Knight Riders', 'Kolkata Knight Riders', 'Chennai Super Kings', 'Chennai Super Kings'],
        'bowling_team': ['Royal Challengers Bangalore', 'Royal Challengers Bangalore', 'Royal Challengers Bangalore', 'Mumbai Indians', 'Mumbai Indians'],
        'batsman': ['SC Ganguly', 'BB McCullum', 'BB McCullum', 'ML Hayden', 'MS Dhoni'],
        'bowler': ['P Kumar', 'Z Khan', 'P Kumar', 'SL Malinga', 'Harbhajan Singh'],
        'runs_scored': [0, 4, 6, 1, 4],
        'is_wicket': [0, 0, 0, 0, 0],
        'venue': ['M Chinnaswamy Stadium', 'M Chinnaswamy Stadium', 'M Chinnaswamy Stadium', 'Wankhede Stadium', 'Wankhede Stadium']
    })
    sample_df.to_csv(dummy_csv, index=False)

    pipeline = IPLETLPipeline(db_file)
    try:
        pipeline.connect_db()
        cleaned_data = pipeline.extract_and_transform(dummy_csv)
        pipeline.load(cleaned_data, 'fact_ipl_deliveries')
    except Exception as e:
        logger.error(f"IPL Pipeline Failed: {e}")
    finally:
        pipeline.close()
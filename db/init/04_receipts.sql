CREATE TABLE IF NOT EXISTS retirement_receipts (
    request_id VARCHAR(128) PRIMARY KEY,
    document VARCHAR(15) NOT NULL,
    retirement_date DATE NOT NULL,
    reason VARCHAR(200) NOT NULL,
    movement INTEGER NOT NULL
);

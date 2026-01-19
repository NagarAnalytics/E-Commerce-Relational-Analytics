import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# 1. Connect to the new project database
conn = sqlite3.connect('retail_warehouse.db')
cursor = conn.cursor()

# 2. Build the Schema (The structure of your data)
# 2. Build the Full Relational Schema
# We drop the tables first to ensure the columns match our data exactly
cursor.execute("DROP TABLE IF EXISTS sales")
cursor.execute("DROP TABLE IF EXISTS products")
cursor.execute("DROP TABLE IF EXISTS categories")
cursor.execute("DROP TABLE IF EXISTS customers")

cursor.executescript('''
    CREATE TABLE categories (
        category_id INTEGER PRIMARY KEY,
        category_name TEXT
    );

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        name TEXT,
        category_id INTEGER,
        price REAL,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    );

    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT
    );

    CREATE TABLE sales (
        sale_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        sale_date DATE,
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
''')

# 3. Seed the Data (5 values for Sales to match the 5 columns)
categories_data = [(1, 'Electronics'), (2, 'Home Office'), (3, 'Accessories')]
products_data = [
    (101, 'Mechanical Keyboard', 1, 120.00),
    (102, '4K Monitor', 1, 450.00),
    (103, 'Standing Desk', 2, 600.00),
    (104, 'Ergonomic Mouse', 3, 80.00),
    (105, 'Webcam HD', 1, 95.00)
]
customers_data = [(50, 'Alice'), (51, 'Bob'), (52, 'Charlie')]

sales_data = [
    (1, 50, 101, 5, '2026-01-10'),
    (2, 51, 103, 2, '2026-01-11'),
    (3, 50, 102, 1, '2026-01-12'),
    (4, 52, 101, 3, '2026-01-15'),
    (5, 51, 105, 10, '2026-01-18'),
    (6, 50, 104, 4, '2026-01-19')
]

cursor.executemany('INSERT INTO categories VALUES (?,?)', categories_data)
cursor.executemany('INSERT INTO products VALUES (?,?,?,?)', products_data)
cursor.executemany('INSERT INTO customers VALUES (?,?)', customers_data)
cursor.executemany('INSERT INTO sales VALUES (?,?,?,?,?)', sales_data)
conn.commit()

print("🚀 Database is LIVE with 5-column Sales table.")

# 4. Analysis 1: Revenue by Category
rev_query = '''
SELECT c.category_name, SUM(s.quantity * p.price) AS total_revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id
GROUP BY c.category_name
ORDER BY total_revenue DESC
'''
print("\n--- Revenue by Category ---")
print(pd.read_sql_query(rev_query, conn))

# 5. Analysis 2: The "Whale" Report (Top Spenders)
whale_query = '''
SELECT c.name, SUM(s.quantity * p.price) AS total_spent
FROM sales s
JOIN products p ON s.product_id = p.product_id
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY c.name
ORDER BY total_spent DESC
'''
df_whales = pd.read_sql_query(whale_query, conn)
print("\n--- Top Spending Customers ---")
print(df_whales)

# 6. Quick Visualization of Top Spenders
plt.figure(figsize=(8, 5))
plt.bar(df_whales['name'], df_whales['total_spent'], color='teal')
plt.title('Total Spend per Customer')
plt.ylabel('Dollars ($)')
plt.show()

print("\n✅ All analyses complete and errors resolved!")
print("🚀 Retail Database is LIVE. Ready for analysis.")

# The "Executive Summary" Query (Which category is our biggest revenue driver?)
revenue_query = '''
SELECT 
    c.category_name,
    SUM(s.quantity * p.price) AS total_revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id
GROUP BY c.category_name
ORDER BY total_revenue DESC;
'''

df_revenue = pd.read_sql_query(revenue_query, conn)
print("\n--- Revenue Report by Category ---")
print(df_revenue)

# Write a SQL query (and pull it into a DataFrame) that shows each Product Name and the Total Quantity Sold,
# but only for products that sold more than 3 units?

total_product_sold = '''
SELECT 
    p.name as 'Product',
    SUM(s.Quantity) as 'Total Quantity Sold'
FROM sales s
JOIN products p on s.product_id = p.product_id       
GROUP BY p.name
Having SUM(s.Quantity) > 3     
'''

df_totProdSold = pd.read_sql_query(total_product_sold, conn)
print("\n--- Products that sold more than 3 units ---")
print(df_totProdSold)


# 1. Create the chart
plt.figure(figsize=(10, 6))
plt.bar(df_totProdSold['Product'], df_totProdSold['Total Quantity Sold'], color='royalblue')

# 2. Add professional styling
plt.title('Top Selling Products (> 3 Units)', fontsize=14, fontweight='bold')
plt.xlabel('Product Name', fontsize=12)
plt.ylabel('Total Units Sold', fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# 3. Add data labels on top of the bars
for i, value in enumerate(df_totProdSold['Total Quantity Sold']):
    plt.text(i, value + 0.2, str(int(value)), ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig("top_sellers.png") # Save for your GitHub!
plt.show()

# SQL to get daily revenue
time_series_query = '''
SELECT 
    s.sale_date,
    SUM(s.quantity * p.price) AS daily_revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY s.sale_date
ORDER BY s.sale_date ASC;
'''

df_trends = pd.read_sql_query(time_series_query, conn)
df_trends['sale_date'] = pd.to_datetime(df_trends['sale_date'])

# Plotting the trend
plt.figure(figsize=(12, 5))
plt.plot(df_trends['sale_date'], df_trends['daily_revenue'], marker='o', linestyle='-', color='darkorange')
plt.title('Daily Revenue Trends (Jan 2026)', fontsize=14)
plt.grid(True, alpha=0.3)
plt.savefig("revenue_trends.png")
plt.show()

whale_query = '''
SELECT 
    c.name,
    SUM(s.quantity * p.price) AS total_customer_spend
FROM sales s
JOIN products p ON s.product_id = p.product_id
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY c.name
ORDER BY total_customer_spend DESC;
'''

df_whales = pd.read_sql_query(whale_query, conn)
print("\n --- Total Customer Spending ---")
print(df_whales)
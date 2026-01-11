"""Data analysis tools for SQL querying, schema exploration, and visualization."""

import base64
import io
import sqlite3
from pathlib import Path
from typing import Literal, Optional

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from langchain_core.tools import tool

matplotlib.use("Agg")  # Non-interactive backend for server environments

# Default database path
DEFAULT_DB_PATH = Path(__file__).parent.parent / "data" / "sample.db"


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Get a SQLite connection with row factory."""
    path = db_path or str(DEFAULT_DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


@tool(parse_docstring=True)
def explore_schema(table_name: Optional[str] = None) -> str:
    """Explore the database schema to understand available tables and columns.

    Use this tool FIRST before writing any SQL queries to understand what
    tables exist and their structure.

    Args:
        table_name: Optional specific table to get detailed schema for.
                   If not provided, lists all available tables with their columns.

    Returns:
        Schema information including table names, column names, types,
        and sample data.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if table_name is None:
            # List all tables with their columns
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]

            result = "## Available Tables\n\n"
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]

                result += f"### {table} ({row_count} rows)\n"
                for col in columns:
                    pk = " (PRIMARY KEY)" if col[5] else ""
                    nullable = "" if col[3] else " NOT NULL"
                    result += f"- {col[1]}: {col[2]}{pk}{nullable}\n"
                result += "\n"

            return result
        else:
            # Detailed schema for specific table
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            if not columns:
                return f"Error: Table '{table_name}' does not exist."

            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()

            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]

            result = f"## Table: {table_name}\n\n"
            result += f"**Row count:** {row_count}\n\n"
            result += "### Columns\n"
            for col in columns:
                pk = " (PRIMARY KEY)" if col[5] else ""
                nullable = "" if col[3] else " NOT NULL"
                result += f"- **{col[1]}**: {col[2]}{pk}{nullable}\n"

            if foreign_keys:
                result += "\n### Foreign Keys\n"
                for fk in foreign_keys:
                    result += f"- {fk[3]} -> {fk[2]}.{fk[4]}\n"

            # Sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            samples = cursor.fetchall()
            if samples:
                col_names = [col[1] for col in columns]
                result += "\n### Sample Data (first 5 rows)\n```\n"
                result += " | ".join(col_names) + "\n"
                result += "-" * 60 + "\n"
                for row in samples:
                    result += " | ".join(str(v) for v in row) + "\n"
                result += "```\n"

            return result
    finally:
        conn.close()


@tool(parse_docstring=True)
def query_database(sql_query: str, limit: int = 100, explain: bool = False) -> str:
    """Execute a READ-ONLY SQL query against the database and return results.

    IMPORTANT: Only SELECT statements are allowed. INSERT, UPDATE, DELETE,
    DROP, and other modifying statements will be rejected for safety.

    Args:
        sql_query: The SQL SELECT query to execute. Must be read-only.
        limit: Maximum number of rows to return (default: 100, max: 1000).
        explain: If True, also return the query execution plan.

    Returns:
        Query results as formatted text table with row count.
    """
    # Safety check - only allow SELECT statements
    normalized = sql_query.strip().upper()
    if not normalized.startswith("SELECT"):
        return "Error: Only SELECT queries are allowed for safety. Please rewrite your query as a SELECT statement."

    # Block dangerous keywords
    dangerous = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
        "TRUNCATE", "EXEC", "EXECUTE", ";--", "ATTACH", "DETACH",
    ]
    for keyword in dangerous:
        if keyword in normalized:
            return f"Error: Query contains forbidden keyword '{keyword}'. Only read-only queries are allowed."

    # Enforce limit
    limit = min(limit, 1000)

    conn = get_connection()
    try:
        explain_result = None
        if explain:
            explain_result = pd.read_sql_query(f"EXPLAIN QUERY PLAN {sql_query}", conn)

        # Add LIMIT if not present
        if "LIMIT" not in normalized:
            sql_query = f"{sql_query} LIMIT {limit}"

        df = pd.read_sql_query(sql_query, conn)

        result = "## Query Results\n\n"
        result += f"**Rows returned:** {len(df)}\n\n"

        if len(df) == 0:
            result += "No results found.\n"
        elif len(df) <= 50:
            # Show full table for smaller results
            result += "```\n"
            result += df.to_string(index=False)
            result += "\n```\n"
        else:
            # Show first 20 and summary for larger results
            result += "### First 20 rows\n```\n"
            result += df.head(20).to_string(index=False)
            result += "\n```\n\n"

            # Add summary statistics for numeric columns
            numeric_cols = df.select_dtypes(include=["number"]).columns
            if len(numeric_cols) > 0:
                result += "### Summary Statistics\n```\n"
                result += df[numeric_cols].describe().to_string()
                result += "\n```\n"

        if explain_result is not None:
            result += "\n### Query Plan\n```\n"
            result += explain_result.to_string(index=False)
            result += "\n```\n"

        return result
    except Exception as e:
        return f"Error executing query: {e!s}"
    finally:
        conn.close()


@tool(parse_docstring=True)
def create_chart(
    sql_query: str,
    chart_type: Literal["bar", "line", "pie", "scatter", "histogram"] = "bar",
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
    title: Optional[str] = None,
    color_column: Optional[str] = None,
) -> str:
    """Create a visualization chart from SQL query results.

    Execute a SQL query and visualize the results as a chart.
    The chart is returned as a base64-encoded PNG image.

    Args:
        sql_query: SQL SELECT query to get data for visualization.
        chart_type: Type of chart - 'bar', 'line', 'pie', 'scatter', or 'histogram'.
        x_column: Column name for x-axis. If not specified, uses first column.
        y_column: Column name for y-axis values. If not specified, uses second column.
        title: Chart title. If not specified, auto-generated from query.
        color_column: Optional column for color grouping (bar/scatter charts).

    Returns:
        Success message with base64-encoded PNG image that can be displayed.
    """
    # Validate query
    normalized = sql_query.strip().upper()
    if not normalized.startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."

    conn = get_connection()
    try:
        df = pd.read_sql_query(sql_query, conn)

        if len(df) == 0:
            return "Error: Query returned no results. Cannot create chart."

        if len(df.columns) < 1:
            return "Error: Query must return at least one column."

        # Set defaults
        x_col = x_column or df.columns[0]
        y_col = y_column or (df.columns[1] if len(df.columns) > 1 else df.columns[0])

        # Validate columns exist
        if x_col not in df.columns:
            return f"Error: Column '{x_col}' not found. Available: {list(df.columns)}"
        if y_col not in df.columns and chart_type != "histogram":
            return f"Error: Column '{y_col}' not found. Available: {list(df.columns)}"

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        chart_title = title or f"{chart_type.title()} Chart: {y_col} by {x_col}"

        if chart_type == "bar":
            if color_column and color_column in df.columns:
                pivot_df = df.pivot(index=x_col, columns=color_column, values=y_col)
                pivot_df.plot(kind="bar", ax=ax)
            else:
                ax.bar(df[x_col].astype(str), df[y_col])
            plt.xticks(rotation=45, ha="right")

        elif chart_type == "line":
            ax.plot(df[x_col], df[y_col], marker="o")
            plt.xticks(rotation=45, ha="right")

        elif chart_type == "pie":
            ax.pie(df[y_col], labels=df[x_col], autopct="%1.1f%%")

        elif chart_type == "scatter":
            if color_column and color_column in df.columns:
                for label in df[color_column].unique():
                    subset = df[df[color_column] == label]
                    ax.scatter(subset[x_col], subset[y_col], label=label)
                ax.legend()
            else:
                ax.scatter(df[x_col], df[y_col])

        elif chart_type == "histogram":
            ax.hist(df[x_col], bins=min(20, len(df)), edgecolor="black")
            chart_title = title or f"Histogram: {x_col}"

        ax.set_title(chart_title)
        if chart_type != "pie":
            ax.set_xlabel(x_col)
            if chart_type != "histogram":
                ax.set_ylabel(y_col)

        plt.tight_layout()

        # Save to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close(fig)

        return f"Chart created successfully.\n\n![{chart_title}](data:image/png;base64,{img_base64})"

    except Exception as e:
        plt.close("all")
        return f"Error creating chart: {e!s}"
    finally:
        conn.close()


@tool(parse_docstring=True)
def analyze_data(
    sql_query: str,
    analysis_type: Literal["summary", "correlation", "distribution", "trends"] = "summary",
) -> str:
    """Perform statistical analysis on SQL query results.

    Execute a query and run statistical analysis on the resulting data.
    Useful for understanding data patterns before visualization.

    Args:
        sql_query: SQL SELECT query to get data for analysis.
        analysis_type: Type of analysis: 'summary' for basic stats, 'correlation' for correlation matrix, 'distribution' for value distributions, or 'trends' for time-series patterns.

    Returns:
        Detailed statistical analysis results as formatted text.
    """
    normalized = sql_query.strip().upper()
    if not normalized.startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."

    conn = get_connection()
    try:
        df = pd.read_sql_query(sql_query, conn)

        if len(df) == 0:
            return "Error: Query returned no results."

        result = f"## Data Analysis: {analysis_type.title()}\n\n"
        result += f"**Dataset size:** {len(df)} rows, {len(df.columns)} columns\n\n"

        if analysis_type == "summary":
            result += "### Numeric Columns Summary\n```\n"
            result += df.describe().to_string()
            result += "\n```\n\n"

            # Non-numeric summary
            non_numeric = df.select_dtypes(exclude=["number"]).columns
            if len(non_numeric) > 0:
                result += "### Categorical Columns\n"
                for col in non_numeric:
                    result += f"\n**{col}:**\n"
                    value_counts = df[col].value_counts().head(10)
                    result += f"- Unique values: {df[col].nunique()}\n"
                    result += f"- Top values: {dict(value_counts)}\n"

        elif analysis_type == "correlation":
            numeric_df = df.select_dtypes(include=["number"])
            if len(numeric_df.columns) < 2:
                return "Error: Need at least 2 numeric columns for correlation analysis."

            corr = numeric_df.corr()
            result += "### Correlation Matrix\n```\n"
            result += corr.to_string()
            result += "\n```\n\n"

            # Highlight strong correlations
            result += "### Strong Correlations (|r| > 0.5)\n"
            found_strong = False
            for i in range(len(corr.columns)):
                for j in range(i + 1, len(corr.columns)):
                    r = corr.iloc[i, j]
                    if abs(r) > 0.5:
                        result += f"- {corr.columns[i]} <-> {corr.columns[j]}: {r:.3f}\n"
                        found_strong = True
            if not found_strong:
                result += "_No strong correlations found._\n"

        elif analysis_type == "distribution":
            result += "### Value Distributions\n\n"
            for col in df.columns:
                result += f"**{col}:**\n"
                if df[col].dtype in ["int64", "float64"]:
                    result += f"- Range: [{df[col].min()}, {df[col].max()}]\n"
                    result += f"- Mean: {df[col].mean():.2f}\n"
                    result += f"- Median: {df[col].median():.2f}\n"
                    result += f"- Std Dev: {df[col].std():.2f}\n"
                else:
                    result += f"- Unique values: {df[col].nunique()}\n"
                    mode_val = df[col].mode()
                    result += f"- Most common: {mode_val.iloc[0] if len(mode_val) > 0 else 'N/A'}\n"
                result += "\n"

        elif analysis_type == "trends":
            # Try to find date columns
            date_cols = [col for col in df.columns if "date" in col.lower() or "time" in col.lower()]
            if not date_cols:
                return "Error: No date/time columns found for trend analysis. Column names should contain 'date' or 'time'."

            date_col = date_cols[0]
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.sort_values(date_col)

            result += f"### Trends over {date_col}\n\n"
            result += f"- Date range: {df[date_col].min()} to {df[date_col].max()}\n\n"

            numeric_cols = df.select_dtypes(include=["number"]).columns
            for col in numeric_cols:
                # Simple trend detection
                first_half = df[col].iloc[: len(df) // 2].mean()
                second_half = df[col].iloc[len(df) // 2 :].mean()
                if first_half != 0:
                    change = (second_half - first_half) / first_half * 100
                else:
                    change = 0
                trend = "increasing" if change > 5 else "decreasing" if change < -5 else "stable"
                result += f"**{col}:** {trend} ({change:+.1f}%)\n"

        return result

    except Exception as e:
        return f"Error analyzing data: {e!s}"
    finally:
        conn.close()

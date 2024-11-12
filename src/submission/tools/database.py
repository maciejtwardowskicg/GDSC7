from langchain_core.tools import tool
from sqlalchemy import text
from src.static.util import ENGINE

@tool
def query_database(query: str) -> str:
    """Query the PIRLS postgres database and return the results as a string.

    Args:
        query (str): The SQL query to execute.

    Returns:
        str: The results of the query as a string, where each row is separated by a newline.

    Raises:
        Exception: If the query is invalid or encounters an exception during execution.
    """
    # lower_query = query.lower()
    # record_limiters = ['count', 'where', 'limit', 'distinct', 'having', 'group by']
    # if not any(word in lower_query for word in record_limiters):
    #     return 'WARNING! The query you are about to perform has no record limitations! In case of large tables and ' \
    #            'joins this will return an incomprehensible output.'

    with ENGINE.connect() as connection:
        try:
            res = connection.execute(text(query))
        except Exception as e:
            return f'Wrong query, encountered exception {e}.'

    max_result_len = 3_000
    ret = '\n'.join(", ".join(map(str, result)) for result in res)
    if len(ret) > max_result_len:
        ret = ret[:max_result_len] + '...\n(results too long. Output truncated.)'

    return f'Query: {query}\nResult: {ret}'


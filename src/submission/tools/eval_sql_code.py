from langchain_core.tools import tool


@tool
def eval_sql_code(code: str) -> str:
    """
    Evaluate the given PostgreSQL code and return the result.

    Parameters:
    code (str): The PostgreSQL code to be executed.

    Returns:
    str: The result of executing the code. If the code executes successfully, it returns "Code executed successfully."
                 If an exception occurs during execution, it returns the error message as a string.
    """
    import sys
    import io

    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    try:
        exec(code, {})
        result = redirected_output.getvalue()
        return result if result else "Code executed successfully."
    except Exception as e:
        return f"Error during execution: {str(e)}"
    finally:
        sys.stdout = old_stdout
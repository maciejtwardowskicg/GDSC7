@tool
def gather_gdp_data(query: str) -> str:
    """
    Gathers GDP data from a predefined list of tuples if the query contains 'GDP'.
    
    Parameters:
    query (str): The query string to check.

    Returns:
    str: The result containing GDP data in a list of tuples, or an appropriate message.
    """
    try:
        # Check if the query contains 'GDP'
        if "GDP" in query.upper():
            # Return the predefined global variable (gdp_data_source)
            return gdp_data if gdp_data else "No GDP data found."
        else:
            return "No GDP-related information requested in the query."

    except Exception as e:
        # Return an error message if something goes wrong
        return f"Error during data gathering: {str(e)}"
from crewai import Agent, Crew, Process, Task
from crewai.project import agent, crew, task

from src.static.submission import Submission
from src.static.ChatBedrockWrapper import ChatBedrockWrapper
from src.submission.tools.database import query_database
from src.submission.tools.eval_sql_code import eval_sql_code
from src.submission.tools.visualization import visualization
from src.submission.tools.gather_gdp_data import gather_gdp_data



class learningVoyager(Submission):
    def __init__(self, llm: ChatBedrockWrapper):
        self.llm = llm

    def run(self, prompt: str) -> str:
        self.prompt = prompt
        return self.crew().kickoff().raw

    @agent
    def postgreSQL_engineer(self) -> Agent:
        """
        Initializes the PostgreSQL Engineer agent responsible for efficient data retrieval and analysis.

        This agent's primary role is to interpret user questions, translate them into SQL queries, 
        and execute these queries on the database to extract relevant insights from the PIRLS dataset. 
        Designed for seamless integration in a multi-agent architecture, the PostgreSQL Engineer focuses on:

        - Goal: Efficiently retrieve and analyze data to deliver concise, relevant answers.
          Passes insights directly to the Education Expert without delving into technical query details.
        - Visualization Preparation: When visualizations are requested, prepares the data accordingly
          and relays the task to the next agent for chart generation.
        - Humorous Delegation: Redirects unrelated questions to the Education Expert with a humorous touch.

        Returns:
            Agent: An instance of the PostgreSQL Engineer with specific responsibilities in data querying and 
            result preparation.

        Tools:
            - `eval_sql_code`: Evaluates SQL expressions for efficient query formation.
            - `query_database`: Executes database queries to retrieve and prepare data insights.
            - `gather_gdp_data`: Gathers additional data about GDP of countres from gdp_data variable.
        """
        return Agent(
            role="PostgreSQL engineer", 
            backstory=f"{postgreSQL_engineer_backstory}, perfect knowledge of {db_info}. When needed can use data from other sources.",
            goal="Efficiently retrieve and analyze data to provide insightful, concise answers based on user questions. Relay the findings to education expert without discussing the query process. When appropriate, prepare data visualizations and pass unrelated questions to education expert with humor. When visualization is needed pass this request to next agent",
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            tools=[eval_sql_code, query_database, gather_gdp_data]
        )
    
    
    @agent
    def education_expert(self) -> Agent:
        """
        Initializes the Education Expert agent, responsible for synthesizing insights and creating accessible responses.

        This agent receives processed data insights from the PostgreSQL Engineer and distills them into concise, 
        non-technical answers tailored to a professional, educational context. The Education Expert's key responsibilities include:

        - Goal: Selects the most critical insights and results from the data provided by the PostgreSQL Engineer.
          Responds to the user with a short, accessible, and professional answer that reflects a deep understanding 
          of educational concepts and practices.
        - Visualization Creation: When there are at least two data points available, generates a visualization 
          to enhance the user's understanding of the insights.

        Returns:
            Agent: An instance of the Education Expert with specialized functions in data synthesis and visualization.

        Tools:
            - `visualization`: Creates graphical representations of data insights when multiple data points are available.
        """
        return Agent(
            role="Education expert", 
            backstory=f"{writer_backstory}",
            goal="Based on given insights from PostgreSQL engineer - Choose 3 the most important insights and results and give an answer to the user in very short, professional, accesible and non-technical way. You answer as a education expert with huge knowledge about education. When are at least 2 data points you create visualization",
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            tools=[visualization]
        )
    
   
    @task
    def translate_to_sql(self) -> Task:
        """
        Translates user queries into PostgreSQL commands and processes the resulting data.

        This task interprets user input and converts it into SQL queries that are executed on the PostgreSQL database 
        to retrieve relevant data. It performs any necessary analysis using statistical techniques, and the results 
        are passed to the Education Expert in a concise, non-technical way. The task also humorously notifies the 
        Education Expert when a query is unrelated and ensures that sufficient data points are provided for visualizations 
        when needed.

        Returns:
            Task: A task object that describes the process of translating user input into SQL commands and passing data 
            insights to the Education Expert for further synthesis and visualization.

        Expected Output:
            - Actionable insights and necessary data points delivered to the Education Expert.
            - Unrelated questions are humorously flagged.
            - Visualization requests are prepared with sufficient data.
        """
        return Task(
            description=f"based on user input: {self.prompt}. Translate user queries into PostgreSQL commands, retrieve relevant data, and conduct any required analysis. Apply statistical techniques as needed, generating clear, actionable insights. Pass findings to education expert in straightforward language, omitting technical query details and focusing on meaningful data insights. Humorously inform education expert when questions are unrelated. When visualization is needed pass this request to education expert",
            expected_output="Deliver insights and necessary data points to education expert without mentioning query operations. Humorously pass along unrelated questions, ensure visualizations contain sufficient data points.",
            agent=self.postgreSQL_engineer())
    
        
    @task
    def tell_story(self) -> Task:
        """
        Synthesizes and condenses insights into a clear, non-technical response for the user.

        This task creates a brief, professional response based on the insights gathered from the PostgreSQL Engineer 
        and Education Expert. The response is designed to be concise and directly related to the user’s query. 
        The task also includes the option to generate visualizations when appropriate. The output consists of a 
        final answer, a list of key insights (up to 5), and potentially useful tips based on the topic of the question. 
        For unrelated questions, the task includes a disclaimer that the Education Expert doesn't have the information 
        and avoids technical language.

        Returns:
            Task: A task object that synthesizes insights into a condensed response for the user, with added visualizations 
            or useful tips where applicable.

        Expected Output:
            - A very short and condensed answer closely related to the user’s question.
            - A list of up to 5 key insights, each interpreted meaningfully.
            - Up to 3 tips for improving the situation based on the user’s query (e.g., improving student outcomes).
            - A disclaimer for unrelated questions indicating that the Education Expert doesn't have the information.
            - If a visualization is created, it is included in the output.
        """
         return Task(
            description=f"{tell_story_description}.You create visualization when possible",
            expected_output=f"Very Short and condensed answer for: {self.prompt}.Pay atention for answer being closely related to the question asked. give final answer to user then - choose 3 key insights with use hyphens - You can make interpretation what this result could mean. if question specifies - At the end you can give up to 3 useful tips with hyphens (for example: how to improve students results in the future or improve schooling systems, improve teaching) based on question's topic. You can't tell what queries were made or what other agents said. Avoid technical language. For question is unrelated with PIRLS dataset you can tell as a education expert you don't know how to. If visualization is created with visualization tool - put an output to your answer",
            agent=self.education_expert(),
        )
        
        


    @crew
    def crew(self) -> Crew:
        """
        Initializes the CrewAI system, orchestrating the interaction between agents and tasks.

        This method sets up the CrewAI with a list of agents and tasks that work together in a 
        sequential process. The Crew is configured to execute a maximum of 4 iterations and 
        caches results to improve performance. The `verbose` flag enables detailed logging 
        to track the process.

        Returns:
            Crew: An instance of the CrewAI that manages the agents and tasks in a sequential process.

        Configuration:
            - `agents`: List of agents involved in the process.
            - `tasks`: List of tasks assigned to the agents.
            - `process`: Defines the execution process as sequential.
            - `verbose`: Enables detailed logging for the process.
            - `max_iter`: Sets the maximum number of iterations to 4.
            - `cache`: Enables caching for efficient execution.
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_iter=3,
            cache=True
        )


db_info = '''
    The PIRLS dataset structure
    The data is stored in a PostgreQSL database.
      
    Schema and explanation:'
    Students
    Student_ID: Int (Primary Key) - uniquely identifies student
    Country_ID: Int (Foreign Key) - uniquely identifies student's country
    School_ID: Int (Foreign Key) - uniquely identifies student's school
    Home_ID: Int (Foreign Key) - uniquely identifies student's home

    StudentQuestionnaireEntries
    Code: String (Primary Key) - uniquely identifies a question
    Question: String - the question
    Type: String - describes the type of the question
    
    StudentQuestionnaireAnswers
    Student_ID: Int (Foreign Key) - references student from the Student table
    Code: String (Foreign Key) - references question code from StudentQuestionnaireEntries table
    Answer: String - contains the answer to the question

    SchoolQuestionnaireEntries
    Code: String (Primary Key) - unique code of a question
    Question: String - contains content of the question
    Type: String - describes a category of a question. There are several questions in each category. The categories are: Instructional Time, Reading in Your School, School Emphasis on Academic Success, School Enrollment and Characteristics, Students’ Literacy Readiness, Principal Experience and Education, COVID-19 Pandemic, Resources and Technology, School Discipline and Safety

    SchoolQuestionnaireAnswers
    School_ID: Int (Composite Key) - references school from Schools table
    Code: String (Composite Key) - references score code from SchoolQuestionnaireEntries table
    Answer: String - answer to the question from the school

    TeacherQuestionnaireEntries
    Code: String (Primary Key)
    Question: String
    Type: String

    TeacherQuestionnaireAnswers
    Teacher_ID: Int (Foreign Key) - references teacher from Teachers table
    Code: String (Foreign Key) - references score code from TeacherQuestionnaireEntries table
    Answer: String - answer to the question from the teacher

    HomeQuestionnaireEntries
    Code: String (Primary Key)
    Question: String
    Type: String

    HomeQuestionnaireAnswers
    Home_ID: Int (Foreign Key)
    Code: String (Foreign Key)
    Answer: String

    CurriculumQuestionnaireEntries
    Code: String (Primary Key)
    Question: String
    Type: String

    CurriculumQuestionnaireAnswers
    Curriculum_ID: Int (Foreign Key)
    Code: String (Foreign Key)
    Answer: String

    Schools
    School_ID: Int (Primary Key) - uniquely identifies a School
    Country_ID: Int (Foreign Key) - uniquely identifies a country

    Teachers
    Teacher_ID: Int (Primary Key) - uniquely identifies a Teacher
    School_ID: Int (Foreign Key) - uniquely identifies a School

    StudentTeachers
    Teacher_ID: Int (Foreign Key)
    Student_ID: Int (Foreign Key)

    Homes
    Home_ID: Int (Primary Key) - uniquely identifies a Home

    Curricula
    Curriculum_ID: Int (Primary Key)
    Country_ID: Int (Foreign Key)

    StudentScoreEntries
    Code: String (Primary Key) - See below for examples of codes
    Name: String
    Type: String

    StudentScoreResults
    Student_ID: Int (Foreign Key) - references student from Students table
    Code: String (Foreign Key) - references score code from StudentScoreEntries table
    Score: Float - the numeric score for a student

    Benchmarks
    Benchmark_ID: Int (Primary Key) - uniquely identifies benchmark
    Score: Int - the lower bound of the benchmark. Students that are equal to or above this value are of that category
    Students' scores are in studentscoreresults and can be classified and labeled according to benchmarks table. (If the score is less than 400, it indicates the student didn't reach even the low level.)
    Low scores cannot be described as "top", "high"
    High scores cannot be described as low. High scores are good but there is sill for improvement.
    Advanced International Benchmark - it's the highest standard to reach. If many student reach it - that is good


    Countries
    Country_ID: Int (Primary Key) - uniquely identifies a country
    Name: String - full name of the country
    Code: String - 3 letter code of the country
    Benchmark: Boolean - boolean value saying if the country was a benchmark country. 
    TestType: String - describes the type of test taken in this country. It's either digital or paper.
    '
    
    # Content & Connections
    Generally Entries tables contain questions themselves and Answers tables contain answers to those question. 
    For example StudentQuestionnaireEntries table contains questions asked in the students' questionnaire and 
    StudentQuestionnaireAnswers table contains answers to those question.
    
    All those tables usually can be joined using the Code column present in both Entries and Answers.
    
    Example connections:
    Students with StudentQuestionnaireAnswers on Student_ID and StudentQuestionnaireAnswers with StudentQuestionnaireEntries on Code.
    Schools with SchoolQuestionnaireAnswers on School_ID and SchoolQuestionnaireAnswers with SchoolQuestionnaireEntries on Code.
    Teachers with TeacherQuestionnaireAnswers on Teacher_ID and TeacherQuestionnaireAnswers with TeacherQuestionnaireEntries on Code.
    Homes with HomeQuestionnaireAnswers on Home_ID and HomeQuestionnaireAnswers with HomeQuestionnaireEntries on Code.
    Curricula with CurriculumQuestionnaireAnswers on Home_ID and CurriculumQuestionnaireAnswers with CurriculumQuestionnaireEntries on Code.
     
    In the student evaluation process 5 distinct scores were measured. The measured codes in StudentScoreEntries are:
    - ASRREA_avg and ASRREA_std describe the overall reading score average and standard deviation
    - ASRLIT_avg and ASRLIT_std describe literary experience score average and standard deviation
    - ASRINF_avg and ASRINF_std describe the score average and standard deviation in acquiring and information usage
    - ASRIIE_avg and ASRIIE_std describe the score average and standard deviation in interpreting, integrating and evaluating
    - ASRRSI_avg and ASRRSI_avg describe the score average and standard deviation in retrieving and straightforward inferencing
        
    Benchmarks table cannot be joined with any other table but it keeps useful information about how to interpret
    student score as one of the 4 categories.   
    
    Examples
    A students' gender is stored as an answer to one of the questions in StudentQuestionnaireEntries table.
    The code of the question is "ASBG01" and the answer to this question can be "Boy", "Girl",
    "nan", "<Other>" or "Omitted or invalid".
    
    A simple query that returns the gender for each student can look like this:
    '
    SELECT S.Student_ID,
       CASE 
           WHEN SQA.Answer = 'Boy' THEN 'Male'
           WHEN SQA.Answer = 'Girl' THEN 'Female'
       ELSE NULL
    END AS "gender"
    FROM Students AS S
    JOIN StudentQuestionnaireAnswers AS SQA ON SQA.Student_ID = S.Student_ID
    JOIN StudentQuestionnaireEntries AS SQE ON SQE.Code = SQA.Code
    WHERE SQA.Code = 'ASBG01'
    '

Examples - treat this only as instrucition: 
'
    Get the total number of {students}:
‘
SELECT COUNT(*) AS StudentCount
FROM {Students} 
LIMIT 1000;
‘

Get the total number of {teachers}:
‘
SELECT COUNT(*) AS TeacherCount
FROM {Teachers} 
LIMIT 1000;
‘


Get total number of students from {France}:
‘
    SELECT COUNT(DISTINCT S.Student_ID) AS StudentsFromFrance
    FROM students AS S
    JOIN countries AS C ON C.Country_ID = S.Country_ID
    WHERE C.Name = {'France'};
‘

Finding questions about COVID-19 or COVID or pandemic:
‘
    SELECT * FROM SchoolQuestionnaireEntries WHERE Type = 'COVID-19 Pandemic';
‘


Finding questions about safety or bullying can be achieved by searching types of questions and coresponding answers based on students ID, for example:
    'SELECT * FROM StudentQuestionnaireEntries WHERE Type = 'Bullying' GROUP BY student_id;'



Finding schools and countries that were affected from Covid – based for how long they were affected
‘
SELECT C.Name, S.School_ID, SQA.Code, SQA.Answer FROM SchoolQuestionnaireAnswers AS SQA
JOIN Schools AS S ON S.School_ID = SQA.School_ID
JOIN Countries AS C ON C.Country_ID = S.Country_ID
WHERE SQA.Code = 'ACBG19' AND SQA.Answer = 'More than eight weeks of instruction';
‘


Which country had all schools closed for more than eight weeks?
‘
    WITH schools_all AS (
    SELECT C.Name, COUNT(S.School_ID) AS schools_in_country
    FROM Schools AS S
    JOIN Countries AS C ON C.Country_ID = S.Country_ID
    GROUP BY C.Name
    ),
    schools_closed AS (
        SELECT C.Name, COUNT(DISTINCT SQA.School_ID) AS schools_in_country_morethan8
        FROM SchoolQuestionnaireEntries AS SQE
        JOIN SchoolQuestionnaireAnswers AS SQA ON SQA.Code = SQE.Code
        JOIN Schools AS S ON S.School_ID = SQA.School_ID
        JOIN Countries AS C ON C.Country_ID = S.Country_ID
        WHERE SQE.Code = 'ACBG19' AND SQA.Answer = 'More than eight weeks of instruction'
        GROUP BY C.Name
    ),
    percentage_calc AS (
        SELECT A.Name, schools_in_country_morethan8 / schools_in_country::float * 100 AS percentage
        FROM schools_all A
        JOIN schools_closed CL ON A.Name = CL.Name
    )
    SELECT *
    FROM percentage_calc
    WHERE percentage = 100;
‘

What percentage of students in Poland reached the Advanced International Benchmark?
‘
    WITH benchmark_score AS (
        SELECT Score FROM Benchmarks
        WHERE Name = Advanced International Benchmark'
    )
    SELECT SUM(CASE WHEN SSR.score >= bs.Score THEN 1 ELSE 0 END) / COUNT(*)::float as percentage
    FROM Students AS S
    JOIN Countries AS C ON C.Country_ID = S.Country_ID
    JOIN StudentScoreResults AS SSR ON SSR.Student_ID = S.Student_ID
    CROSS JOIN benchmark_score AS bs
    WHERE C.Name = 'Poland' AND SSR.Code = 'ASRREA_avg'
'
'

When a query asks for information about a percentage of students achieving a specific benchmark (such as "at least 55% of students reaching the Low International Benchmark"), follow these steps to handle the query:

Entity Recognition:

Identify the primary subject of the query, which could be "countries," "schools," or another entity.
Determine the target metric, such as the "percentage of students."
Identify the condition, such as "at least 55%" or any other threshold percentage.
Recognize the specific benchmark level, such as "Low International Benchmark," "Intermediate Benchmark," or similar.
Translate Query into SQL:

Step 1: Use SELECT to specify the desired output (e.g., counting distinct countries).
Step 2: From the relevant table(s) in the schema, such as country_benchmarks, student_performance, or another table where the percentage and benchmark data are stored.
Step 3: Apply the WHERE clause to filter records based on the benchmark and percentage condition.
Step 4: Return the number of entities that meet the criteria.
SQL Query Template: Here’s the SQL query template to follow:

sql
Copy code
SELECT COUNT(DISTINCT country_id)
FROM country_benchmarks
WHERE percentage_students >= {percentage_threshold}
  AND benchmark_level = '{benchmark_name}';
Input Breakdown:

Replace {percentage_threshold} with the numeric value provided in the query (e.g., 55 for "at least 55%").
Replace {benchmark_name} with the benchmark level (e.g., 'Low International Benchmark').
Edge Cases:

If the query includes a different benchmark level, such as "Intermediate Benchmark," modify the benchmark_level condition accordingly.
If the query involves additional conditions, like different years or regions, include these as extra conditions in the WHERE clause.
Examples:

Input: "How many countries reported that at least 55% of their students reached the Low International Benchmark?"

SQL Output:
sql
Copy code
SELECT COUNT(DISTINCT country_id)
FROM country_benchmarks
WHERE percentage_students >= 55
  AND benchmark_level = 'Low International Benchmark';
Input: "How many countries had over 90% of students achieving the Intermediate Benchmark?"

SQL Output:
sql
Copy code
SELECT COUNT(DISTINCT country_id)
FROM country_benchmarks
WHERE percentage_students > 90
  AND benchmark_level = 'Intermediate Benchmark';
By following this process, you will effectively translate user queries into SQL statements that retrieve the correct information. Make sure to handle potential variations in benchmark levels, percentage thresholds, and other conditions.

End of instructions


Tips: Try optimize queries, especially the more complex ones. For example use:
-CTEs
-Window Functions
-Lateral Joins
-Full Text Search:
-EXPLAIN ANALYZE
-Efficient Date Handling:
-Array Operations
-Efficient Pagination
-With questions about "how many" remember to use COUNT

'''


postgreSQL_engineer_backstory =  f'''
You are a proficient data analyst and PostgreSQL expert with deep knowledge of the PIRLS dataset and schema. Your main role is to respond to natural language questions by translating them into efficient SQL queries, gathering and analyzing data, and delivering concise, insightful responses. You apply various statistical techniques when needed, such as descriptive, inferential, and predictive analysis, to ensure thorough answers.

For complex questions, you break down key components, identify relevant influences (e.g., socioeconomic or cultural factors), and analyze each aspect. When a question isn’t related to the dataset, you humorously notify the data presentation agent, 'education expert' You make sure your responses are informative and clear, free of technical query details, and always you generate enough data points for visualizations.
When visualization is needed pass this request to education expert
'''

writer_backstory = '''
    You always answer like a education expert.
    You have good knowledge about education, teaching, children.
    When are at least 2 data points - you create visualizations and you use visualization tool - and put outcome to your answer
    Capable in answering user's question in interesting, professional, accesible and non-technical way - supported by the data.
    You can choose which information from PostgreSQL engineer is relevant to asked question
    you create visualizations - and put outcome to your answer
    You make sure that your answer do not go beyond asked question.
    If question is simple, you give simple answer
    You give 1 sentence introduction and give the answer.
    You answer the question based on the dataset but also expanding answer according on your knowledge about learning techiques and schooling systems.
    You give great tips and conclusions.
    If you don't have the proper answer from PostgreSQL engineer - do not admit it.
    Avoid words like "postgreSQL","queries","query","tables" - instead use phrases like: "data says...","based on data..." etc.
    You pay extra attention to ensuring if your answer is answering the question
    You provide a summary of the results without including any details about the SQL queries or methods used to retrieve them. Focus solely on the data and insights derived from the results.
    If PostgreSQL engineer gives you insights that contain information about how result was calculated - skip this information!
    you give very, very short and condensed answers.
'''

tell_story_description= '''
    You always answer like a education expert.
    You have good knowledge about education, teaching, children.
    make the answer to be professional, interesting and easy to read.
    When are at least 2 data points - you create visualizations and you use visualization tool - and put outcome to your answer
    avoid technical language
    if you don't have the proper answer from PostgreSQL engineer - say that further analysis is needed
    Avoid words like "postgreSQL","queries","query" - instead use phrases like: "data says...","based on data..." etc.
    If question is unrelated with PIRLS dataset you can tell as a education expert you don't know how to.
    in your answer You can't mention that data was provided by posgreSQL engineer
    You can't mention your thoughts
    you give short and condensed answers.
'''


gdp_data = [('Australia', 1723827000000), ('Austria', 516034000000), ('Azerbaijan', 72356000000), ('Bahrain', 43205000000), ('Belgium', 632217000000), ('Brazil', 2173666000000), ('Croatia', 82689000000), ('Cyprus', 32230000000), ('Czech Republic', 330858000000), ('Denmark', 404199000000), ('Egypt', 395926000000), ('Finland', 300187000000), ('France', 3030904000000), ('Georgia', 30536000000), ('Germany', 4456081000000), ('Hong Kong SAR, China', 382055000000), ('Hungary', 212389000000), ('Iran, Islamic Rep.', 401505000000), ('Ireland', 545629000000), ('Israel', 509901000000), ('Italy', 2254851000000), ('Jordan', 50814000000), ('Kazakhstan', 261421000000), ('Kosovo', 10438000000), ('Latvia', 43627000000), ('Lithuania', 77836000000), ('Macao SAR, China', 382055000000), ('Malta', 20957000000), ('Montenegro', 7405000000), ('Morocco', 141109000000), ('Netherlands', 1118125000000), ('New Zealand', 253466000000), ('North Macedonia', 14761000000), ('Norway', 485513000000), ('Oman', 108192000000), ('Portugal', 287080000000), ('Qatar', 235770000000), ('Russian Federation', 2021421000000), ('Saudi Arabia', 1067583000000), ('Serbia', 75187000000), ('Singapore', 501428000000), ('Slovak Republic', 132794000000), ('Slovenia', 68217000000), ('South Africa', 377782000000), ('Spain', 1580695000000), ('Sweden', 593268000000), ('Türkiye', 1118125000000), ('United Arab Emirates', 504173000000), ('United States', 27360935000000), ('Uzbekistan', 90889000000), ('Alberta, Canada', 2140086000000), ('British Columbia, Canada', 2140086000000), ('Newfoundland & Labrador, Canada', 2140086000000), ('Quebec, Canada', 2140086000000), ('Moscow City, Russian Federation', 2021421000000), ('South Africa', 377782000000), ('Bulgaria', 101584000000), ('Taiwan, China', 1180000000000), ('United Kingdom', 3340032000000), ('Dubai, United Arab Emirates', 504173000000), ('Abu Dhabi, United Arab Emirates', 504173000000), ('Albania', 22978000000), ('Poland', 811229000000)]

"""
Seed script to populate the database with initial questions
Run this after setting up the application: python seed_data.py
"""

from app import create_app, mongo
from datetime import datetime

app = create_app()

# Question data organized by category
QUESTIONS = {
    'DSA': [
        {
            'question_text': 'What is the time complexity of binary search?',
            'options': ['O(n)', 'O(log n)', 'O(n²)', 'O(1)'],
            'correct_answer': 'O(log n)',
            'explanation': 'Binary search divides the search space in half with each iteration, resulting in logarithmic time complexity.',
            'difficulty': 'easy',
            'tags': ['algorithms', 'searching', 'binary search']
        },
        {
            'question_text': 'Which data structure uses LIFO (Last In First Out) principle?',
            'options': ['Queue', 'Stack', 'Linked List', 'Tree'],
            'correct_answer': 'Stack',
            'explanation': 'Stack follows LIFO principle where the last element added is the first one to be removed.',
            'difficulty': 'easy',
            'tags': ['data structures', 'stack']
        },
        {
            'question_text': 'What is the worst-case time complexity of QuickSort?',
            'options': ['O(n log n)', 'O(n²)', 'O(n)', 'O(log n)'],
            'correct_answer': 'O(n²)',
            'explanation': 'QuickSort has O(n²) worst case when the pivot selection consistently results in unbalanced partitions.',
            'difficulty': 'medium',
            'tags': ['algorithms', 'sorting', 'quicksort']
        },
        {
            'question_text': 'Which traversal visits the root node first in a binary tree?',
            'options': ['Inorder', 'Preorder', 'Postorder', 'Level order'],
            'correct_answer': 'Preorder',
            'explanation': 'Preorder traversal visits nodes in the order: Root, Left, Right.',
            'difficulty': 'easy',
            'tags': ['data structures', 'trees', 'traversal']
        },
        {
            'question_text': 'What is the space complexity of merge sort?',
            'options': ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'],
            'correct_answer': 'O(n)',
            'explanation': 'Merge sort requires additional space proportional to the input size for the merging process.',
            'difficulty': 'medium',
            'tags': ['algorithms', 'sorting', 'merge sort']
        },
        {
            'question_text': 'Which data structure is best for implementing a priority queue?',
            'options': ['Array', 'Linked List', 'Heap', 'Stack'],
            'correct_answer': 'Heap',
            'explanation': 'Heap provides O(log n) insertion and O(1) access to the highest/lowest priority element.',
            'difficulty': 'medium',
            'tags': ['data structures', 'heap', 'priority queue']
        },
        {
            'question_text': 'What is the time complexity of accessing an element in a hash table (average case)?',
            'options': ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'],
            'correct_answer': 'O(1)',
            'explanation': 'Hash tables provide constant time access on average due to direct indexing using hash functions.',
            'difficulty': 'easy',
            'tags': ['data structures', 'hash table']
        },
        {
            'question_text': 'Which algorithm is used to find the shortest path in an unweighted graph?',
            'options': ['DFS', 'BFS', 'Dijkstra', 'Bellman-Ford'],
            'correct_answer': 'BFS',
            'explanation': 'BFS explores nodes level by level, guaranteeing the shortest path in unweighted graphs.',
            'difficulty': 'medium',
            'tags': ['algorithms', 'graphs', 'bfs']
        },
        {
            'question_text': 'What is the maximum number of nodes at level k in a binary tree?',
            'options': ['k', '2k', '2^k', '2^(k-1)'],
            'correct_answer': '2^k',
            'explanation': 'At level k (starting from 0), the maximum number of nodes is 2^k.',
            'difficulty': 'medium',
            'tags': ['data structures', 'trees', 'binary tree']
        },
        {
            'question_text': 'Which sorting algorithm is most efficient for nearly sorted data?',
            'options': ['QuickSort', 'MergeSort', 'Insertion Sort', 'Selection Sort'],
            'correct_answer': 'Insertion Sort',
            'explanation': 'Insertion sort has O(n) complexity for nearly sorted data as elements need minimal shifts.',
            'difficulty': 'medium',
            'tags': ['algorithms', 'sorting', 'insertion sort']
        }
    ],
    'Python': [
        {
            'question_text': 'What is the output of print(type([]))?',
            'options': ["<class 'list'>", "<class 'array'>", "<class 'tuple'>", "<class 'dict'>"],
            'correct_answer': "<class 'list'>",
            'explanation': 'Empty square brackets [] create an empty list in Python.',
            'difficulty': 'easy',
            'tags': ['python', 'data types', 'list']
        },
        {
            'question_text': 'Which keyword is used to define a generator function in Python?',
            'options': ['return', 'yield', 'generate', 'iter'],
            'correct_answer': 'yield',
            'explanation': 'The yield keyword is used to create generator functions that return values lazily.',
            'difficulty': 'medium',
            'tags': ['python', 'generators', 'functions']
        },
        {
            'question_text': 'What is the purpose of __init__ method in Python classes?',
            'options': ['To destroy an object', 'To initialize an object', 'To copy an object', 'To compare objects'],
            'correct_answer': 'To initialize an object',
            'explanation': '__init__ is the constructor method called when creating a new instance of a class.',
            'difficulty': 'easy',
            'tags': ['python', 'oop', 'classes']
        },
        {
            'question_text': 'What does the "self" parameter represent in a Python class method?',
            'options': ['The class itself', 'The instance of the class', 'A global variable', 'The parent class'],
            'correct_answer': 'The instance of the class',
            'explanation': 'self refers to the current instance of the class and is used to access instance attributes and methods.',
            'difficulty': 'easy',
            'tags': ['python', 'oop', 'self']
        },
        {
            'question_text': 'Which of the following is immutable in Python?',
            'options': ['List', 'Dictionary', 'Set', 'Tuple'],
            'correct_answer': 'Tuple',
            'explanation': 'Tuples are immutable sequences in Python - their elements cannot be modified after creation.',
            'difficulty': 'easy',
            'tags': ['python', 'data types', 'tuple']
        },
        {
            'question_text': 'What is a decorator in Python?',
            'options': ['A class attribute', 'A function that modifies another function', 'A type of loop', 'A data structure'],
            'correct_answer': 'A function that modifies another function',
            'explanation': 'Decorators are functions that take another function and extend its behavior without modifying it.',
            'difficulty': 'medium',
            'tags': ['python', 'decorators', 'functions']
        },
        {
            'question_text': 'What is the difference between "==" and "is" in Python?',
            'options': ['No difference', '"==" compares values, "is" compares identity', '"is" compares values, "==" compares identity', 'Both compare identity'],
            'correct_answer': '"==" compares values, "is" compares identity',
            'explanation': '"==" checks if values are equal, while "is" checks if two variables point to the same object in memory.',
            'difficulty': 'medium',
            'tags': ['python', 'operators', 'comparison']
        },
        {
            'question_text': 'What does the GIL (Global Interpreter Lock) do in Python?',
            'options': ['Allows multiple threads to execute Python bytecode simultaneously', 'Prevents multiple threads from executing Python bytecode simultaneously', 'Manages memory allocation', 'Handles exceptions'],
            'correct_answer': 'Prevents multiple threads from executing Python bytecode simultaneously',
            'explanation': 'The GIL ensures only one thread executes Python bytecode at a time, simplifying memory management.',
            'difficulty': 'hard',
            'tags': ['python', 'threading', 'gil']
        },
        {
            'question_text': 'What is the output of list(range(0, 10, 2))?',
            'options': ['[0, 2, 4, 6, 8]', '[0, 2, 4, 6, 8, 10]', '[2, 4, 6, 8]', '[0, 1, 2, 3, 4]'],
            'correct_answer': '[0, 2, 4, 6, 8]',
            'explanation': 'range(0, 10, 2) generates numbers from 0 to 9 with step 2.',
            'difficulty': 'easy',
            'tags': ['python', 'range', 'sequences']
        },
        {
            'question_text': 'What is a lambda function in Python?',
            'options': ['A named function', 'An anonymous function', 'A recursive function', 'A class method'],
            'correct_answer': 'An anonymous function',
            'explanation': 'Lambda functions are small anonymous functions defined with the lambda keyword.',
            'difficulty': 'easy',
            'tags': ['python', 'lambda', 'functions']
        }
    ],
    'JavaScript': [
        {
            'question_text': 'What is the difference between let and var in JavaScript?',
            'options': ['No difference', 'let is block-scoped, var is function-scoped', 'var is block-scoped, let is function-scoped', 'let is for constants'],
            'correct_answer': 'let is block-scoped, var is function-scoped',
            'explanation': 'let has block scope while var has function scope, making let more predictable.',
            'difficulty': 'easy',
            'tags': ['javascript', 'variables', 'scope']
        },
        {
            'question_text': 'What does the "===" operator do in JavaScript?',
            'options': ['Compares only values', 'Compares values and types', 'Assigns a value', 'Compares references'],
            'correct_answer': 'Compares values and types',
            'explanation': '=== is the strict equality operator that checks both value and type without type coercion.',
            'difficulty': 'easy',
            'tags': ['javascript', 'operators', 'comparison']
        },
        {
            'question_text': 'What is a closure in JavaScript?',
            'options': ['A way to close a browser window', 'A function with access to its outer scope', 'A type of loop', 'An error handling mechanism'],
            'correct_answer': 'A function with access to its outer scope',
            'explanation': 'A closure is a function that remembers variables from its outer scope even after the outer function has returned.',
            'difficulty': 'medium',
            'tags': ['javascript', 'closures', 'functions']
        },
        {
            'question_text': 'What is the purpose of the "async" keyword in JavaScript?',
            'options': ['To create a synchronous function', 'To create an asynchronous function that returns a Promise', 'To pause execution', 'To handle errors'],
            'correct_answer': 'To create an asynchronous function that returns a Promise',
            'explanation': 'async functions always return a Promise and allow the use of await inside them.',
            'difficulty': 'medium',
            'tags': ['javascript', 'async', 'promises']
        },
        {
            'question_text': 'What is the output of typeof null in JavaScript?',
            'options': ["'null'", "'undefined'", "'object'", "'boolean'"],
            'correct_answer': "'object'",
            'explanation': 'This is a known bug in JavaScript. typeof null returns "object" due to how types were originally implemented.',
            'difficulty': 'medium',
            'tags': ['javascript', 'types', 'quirks']
        },
        {
            'question_text': 'What is event bubbling in JavaScript?',
            'options': ['Events start from the target and propagate up to ancestors', 'Events start from ancestors and propagate down', 'Events only trigger on the target', 'Events trigger randomly'],
            'correct_answer': 'Events start from the target and propagate up to ancestors',
            'explanation': 'Event bubbling means an event triggers on the target element first, then bubbles up through its ancestors.',
            'difficulty': 'medium',
            'tags': ['javascript', 'events', 'dom']
        },
        {
            'question_text': 'What is the purpose of the spread operator (...) in JavaScript?',
            'options': ['To spread butter', 'To expand iterables into individual elements', 'To create loops', 'To define functions'],
            'correct_answer': 'To expand iterables into individual elements',
            'explanation': 'The spread operator expands arrays or objects into individual elements or properties.',
            'difficulty': 'easy',
            'tags': ['javascript', 'spread operator', 'es6']
        },
        {
            'question_text': 'What is a Promise in JavaScript?',
            'options': ['A guarantee of code execution', 'An object representing eventual completion or failure of an async operation', 'A type of function', 'A debugging tool'],
            'correct_answer': 'An object representing eventual completion or failure of an async operation',
            'explanation': 'Promises handle asynchronous operations and can be in pending, fulfilled, or rejected states.',
            'difficulty': 'medium',
            'tags': ['javascript', 'promises', 'async']
        },
        {
            'question_text': 'What does Array.prototype.map() return?',
            'options': ['The original array', 'A new array with transformed elements', 'undefined', 'A boolean'],
            'correct_answer': 'A new array with transformed elements',
            'explanation': 'map() creates a new array with the results of calling a function on every element.',
            'difficulty': 'easy',
            'tags': ['javascript', 'arrays', 'methods']
        },
        {
            'question_text': 'What is hoisting in JavaScript?',
            'options': ['Moving code to a server', 'Moving declarations to the top of their scope', 'Removing unused code', 'Compressing code'],
            'correct_answer': 'Moving declarations to the top of their scope',
            'explanation': 'JavaScript hoists variable and function declarations to the top of their scope during compilation.',
            'difficulty': 'medium',
            'tags': ['javascript', 'hoisting', 'scope']
        }
    ],
    'Web Development': [
        {
            'question_text': 'What does REST stand for?',
            'options': ['Random Execution State Transfer', 'Representational State Transfer', 'Request State Transfer', 'Resource State Transfer'],
            'correct_answer': 'Representational State Transfer',
            'explanation': 'REST is an architectural style for designing networked applications using stateless communication.',
            'difficulty': 'easy',
            'tags': ['web', 'rest', 'api']
        },
        {
            'question_text': 'Which HTTP method is used to update a resource?',
            'options': ['GET', 'POST', 'PUT', 'DELETE'],
            'correct_answer': 'PUT',
            'explanation': 'PUT is used to update or replace an existing resource at a specified URL.',
            'difficulty': 'easy',
            'tags': ['web', 'http', 'methods']
        },
        {
            'question_text': 'What is CORS in web development?',
            'options': ['A CSS framework', 'Cross-Origin Resource Sharing', 'A JavaScript library', 'A database system'],
            'correct_answer': 'Cross-Origin Resource Sharing',
            'explanation': 'CORS is a security mechanism that allows or restricts resources on a web page from another domain.',
            'difficulty': 'medium',
            'tags': ['web', 'security', 'cors']
        },
        {
            'question_text': 'What is the purpose of a CDN?',
            'options': ['To write code', 'To deliver content from servers closest to users', 'To create databases', 'To manage domains'],
            'correct_answer': 'To deliver content from servers closest to users',
            'explanation': 'CDNs distribute content across multiple servers globally to reduce latency and improve load times.',
            'difficulty': 'easy',
            'tags': ['web', 'cdn', 'performance']
        },
        {
            'question_text': 'What HTTP status code indicates a successful request?',
            'options': ['200', '301', '404', '500'],
            'correct_answer': '200',
            'explanation': 'HTTP 200 OK indicates that the request was successful.',
            'difficulty': 'easy',
            'tags': ['web', 'http', 'status codes']
        },
        {
            'question_text': 'What is the purpose of JWT (JSON Web Token)?',
            'options': ['To style web pages', 'To securely transmit information between parties', 'To create databases', 'To compress images'],
            'correct_answer': 'To securely transmit information between parties',
            'explanation': 'JWT is used for authentication and information exchange in a secure, compact, and self-contained way.',
            'difficulty': 'medium',
            'tags': ['web', 'security', 'jwt', 'authentication']
        },
        {
            'question_text': 'What is server-side rendering (SSR)?',
            'options': ['Rendering on the client browser', 'Generating HTML on the server before sending to client', 'A CSS technique', 'A database operation'],
            'correct_answer': 'Generating HTML on the server before sending to client',
            'explanation': 'SSR renders the initial page on the server, improving SEO and initial load performance.',
            'difficulty': 'medium',
            'tags': ['web', 'ssr', 'rendering']
        },
        {
            'question_text': 'What is the difference between cookies and localStorage?',
            'options': ['No difference', 'Cookies are sent with HTTP requests, localStorage is not', 'localStorage is sent with HTTP requests', 'Cookies are larger'],
            'correct_answer': 'Cookies are sent with HTTP requests, localStorage is not',
            'explanation': 'Cookies are automatically sent with every HTTP request, while localStorage data stays on the client.',
            'difficulty': 'medium',
            'tags': ['web', 'storage', 'cookies']
        },
        {
            'question_text': 'What is WebSocket used for?',
            'options': ['Styling web pages', 'Full-duplex communication between client and server', 'Database queries', 'File uploads only'],
            'correct_answer': 'Full-duplex communication between client and server',
            'explanation': 'WebSocket enables real-time, bidirectional communication between client and server.',
            'difficulty': 'medium',
            'tags': ['web', 'websocket', 'real-time']
        },
        {
            'question_text': 'What is the purpose of a web framework?',
            'options': ['To design logos', 'To provide structure and tools for building web applications', 'To host websites', 'To create animations'],
            'correct_answer': 'To provide structure and tools for building web applications',
            'explanation': 'Web frameworks provide reusable code, patterns, and tools to simplify web development.',
            'difficulty': 'easy',
            'tags': ['web', 'framework', 'development']
        }
    ],
    'Database': [
        {
            'question_text': 'What does SQL stand for?',
            'options': ['Structured Query Language', 'Simple Query Language', 'Standard Query Logic', 'System Query Language'],
            'correct_answer': 'Structured Query Language',
            'explanation': 'SQL is the standard language for managing and querying relational databases.',
            'difficulty': 'easy',
            'tags': ['database', 'sql']
        },
        {
            'question_text': 'What is a primary key in a database?',
            'options': ['The first column', 'A unique identifier for each row', 'A foreign key reference', 'An index'],
            'correct_answer': 'A unique identifier for each row',
            'explanation': 'A primary key uniquely identifies each record in a table and cannot contain NULL values.',
            'difficulty': 'easy',
            'tags': ['database', 'keys', 'primary key']
        },
        {
            'question_text': 'What is normalization in databases?',
            'options': ['Making data normal', 'Organizing data to reduce redundancy', 'Encrypting data', 'Compressing data'],
            'correct_answer': 'Organizing data to reduce redundancy',
            'explanation': 'Normalization organizes tables to minimize data redundancy and improve data integrity.',
            'difficulty': 'medium',
            'tags': ['database', 'normalization', 'design']
        },
        {
            'question_text': 'What is the difference between SQL and NoSQL databases?',
            'options': ['No difference', 'SQL is relational, NoSQL is non-relational', 'NoSQL is older', 'SQL is faster'],
            'correct_answer': 'SQL is relational, NoSQL is non-relational',
            'explanation': 'SQL databases use structured tables with relationships, while NoSQL databases use flexible schemas.',
            'difficulty': 'easy',
            'tags': ['database', 'sql', 'nosql']
        },
        {
            'question_text': 'What is an index in a database?',
            'options': ['A list of tables', 'A data structure that improves query speed', 'A type of join', 'A backup system'],
            'correct_answer': 'A data structure that improves query speed',
            'explanation': 'Indexes help databases find data faster by creating a sorted structure for quick lookups.',
            'difficulty': 'easy',
            'tags': ['database', 'index', 'performance']
        },
        {
            'question_text': 'What is ACID in database transactions?',
            'options': ['A chemical property', 'Atomicity, Consistency, Isolation, Durability', 'A query type', 'A backup method'],
            'correct_answer': 'Atomicity, Consistency, Isolation, Durability',
            'explanation': 'ACID properties ensure database transactions are processed reliably.',
            'difficulty': 'medium',
            'tags': ['database', 'acid', 'transactions']
        },
        {
            'question_text': 'What is a JOIN in SQL?',
            'options': ['Creating a new table', 'Combining rows from two or more tables', 'Deleting data', 'Creating an index'],
            'correct_answer': 'Combining rows from two or more tables',
            'explanation': 'JOIN combines rows from multiple tables based on a related column between them.',
            'difficulty': 'easy',
            'tags': ['database', 'sql', 'join']
        },
        {
            'question_text': 'What is MongoDB?',
            'options': ['A SQL database', 'A document-oriented NoSQL database', 'A programming language', 'A web framework'],
            'correct_answer': 'A document-oriented NoSQL database',
            'explanation': 'MongoDB stores data in flexible, JSON-like documents instead of traditional tables.',
            'difficulty': 'easy',
            'tags': ['database', 'mongodb', 'nosql']
        },
        {
            'question_text': 'What is sharding in databases?',
            'options': ['Breaking data', 'Distributing data across multiple servers', 'Encrypting data', 'Backing up data'],
            'correct_answer': 'Distributing data across multiple servers',
            'explanation': 'Sharding horizontally partitions data across multiple database instances for scalability.',
            'difficulty': 'hard',
            'tags': ['database', 'sharding', 'scalability']
        },
        {
            'question_text': 'What is a foreign key?',
            'options': ['A key from another country', 'A field that links to a primary key in another table', 'An encrypted key', 'A backup key'],
            'correct_answer': 'A field that links to a primary key in another table',
            'explanation': 'A foreign key establishes a relationship between two tables by referencing a primary key.',
            'difficulty': 'easy',
            'tags': ['database', 'keys', 'foreign key']
        }
    ],
    'Machine Learning': [
        {
            'question_text': 'What is supervised learning?',
            'options': ['Learning without data', 'Learning with labeled data', 'Learning with unlabeled data', 'Learning by reinforcement'],
            'correct_answer': 'Learning with labeled data',
            'explanation': 'Supervised learning uses labeled training data where the correct output is known.',
            'difficulty': 'easy',
            'tags': ['ml', 'supervised learning', 'basics']
        },
        {
            'question_text': 'What is overfitting in machine learning?',
            'options': ['Model performs well on all data', 'Model performs well on training but poorly on test data', 'Model is too simple', 'Model is too fast'],
            'correct_answer': 'Model performs well on training but poorly on test data',
            'explanation': 'Overfitting occurs when a model learns training data too well, including noise, and fails to generalize.',
            'difficulty': 'medium',
            'tags': ['ml', 'overfitting', 'model evaluation']
        },
        {
            'question_text': 'What is the purpose of a validation set?',
            'options': ['To train the model', 'To tune hyperparameters', 'To test final performance', 'To store data'],
            'correct_answer': 'To tune hyperparameters',
            'explanation': 'Validation sets help tune hyperparameters and prevent overfitting during model development.',
            'difficulty': 'medium',
            'tags': ['ml', 'validation', 'model evaluation']
        },
        {
            'question_text': 'What is gradient descent?',
            'options': ['A mountain climbing technique', 'An optimization algorithm to minimize loss', 'A type of neural network', 'A data preprocessing step'],
            'correct_answer': 'An optimization algorithm to minimize loss',
            'explanation': 'Gradient descent iteratively adjusts parameters to minimize the loss function.',
            'difficulty': 'medium',
            'tags': ['ml', 'optimization', 'gradient descent']
        },
        {
            'question_text': 'What is the difference between classification and regression?',
            'options': ['No difference', 'Classification predicts categories, regression predicts continuous values', 'Regression predicts categories', 'Classification is faster'],
            'correct_answer': 'Classification predicts categories, regression predicts continuous values',
            'explanation': 'Classification outputs discrete labels while regression outputs continuous numerical values.',
            'difficulty': 'easy',
            'tags': ['ml', 'classification', 'regression']
        },
        {
            'question_text': 'What is a neural network activation function?',
            'options': ['A function that activates the computer', 'A function that introduces non-linearity', 'A loss function', 'An optimization algorithm'],
            'correct_answer': 'A function that introduces non-linearity',
            'explanation': 'Activation functions add non-linearity to neural networks, enabling them to learn complex patterns.',
            'difficulty': 'medium',
            'tags': ['ml', 'neural networks', 'activation']
        },
        {
            'question_text': 'What is cross-validation?',
            'options': ['Validating across countries', 'A technique to assess model performance using data splits', 'A type of neural network', 'An optimization method'],
            'correct_answer': 'A technique to assess model performance using data splits',
            'explanation': 'Cross-validation splits data into multiple folds to evaluate model performance more reliably.',
            'difficulty': 'medium',
            'tags': ['ml', 'validation', 'cross-validation']
        },
        {
            'question_text': 'What is feature scaling?',
            'options': ['Removing features', 'Normalizing feature values to a similar range', 'Adding new features', 'Selecting important features'],
            'correct_answer': 'Normalizing feature values to a similar range',
            'explanation': 'Feature scaling ensures all features contribute equally by bringing them to a similar scale.',
            'difficulty': 'easy',
            'tags': ['ml', 'preprocessing', 'feature scaling']
        },
        {
            'question_text': 'What is ensemble learning?',
            'options': ['Learning music', 'Combining multiple models for better predictions', 'A single powerful model', 'A type of neural network'],
            'correct_answer': 'Combining multiple models for better predictions',
            'explanation': 'Ensemble methods combine predictions from multiple models to improve accuracy and robustness.',
            'difficulty': 'medium',
            'tags': ['ml', 'ensemble', 'model combination']
        },
        {
            'question_text': 'What does CNN stand for in deep learning?',
            'options': ['Computer Neural Network', 'Convolutional Neural Network', 'Connected Node Network', 'Central Neural Network'],
            'correct_answer': 'Convolutional Neural Network',
            'explanation': 'CNNs are specialized neural networks designed primarily for processing grid-like data such as images.',
            'difficulty': 'easy',
            'tags': ['ml', 'deep learning', 'cnn']
        }
    ],
    'System Design': [
        {
            'question_text': 'What is horizontal scaling?',
            'options': ['Adding more power to a single server', 'Adding more servers to handle load', 'Scaling sideways', 'Reducing server count'],
            'correct_answer': 'Adding more servers to handle load',
            'explanation': 'Horizontal scaling (scaling out) adds more machines to distribute the workload.',
            'difficulty': 'easy',
            'tags': ['system design', 'scaling', 'horizontal']
        },
        {
            'question_text': 'What is a load balancer?',
            'options': ['A device that balances weight', 'A system that distributes traffic across servers', 'A database', 'A caching system'],
            'correct_answer': 'A system that distributes traffic across servers',
            'explanation': 'Load balancers distribute incoming traffic across multiple servers to ensure no single server is overwhelmed.',
            'difficulty': 'easy',
            'tags': ['system design', 'load balancer', 'infrastructure']
        },
        {
            'question_text': 'What is caching?',
            'options': ['Storing money', 'Storing frequently accessed data for faster retrieval', 'Deleting old data', 'Encrypting data'],
            'correct_answer': 'Storing frequently accessed data for faster retrieval',
            'explanation': 'Caching stores copies of frequently accessed data in fast storage to reduce latency.',
            'difficulty': 'easy',
            'tags': ['system design', 'caching', 'performance']
        },
        {
            'question_text': 'What is the CAP theorem?',
            'options': ['A hat theorem', 'Consistency, Availability, Partition tolerance trade-off', 'A caching method', 'A database type'],
            'correct_answer': 'Consistency, Availability, Partition tolerance trade-off',
            'explanation': 'CAP theorem states distributed systems can only guarantee two of three: Consistency, Availability, Partition tolerance.',
            'difficulty': 'hard',
            'tags': ['system design', 'cap theorem', 'distributed systems']
        },
        {
            'question_text': 'What is microservices architecture?',
            'options': ['Very small services', 'Breaking an application into small, independent services', 'A monolithic approach', 'A database design'],
            'correct_answer': 'Breaking an application into small, independent services',
            'explanation': 'Microservices architecture decomposes applications into loosely coupled, independently deployable services.',
            'difficulty': 'medium',
            'tags': ['system design', 'microservices', 'architecture']
        },
        {
            'question_text': 'What is a message queue?',
            'options': ['A queue of messages', 'A system for asynchronous communication between services', 'A type of database', 'A load balancer'],
            'correct_answer': 'A system for asynchronous communication between services',
            'explanation': 'Message queues enable asynchronous communication and decouple components in distributed systems.',
            'difficulty': 'medium',
            'tags': ['system design', 'message queue', 'async']
        },
        {
            'question_text': 'What is database replication?',
            'options': ['Copying database design', 'Maintaining copies of data across multiple servers', 'Deleting duplicate data', 'Compressing data'],
            'correct_answer': 'Maintaining copies of data across multiple servers',
            'explanation': 'Replication copies data across multiple database servers for redundancy and read scaling.',
            'difficulty': 'medium',
            'tags': ['system design', 'replication', 'database']
        },
        {
            'question_text': 'What is an API Gateway?',
            'options': ['A physical gateway', 'A single entry point for all client requests to backend services', 'A database', 'A frontend framework'],
            'correct_answer': 'A single entry point for all client requests to backend services',
            'explanation': 'API Gateway acts as a reverse proxy, routing requests and providing cross-cutting concerns.',
            'difficulty': 'medium',
            'tags': ['system design', 'api gateway', 'architecture']
        },
        {
            'question_text': 'What is eventual consistency?',
            'options': ['Data is always consistent', 'Data will become consistent over time', 'Data is never consistent', 'A type of database'],
            'correct_answer': 'Data will become consistent over time',
            'explanation': 'Eventual consistency guarantees that all replicas will converge to the same value given enough time.',
            'difficulty': 'hard',
            'tags': ['system design', 'consistency', 'distributed systems']
        },
        {
            'question_text': 'What is a CDN?',
            'options': ['Content Delivery Network', 'Central Data Node', 'Computer Distribution Network', 'Cloud Database Network'],
            'correct_answer': 'Content Delivery Network',
            'explanation': 'CDN is a network of geographically distributed servers that deliver content to users from nearby locations.',
            'difficulty': 'easy',
            'tags': ['system design', 'cdn', 'performance']
        }
    ],
    'DevOps': [
        {
            'question_text': 'What is Docker?',
            'options': ['A programming language', 'A containerization platform', 'A database', 'A web framework'],
            'correct_answer': 'A containerization platform',
            'explanation': 'Docker packages applications and dependencies into containers for consistent deployment.',
            'difficulty': 'easy',
            'tags': ['devops', 'docker', 'containers']
        },
        {
            'question_text': 'What is Kubernetes?',
            'options': ['A programming language', 'A container orchestration platform', 'A database', 'A monitoring tool'],
            'correct_answer': 'A container orchestration platform',
            'explanation': 'Kubernetes automates deployment, scaling, and management of containerized applications.',
            'difficulty': 'medium',
            'tags': ['devops', 'kubernetes', 'orchestration']
        },
        {
            'question_text': 'What is CI/CD?',
            'options': ['A programming language', 'Continuous Integration/Continuous Deployment', 'A database system', 'A monitoring tool'],
            'correct_answer': 'Continuous Integration/Continuous Deployment',
            'explanation': 'CI/CD automates building, testing, and deploying code changes to production.',
            'difficulty': 'easy',
            'tags': ['devops', 'ci/cd', 'automation']
        },
        {
            'question_text': 'What is Infrastructure as Code (IaC)?',
            'options': ['Writing code about infrastructure', 'Managing infrastructure through code and automation', 'A programming language', 'A type of database'],
            'correct_answer': 'Managing infrastructure through code and automation',
            'explanation': 'IaC manages and provisions infrastructure using code and version control.',
            'difficulty': 'medium',
            'tags': ['devops', 'iac', 'automation']
        },
        {
            'question_text': 'What is the purpose of monitoring in DevOps?',
            'options': ['To watch employees', 'To track system health and performance', 'To write code', 'To deploy applications'],
            'correct_answer': 'To track system health and performance',
            'explanation': 'Monitoring provides visibility into system behavior, helping identify and resolve issues quickly.',
            'difficulty': 'easy',
            'tags': ['devops', 'monitoring', 'observability']
        },
        {
            'question_text': 'What is Terraform?',
            'options': ['A planet', 'An Infrastructure as Code tool', 'A programming language', 'A container platform'],
            'correct_answer': 'An Infrastructure as Code tool',
            'explanation': 'Terraform is an IaC tool for building, changing, and versioning infrastructure safely.',
            'difficulty': 'medium',
            'tags': ['devops', 'terraform', 'iac']
        },
        {
            'question_text': 'What is a container?',
            'options': ['A storage box', 'A lightweight, standalone executable package', 'A virtual machine', 'A database'],
            'correct_answer': 'A lightweight, standalone executable package',
            'explanation': 'Containers package code and dependencies together, ensuring consistent behavior across environments.',
            'difficulty': 'easy',
            'tags': ['devops', 'containers', 'docker']
        },
        {
            'question_text': 'What is Git?',
            'options': ['A programming language', 'A distributed version control system', 'A database', 'A web server'],
            'correct_answer': 'A distributed version control system',
            'explanation': 'Git tracks changes in source code and enables collaboration among developers.',
            'difficulty': 'easy',
            'tags': ['devops', 'git', 'version control']
        },
        {
            'question_text': 'What is a pod in Kubernetes?',
            'options': ['A group of whales', 'The smallest deployable unit containing one or more containers', 'A type of node', 'A service'],
            'correct_answer': 'The smallest deployable unit containing one or more containers',
            'explanation': 'A pod is the basic execution unit in Kubernetes, containing one or more tightly coupled containers.',
            'difficulty': 'medium',
            'tags': ['devops', 'kubernetes', 'pods']
        },
        {
            'question_text': 'What is the difference between a container and a virtual machine?',
            'options': ['No difference', 'Containers share the host OS kernel, VMs have their own OS', 'VMs are lighter', 'Containers are slower'],
            'correct_answer': 'Containers share the host OS kernel, VMs have their own OS',
            'explanation': 'Containers are more lightweight as they share the host OS, while VMs include a full guest OS.',
            'difficulty': 'medium',
            'tags': ['devops', 'containers', 'virtualization']
        }
    ]
}

def seed_questions():
    """Seed the database with questions"""
    with app.app_context():
        # Clear existing questions
        mongo.db.questions.delete_many({})
        
        questions_to_insert = []
        
        for category, questions in QUESTIONS.items():
            for q in questions:
                question_doc = {
                    'question_text': q['question_text'],
                    'question_type': 'mcq',
                    'options': q['options'],
                    'correct_answer': q['correct_answer'],
                    'explanation': q['explanation'],
                    'difficulty': q['difficulty'],
                    'category': category,
                    'tags': q['tags'],
                    'points': 10 if q['difficulty'] == 'easy' else 15 if q['difficulty'] == 'medium' else 20,
                    'created_at': datetime.utcnow()
                }
                questions_to_insert.append(question_doc)
        
        # Insert all questions
        result = mongo.db.questions.insert_many(questions_to_insert)
        print(f"Successfully inserted {len(result.inserted_ids)} questions into the database.")
        
        # Print category breakdown
        print("\nQuestions by category:")
        for category in QUESTIONS.keys():
            count = mongo.db.questions.count_documents({'category': category})
            print(f"  {category}: {count} questions")

if __name__ == '__main__':
    seed_questions()
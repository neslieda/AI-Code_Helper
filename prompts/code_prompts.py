"""
Prompt templates for code-related tasks.
"""
from langchain_core.prompts import PromptTemplate

# Prompt for code generation
CODE_GENERATION_PROMPT = PromptTemplate(
    input_variables=["language", "task_description", "additional_context"],
    template="""You are an expert software developer. Write code to solve the following task.

Language: {language}
Task: {task_description}
Additional Context: {additional_context}

Provide well-documented, efficient, and readable code that follows best practices for the specified language.
Include comments to explain your approach and any important considerations.
"""
)

# Prompt for code explanation
CODE_EXPLANATION_PROMPT = PromptTemplate(
    input_variables=["code", "language"],
    template="""Explain the following code in detail:

```{language}
{code}
```

Your explanation should include:
1. A high-level overview of what the code does
2. Explanation of key functions and their purposes
3. Any notable design patterns or algorithms used
4. Potential improvements or issues with the code
"""
)

# Prompt for code review
CODE_REVIEW_PROMPT = PromptTemplate(
    input_variables=["code", "language"],
    template="""Review the following code and provide constructive feedback:

```{language}
{code}
```

Your review should include:
1. Code quality assessment
2. Potential bugs or edge cases
3. Performance considerations
4. Adherence to best practices
5. Suggestions for improvement

Be specific and provide examples where possible.
"""
)

# Prompt for code refactoring
CODE_REFACTORING_PROMPT = PromptTemplate(
    input_variables=["code", "language", "refactoring_goals"],
    template="""Refactor the following code according to the specified goals:

```{language}
{code}
```

Refactoring Goals: {refactoring_goals}

Provide the refactored code along with an explanation of the changes you made and how they address the refactoring goals.
Focus on improving code quality while maintaining functionality.
"""
)

# Prompt for bug fixing
BUG_FIXING_PROMPT = PromptTemplate(
    input_variables=["code", "language", "bug_description", "expected_behavior"],
    template="""Fix the bug in the following code:

```{language}
{code}
```

Bug Description: {bug_description}
Expected Behavior: {expected_behavior}

Provide the corrected code and explain the cause of the bug and how your solution fixes it.
"""
)

# Prompt for code completion
CODE_COMPLETION_PROMPT = PromptTemplate(
    input_variables=["code_snippet", "language", "completion_instruction"],
    template="""Complete the following code according to the instructions:

```{language}
{code_snippet}
```

Instructions: {completion_instruction}

Provide the completed code that satisfies the instructions. Ensure the code is consistent with the existing code style and functionality.
"""
)

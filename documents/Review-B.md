# Scientific Documentation of Today's Work + Next-Steps Roadmap

`Creation Date: (8/30/23)`

## Today's Work:

### Initial State

The project started with a `main.py` script responsible for sending images to a Discord webhook.
The initial code had several limitations:

1. Lack of modularization: Functions like `send_image` were doing multiple things, making it hard to maintain and update.
2. Minimal error handling: Only basic exceptions were being caught, and no custom exceptions were being used for image validation.
3. Hardcoded configurations: Parameters like rate limits and image types were hardcoded.
4. Limited retry mechanism: A basic retry mechanism was in place, but it wasn't robust.

### User Requirements

1. Refactor the code to be more modular and maintainable.
2. Introduce custom exceptions for image validation.
3. Make the script configurable via environment variables.
4. Implement a more robust retry mechanism.

## Steps Taken

### Step 1: Code Analysis

- Reviewed the original `main.py` and `.env.template` to understand their functionalities and limitations.
- Analyzed the `Review-A.md` document to identify areas for improvement.

### Step 2: Pseudocode

- Created a pseudocode to outline the new structure and functionalities.

### Step 3: Code Refactoring

- Broke down the `send_image` function into smaller functions for better readability and maintainability.
- Introduced custom exceptions for image validation.

### Step 4: Configuration and Environment Variables

- Modified the script to read configurations from an `.env` file.
- Created an updated `.env.template` to guide users in setting up their environment variables.

### Step 5: Implementing Retry Mechanism

- Implemented a more sophisticated retry mechanism using Python's `Queue` for failed images.

### Step 6: Logging and Metrics

- Added logging functionalities to keep track of the images that were sent, skipped, or failed.
- Implemented a metrics collection mechanism.

### Step 7: Final Adjustments and User Feedback

- Made final adjustments based on user feedback, such as correctly handling the image paths.
- Removed placeholder functions and filled them with actual logic.

## Final State

The final code is a modular, configurable, and robust Python script for sending images to a Discord webhook.
It has improved error handling, a sophisticated retry mechanism, and enhanced logging and metrics collection functionalities.

### Context of Decisions

1. Moved to OOP (Object-Oriented Programming) for better modularity and future scalability.
2. Utilized environment variables to make the script more configurable and secure.
3. Implemented Python's built-in `Queue` for the retry mechanism for simplicity and efficiency.
4. Used Python's logging module for better monitoring.

### Files Produced

1. `__init__.py`: The main Python script containing all functionalities.
2. `.env.template.updated`: An updated template for the environment variables.

### Challenges and Solutions

1. Complexity in Modularization: Breaking down the `send_image` function into smaller parts while maintaining its original functionality was challenging. It was solved through careful planning and testing.
2. Rate Limiting: Initially overlooked, it was later implemented based on the specific time to wait given by the server response.

### Future Work

1. Implementing more advanced features like dynamic threading based on the workload.
2. Utilizing third-party services for logging and metrics.
3. Adding more functionalities like image transformation before sending.

### Lessons Learned

1. The importance of modular code for maintainability.
2. The utility of environment variables for configuration and security.
3. The need for robust error handling and retry mechanisms in real-world applications.

---

# Development Roadmap for Discord-AIU Project

## Current State

- Basic image sending functionality.
- Some level of error handling and metrics collection.
- Rate-limiting and retry mechanisms are in place.
- Environment variables are used for some configurations.

## Short-term Goals

### Error Handling Improvements

- Implement a robust error-handling mechanism that covers a wider range of exceptions.
- Integrate a logging system.

### Configuration

- Move more hardcoded values to environment variables.

### Documentation

- Add more detailed docstrings and inline comments.

## Mid-term Goals

### Metrics

- Improve the MetricsCollector class to export metrics to a monitoring system.
- Log metrics in a structured format for analysis.

### Type Annotations and Docstrings

- Add type annotations to all functions and methods.
- Document the expected parameters and returns for each function/method.

### Test Coverage

- Write unit tests to cover all logical branches in the code.

## Long-term Goals

### Refactor for Extensibility

- Refactor the code to make it more modular and easier to extend.
- Make image file extensions configurable.

### Asynchronous Programming

- Investigate and potentially implement asyncio to improve performance.

### CI/CD Integration

- Implement a CI/CD pipeline for automated testing and deployment.

## Optional Goals

### User Interface

- Develop a user-friendly interface for non-technical users.

### Cloud Deployment

- Prepare the application for cloud deployment, including containerization.

---

This roadmap will help guide the development of the Discord-AIU project, making it easier to prioritize tasks and track progress.

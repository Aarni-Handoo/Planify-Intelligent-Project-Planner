import csv
import os
import random


TASKS = [
    {
        "title": "Create Login Page",
        "description": "Design and implement user login interface",
        "role": "frontend",
        "skills": "React,CSS,JavaScript",
        "priority": "High",
        "complexity": 2
    },
    {
        "title": "Build Registration Page",
        "description": "Create user registration form and validation",
        "role": "frontend",
        "skills": "React,CSS,JavaScript",
        "priority": "Medium",
        "complexity": 2
    },
    {
        "title": "Build REST API",
        "description": "Create backend API for application",
        "role": "backend",
        "skills": "Python,Flask,API",
        "priority": "High",
        "complexity": 4
    },
    {
        "title": "Create Authentication API",
        "description": "Implement login authentication and authorization",
        "role": "backend",
        "skills": "Python,Flask,JWT",
        "priority": "High",
        "complexity": 4
    },
    {
        "title": "Design Database",
        "description": "Create database schema and relationships",
        "role": "database",
        "skills": "SQL,Database",
        "priority": "High",
        "complexity": 3
    },
    {
        "title": "Create Database Tables",
        "description": "Implement tables and constraints",
        "role": "database",
        "skills": "SQL,MySQL",
        "priority": "Medium",
        "complexity": 3
    },
    {
        "title": "Build Dashboard",
        "description": "Create project management dashboard",
        "role": "frontend",
        "skills": "React,CSS,JavaScript",
        "priority": "High",
        "complexity": 4
    },
    {
        "title": "Implement Task Management",
        "description": "Add create edit delete and complete task functionality",
        "role": "frontend",
        "skills": "React,JavaScript",
        "priority": "High",
        "complexity": 4
    },
    {
        "title": "Implement Scheduling",
        "description": "Create automatic task scheduling logic",
        "role": "backend",
        "skills": "Python,Algorithms",
        "priority": "High",
        "complexity": 5
    },
    {
        "title": "Create ML Dataset",
        "description": "Prepare dataset for task prediction",
        "role": "backend",
        "skills": "Python,Machine Learning",
        "priority": "Medium",
        "complexity": 4
    },
    {
        "title": "Train Task Prediction Model",
        "description": "Train machine learning model for task analysis",
        "role": "backend",
        "skills": "Python,Machine Learning",
        "priority": "High",
        "complexity": 5
    },
    {
        "title": "Design Application UI",
        "description": "Create UI design and wireframes",
        "role": "design",
        "skills": "Figma,UI,UX",
        "priority": "Medium",
        "complexity": 3
    },
    {
        "title": "Create Project Logo",
        "description": "Design logo and branding elements",
        "role": "design",
        "skills": "Figma,Canva",
        "priority": "Low",
        "complexity": 1
    },
    {
        "title": "Configure Docker",
        "description": "Containerize the application",
        "role": "devops",
        "skills": "Docker,DevOps",
        "priority": "Medium",
        "complexity": 4
    },
    {
        "title": "Deploy Application",
        "description": "Deploy application to cloud server",
        "role": "devops",
        "skills": "AWS,Docker,DevOps",
        "priority": "High",
        "complexity": 5
    }
]


def generate_dataset(number_of_rows=500):
    output_dir = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "raw"
    )

    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(
        output_dir,
        "tasks.csv"
    )

    rows = []

    for i in range(number_of_rows):

        task = random.choice(TASKS)

        duration = random.randint(
            max(1, task["complexity"] - 1),
            task["complexity"] + 3
        )

        rows.append({
            "task_id": i + 1,
            "title": task["title"],
            "description": task["description"],
            "role": task["role"],
            "skills": task["skills"],
            "priority": task["priority"],
            "complexity": task["complexity"],
            "duration_days": duration
        })

    with open(output_file, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "task_id",
                "title",
                "description",
                "role",
                "skills",
                "priority",
                "complexity",
                "duration_days"
            ]
        )

        writer.writeheader()
        writer.writerows(rows)

    print("Dataset generated successfully.")
    print("File:", output_file)
    print("Rows:", number_of_rows)


if __name__ == "__main__":
    generate_dataset(500)